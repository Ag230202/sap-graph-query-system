import os
import re
import pandas as pd
import google.generativeai as genai
from typing import Dict, Any

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a data query assistant for an SAP Order-to-Cash system. 

Your role is to help users query business data about:
- Sales Orders (salesOrder, soldToParty, totalNetAmount, etc.)
- Deliveries (deliveryDocument, shippingPoint, etc.)
- Billing Documents/Invoices (billingDocument, billingDocumentType, etc.)
- Payments and Journal Entries
- Customers (Business Partners)
- Products and Materials
- Plants and Storage Locations

**STRICT GUARDRAILS:**
1. ONLY answer questions related to the O2C dataset
2. REJECT questions about: general knowledge, creative writing, code generation, unrelated topics
3. If unsure, politely state you can only help with O2C data queries

When user asks a question:
1. Determine if it's related to the dataset (if not, reject politely)
2. Generate a SQL query using pandas syntax to answer the question
3. The query must use the available dataframes: sales_order_headers, sales_order_items, outbound_delivery_headers, outbound_delivery_items, billing_document_headers, billing_document_items, business_partners, products, plants, journal_entry_items_accounts_receivable, payments_accounts_receivable

Response format:
```sql
<your pandas-compatible SQL query here>
```

Example:
User: "Which products have the most billing documents?"
Response:
```sql
SELECT material, COUNT(DISTINCT billingDocument) as bill_count
FROM billing_document_items
GROUP BY material
ORDER BY bill_count DESC
LIMIT 10
```

Keep queries simple and efficient."""

def is_query_allowed(question: str) -> bool:
    """Check if the query is within allowed domain"""
    allowed_keywords = [
        'order', 'sales', 'delivery', 'billing', 'invoice', 'payment', 
        'customer', 'product', 'material', 'plant', 'journal', 
        'amount', 'quantity', 'status', 'document', 'flow', 'trace'
    ]
    
    question_lower = question.lower()
    
    # Check if any allowed keyword is present
    if any(keyword in question_lower for keyword in allowed_keywords):
        return True
    
    # Reject if it looks like off-topic
    reject_patterns = [
        r'write.*story', r'create.*poem', r'generate.*code',
        r'what is.*capital', r'who is', r'when did',
        r'calculate.*\d+\s*[\+\-\*/]', r'solve.*equation'
    ]
    
    for pattern in reject_patterns:
        if re.search(pattern, question_lower):
            return False
    
    return False

def extract_sql_from_response(response_text: str) -> str:
    """Extract SQL query from LLM response"""
    # Look for code blocks
    sql_match = re.search(r'```sql\n(.*?)\n```', response_text, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    
    # Look for any code block
    code_match = re.search(r'```\n(.*?)\n```', response_text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    
    return response_text.strip()

def generate_sql_query(question: str, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Use LLM to generate SQL query from natural language"""
    
    # Check guardrails
    if not is_query_allowed(question):
        return {
            "success": False,
            "error": "I can only answer questions about the SAP Order-to-Cash dataset. Please ask about sales orders, deliveries, billing documents, payments, customers, or products.",
            "answer": None
        }
    
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "GEMINI_API_KEY not configured. Please set it in .env file.",
            "answer": None
        }
    
    try:
        # Get schema info
        schema_info = "\n\nAvailable tables and columns:\n"
        for table_name, df in datasets.items():
            if len(df) > 0:
                cols = ", ".join(df.columns[:10])  # First 10 columns
                schema_info += f"\n{table_name}: {cols}..."
        
        prompt = f"{SYSTEM_PROMPT}\n{schema_info}\n\nUser question: {question}"
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        sql_query = extract_sql_from_response(response.text)
        
        return {
            "success": True,
            "sql_query": sql_query,
            "raw_response": response.text
        }
    
    except Exception as e:
        error_msg = str(e)

        # 🎯 Handle quota / rate limit errors
        if "quota" in error_msg.lower() or "429" in error_msg:
            return {
                "success": False,
                "error": "⚠️ I'm currently experiencing high usage and can't process your request right now.\n\n"
                        "Please try again in a few seconds.\n\n"
                        "💡 Tip: Try a simpler query or wait a moment before retrying."
            }

        # 🎯 Generic fallback
        return {
            "success": False,
            "error": "⚠️ Something went wrong while processing your request.\n\n"
                    "Please try again or rephrase your question."
        }

def execute_query(sql_query: str, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Execute SQL query on pandas DataFrames"""
    try:
        # Import pandasql for SQL execution
        from pandasql import sqldf
        
        # Create a function that executes SQL with local dataframes
        pysqldf = lambda q: sqldf(q, datasets)
        
        # Execute the query
        result = pysqldf(sql_query)
        
        return {
            "success": True,
            "result": result.to_dict('records') if not result.empty else [],
            "row_count": len(result)
        }
    
    except Exception as e:
        # Fallback: try to execute simple queries manually
        try:
            result = execute_simple_query(sql_query, datasets)
            return {
                "success": True,
                "result": result,
                "row_count": len(result)
            }
        except Exception as e2:
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}. Fallback also failed: {str(e2)}",
                "result": None
            }

def execute_simple_query(sql_query: str, datasets: Dict[str, pd.DataFrame]):
    """Simple query executor for common patterns"""
    sql_lower = sql_query.lower()
    
    # Pattern: SELECT ... FROM table_name
    table_match = re.search(r'from\s+(\w+)', sql_lower)
    if not table_match:
        raise Exception("Could not parse table name")
    
    table_name = table_match.group(1)
    if table_name not in datasets:
        raise Exception(f"Table {table_name} not found")
    
    df = datasets[table_name]
    
    # Simple aggregation: COUNT, GROUP BY
    if 'group by' in sql_lower and 'count' in sql_lower:
        group_col_match = re.search(r'group by\s+(\w+)', sql_lower)
        if group_col_match:
            group_col = group_col_match.group(1)
            result = df.groupby(group_col).size().reset_index(name='count')
            result = result.sort_values('count', ascending=False).head(10)
            return result.to_dict('records')
    
    # Simple SELECT with LIMIT
    limit_match = re.search(r'limit\s+(\d+)', sql_lower)
    limit = int(limit_match.group(1)) if limit_match else 10
    
    return df.head(limit).to_dict('records')


def generate_natural_language_response(question: str, query_result: Dict[str, Any]) -> str:
    """Generate polished, user-friendly business responses"""

    if not query_result['success']:
        return query_result.get('error', 'Query failed')

    data = query_result['result']
    row_count = query_result['row_count']

    if not data or row_count == 0:
        return "⚠️ I couldn’t find any matching results. Try refining your query."

    # =========================
    # 🚨 CASE 0: Broken Flow
    # =========================
    if "broken" in question.lower() or "incomplete" in question.lower():
        total = row_count

        response = f"🚨 **O2C Flow Alert**\n\n"
        response += f"I found **{total} sales orders** that are not completing the full Order-to-Cash cycle.\n\n"

        response += "📊 **What this means:**\n"
        response += "• Orders are getting stuck in the process\n"
        response += "• Revenue realization may be delayed\n"
        response += "• Possible gaps between Delivery → Billing or Billing → Payment\n\n"

        response += "🔍 **Sample affected orders:**\n\n"

        for i, row in enumerate(data[:5], 1):
            so = row.get("salesOrder") or row.get("sales_document") or "N/A"
            customer = row.get("soldToParty", "")
            amount = row.get("totalNetAmount", "")

            response += f"**{i}. Order {so}**\n"
            if customer:
                response += f"   • Customer: {customer}\n"
            if amount:
                response += f"   • Amount: {amount}\n"
            response += "\n"

        if total > 5:
            response += f"...and **{total - 5} more orders** impacted.\n\n"

        response += "💡 **Recommendation:**\n"
        response += "Focus on improving the transition from **Delivery → Billing** to reduce delays.\n"

        return response

    # =========================
    # 🎯 CASE 1: Single Result
    # =========================
    if row_count == 1:
        row = data[0]

        response = "✅ **Here’s what I found:**\n\n"

        for key, value in row.items():
            response += f"• **{key}**: {value}\n"

        response += "\nLet me know if you'd like deeper analysis."

        return response

    # =========================
    # 📊 CASE 2: Aggregation
    # =========================
    if isinstance(data[0], dict) and len(data[0]) == 2:
        keys = list(data[0].keys())

        if "count" in keys[1].lower() or "bill" in keys[1].lower():
            main_key, value_key = keys[0], keys[1]

            response = "📊 **Key Insights from Your Data**\n\n"

            top = data[:3]

            response += "🏆 **Top Performers:**\n"
            for i, row in enumerate(top, 1):
                response += f"{i}. **{row[main_key]}** → {row[value_key]}\n"

            response += "\n📈 These entities are driving the highest activity in your system.\n\n"

            if len(data) > 3:
                response += "📌 **Other Notable Entries:**\n"
                for row in data[3:8]:
                    response += f"• {row[main_key]} ({row[value_key]})\n"

            response += "\n💡 You may want to analyze these further for performance optimization."

            return response

    # =========================
    # 📋 CASE 3: General Results
    # =========================
    response = f"📋 **I found {row_count} relevant records**\n\n"

    for i, row in enumerate(data[:5], 1):
        response += f"**{i}.**\n"
        for k, v in row.items():
            response += f"   • {k}: {v}\n"
        response += "\n"

    if row_count > 5:
        response += f"...and **{row_count - 5} more records**.\n\n"

    response += "💡 Let me know if you'd like deeper insights or visual tracing."

    return response