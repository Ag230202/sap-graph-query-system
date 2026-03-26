# SAP Order-to-Cash Graph Query System

A graph-based data modeling and natural language query system for SAP O2C (Order-to-Cash) business processes.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)

---

## 🎯 Overview

This system transforms fragmented SAP O2C data into an interconnected graph and provides a conversational interface to explore relationships between sales orders, deliveries, invoices, and payments using natural language.

### Key Features

- **Graph-Based Data Model**: Entities (orders, deliveries, invoices) as nodes with relationship edges
- **Interactive Visualization**: Explore the graph with React Flow - expand nodes, inspect metadata
- **Natural Language Queries**: Ask questions in plain English, get data-backed answers
- **LLM-Powered**: Uses Google Gemini to translate questions → SQL → results
- **Guardrails**: Restricts queries to the O2C dataset domain only
- **Minimal Dependencies**: Simple FastAPI backend + React frontend

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.11
- FastAPI (REST API)
- NetworkX (Graph construction)
- Pandas (Data operations)
- Google Gemini API (LLM for query translation)

**Frontend:**
- React 18
- React Flow (Graph visualization)
- Axios (HTTP client)

**Deployment:**
- Docker & Docker Compose

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │  Graph Visualization │    │   Chat Interface         │   │
│  │  (React Flow)        │    │   (Natural Language)     │   │
│  └─────────────────────┘    └──────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (REST API)
┌──────────────────────▼──────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Graph Builder  │  │ Query Handler│  │ LLM Integration │ │
│  │  (NetworkX)    │  │ (SQL Gen)    │  │  (Gemini API)   │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│           │                   │                   │          │
│           └───────────────────┴───────────────────┘          │
│                         │                                    │
│                 ┌───────▼────────┐                          │
│                 │  Data Loader   │                          │
│                 │  (Pandas)      │                          │
│                 └───────┬────────┘                          │
└─────────────────────────┼───────────────────────────────────┘
                          │
                  ┌───────▼────────┐
                  │  JSONL Files   │
                  │  (19 entities) │
                  └────────────────┘
```

### Data Model

The system models the complete O2C flow:

**Core Transactional Flow:**
```
Customer → Sales Order → Delivery → Billing Document → Journal Entry → Payment
```

**Entities & Relationships:**
- **Sales Orders**: Header + Items (linked to customers, products)
- **Deliveries**: Header + Items (linked to sales order items)
- **Billing Documents**: Header + Items (linked to delivery items)
- **Journal Entries**: Accounting records (linked to billing documents)
- **Payments**: Payment records (linked to accounting documents)
- **Master Data**: Customers, Products, Plants

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Google Gemini API key (free tier: https://ai.google.dev)
- The SAP O2C dataset (provided)

### 1. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd sap-graph-query-system

# Create environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_actual_key_here
```

### 2. Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 3. Alternative: Run Locally (Without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## 📊 Dataset

The system uses 19 JSONL files representing SAP S/4HANA O2C entities:

### Transactional Data
- `sales_order_headers` - Sales order metadata
- `sales_order_items` - Line items with products
- `sales_order_schedule_lines` - Delivery schedules
- `outbound_delivery_headers` - Delivery documents
- `outbound_delivery_items` - Delivery line items
- `billing_document_headers` - Invoices
- `billing_document_items` - Invoice line items
- `billing_document_cancellations` - Cancelled invoices
- `journal_entry_items_accounts_receivable` - Financial postings
- `payments_accounts_receivable` - Payment records

### Master Data
- `business_partners` - Customer master data
- `business_partner_addresses` - Customer addresses
- `customer_sales_area_assignments` - Sales org assignments
- `customer_company_assignments` - Company code assignments
- `products` - Product master data
- `product_descriptions` - Product descriptions
- `product_plants` - Product-plant relationships
- `product_storage_locations` - Storage location data
- `plants` - Plant/facility master data

---

## 💬 Example Queries

The system can answer questions like:

1. **Product Analysis**
   - "Which products are associated with the highest number of billing documents?"
   - "What are the top 10 products by sales amount?"

2. **Flow Tracing**
   - "Trace the full flow of billing document 90504259"
   - "Show me the complete O2C cycle for sales order 740506"

3. **Broken Flow Detection**
   - "Identify sales orders that have been delivered but not billed"
   - "Find deliveries without corresponding billing documents"
   - "Show me sales orders with incomplete flows"

4. **Business Metrics**
   - "What is the total sales amount for this month?"
   - "How many sales orders are pending delivery?"
   - "Which customers have the most outstanding invoices?"

---

## 🛡️ Guardrails & Safety

The system implements strict domain restrictions:

### Allowed Queries
✅ Questions about O2C data (orders, deliveries, invoices, payments)
✅ Business metrics and analytics
✅ Flow tracing and relationship queries
✅ Data aggregations and summaries

### Rejected Queries
❌ General knowledge questions ("What is the capital of France?")
❌ Creative writing ("Write me a story about...")
❌ Code generation requests
❌ Unrelated topics

**Implementation:**
- Keyword-based filtering in `query_handler.py`
- Pattern matching for off-topic requests
- LLM system prompt enforces domain boundaries

---

## 🧠 LLM Integration Strategy

### Query Processing Pipeline

1. **User Input**: Natural language question
2. **Guardrail Check**: Validate query is O2C-related
3. **SQL Generation**: LLM translates question → SQL query
4. **Query Execution**: Execute on Pandas DataFrames
5. **Response Generation**: Format results as natural language

### Prompt Engineering

The system uses a carefully crafted system prompt that:
- Defines available tables and columns
- Provides SQL query examples
- Enforces output format (SQL in code blocks)
- Restricts domain to O2C dataset

**See `query_handler.py` → `SYSTEM_PROMPT` for full prompt.**

### LLM Provider Choice: Google Gemini

**Why Gemini?**
- ✅ Free tier with generous limits (60 requests/minute)
- ✅ Good SQL generation capabilities
- ✅ Fast response times
- ✅ Simple API integration

**Alternatives:**
- Groq (faster, smaller context)
- OpenRouter (multiple models)
- Cohere (good for structured output)

To switch LLM providers, modify `query_handler.py`.

---

## 📈 Graph Construction Logic

### Node Types
- `SalesOrder` - Sales order header
- `SalesOrderItem` - Line item
- `Delivery` - Delivery document header
- `DeliveryItem` - Delivery line item
- `BillingDocument` - Invoice header
- `BillingDocumentItem` - Invoice line item
- `JournalEntry` - Accounting record
- `Payment` - Payment record
- `Customer` - Business partner
- `Product` - Material/product
- `Plant` - Facility/location

### Relationship Types
- `HAS_ITEM` - Header → Item relationship
- `PLACED` - Customer → Sales Order
- `FOR_PRODUCT` - Item → Product
- `DELIVERED_BY` - Sales Order Item → Delivery Item
- `BILLED_BY` - Delivery Item → Billing Item
- `POSTED_AS` - Billing Document → Journal Entry

### Graph Building Process

```python
# Simplified pseudocode
def build_graph():
    # 1. Add all entity nodes
    for sales_order in sales_orders:
        graph.add_node(sales_order_id, type="SalesOrder", data=...)
    
    # 2. Add relationships
    for item in sales_order_items:
        graph.add_edge(order_id, item_id, relationship="HAS_ITEM")
    
    # 3. Link across documents
    for delivery_item in delivery_items:
        if delivery_item.ref_sales_order:
            graph.add_edge(
                sales_order_item_id, 
                delivery_item_id, 
                relationship="DELIVERED_BY"
            )
```

**See `graph_builder.py` for complete implementation.**

---

## 🎨 Frontend Features

### Graph Visualization
- **Interactive Graph**: Zoom, pan, drag nodes
- **Node Colors**: Color-coded by entity type
- **Minimap**: Navigate large graphs easily
- **Node Details**: Click to inspect metadata
- **Edge Labels**: Show relationship types

### Chat Interface
- **Natural Language Input**: Type questions naturally
- **Query History**: See conversation flow
- **SQL Display**: View generated SQL queries
- **Example Queries**: Quick-start templates
- **Error Handling**: Clear error messages

---

## 🔧 Configuration

### Backend Configuration

**File: `backend/.env`**
```bash
GEMINI_API_KEY=your_key_here
```

### Frontend Configuration

**File: `frontend/src/App.js`**
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

For production, use environment variables:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

---

## 📦 Deployment

### Local Development
```bash
docker-compose up
```

### Production Deployment

**Option 1: Cloud VM (AWS EC2, GCP Compute)**
```bash
# SSH into server
git clone <repo>
cd sap-graph-query-system
cp .env.example .env
# Edit .env with production API key
docker-compose up -d
```

**Option 2: Cloud Platform (Heroku, Railway, Render)**
- Set environment variables in platform dashboard
- Deploy backend and frontend as separate services
- Update CORS settings in `backend/main.py`

**Option 3: Kubernetes**
- Create ConfigMap for environment variables
- Deploy backend and frontend as separate deployments
- Use LoadBalancer or Ingress for external access

---

## 🧪 Testing Example Queries

Once running, try these queries in the chat interface:

```
1. "Which products have the most billing documents?"
   → Tests product aggregation

2. "Show me sales order 740506"
   → Tests specific document lookup

3. "What is the total sales amount?"
   → Tests financial aggregation

4. "Find sales orders that are delivered but not billed"
   → Tests broken flow detection

5. "Trace the flow of billing document 90504259"
   → Tests relationship traversal
```

---

## 📁 Project Structure

```
sap-graph-query-system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── data_loader.py          # JSONL file reader
│   ├── graph_builder.py        # Graph construction logic
│   ├── query_handler.py        # LLM query processing
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── App.css             # Styling
│   │   ├── index.js            # React entry point
│   │   └── index.css
│   ├── package.json
│   └── Dockerfile
├── data/                       # JSONL files (19 entities)
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify GEMINI_API_KEY is set in `.env`
- Check data files are in `./data/` directory

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in `frontend/src/App.js`

### Graph not loading
- Check browser console for errors
- Verify data files are not empty
- Check backend logs: `docker-compose logs backend`

### LLM queries failing
- Verify API key is valid and has quota
- Check network connectivity
- Try a simpler query first

---

## 🔮 Future Enhancements

**Implemented:**
- ✅ Graph construction with NetworkX
- ✅ React Flow visualization
- ✅ Natural language queries with Gemini
- ✅ Guardrails for domain restriction
- ✅ Docker deployment

**Potential Extensions:**
- [ ] Query result node highlighting in graph
- [ ] Advanced graph analytics (PageRank, centrality)
- [ ] Conversation memory (multi-turn context)
- [ ] Streaming LLM responses
- [ ] Export graph to Neo4j
- [ ] Real-time data updates
- [ ] User authentication
- [ ] Query performance optimization
- [ ] Advanced SQL generation (JOINs across tables)

---

## 📝 License

MIT License - feel free to use for learning and development.

---

## 🙏 Acknowledgments

- SAP S/4HANA data model reference
- Google Gemini API for LLM capabilities
- React Flow for graph visualization
- FastAPI framework

---

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainer.

---

**Built with ❤️ for SAP Forward Deployed Engineer Assessment**
