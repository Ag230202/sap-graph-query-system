from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import networkx as nx

from graph_builder import GraphBuilder
from query_handler import generate_sql_query, execute_query, generate_natural_language_response

# ✅ Initialize graph properly (ONLY ONCE)
graph_builder = GraphBuilder()
GRAPH = graph_builder.build_graph()
DATASETS = graph_builder.datasets

print("===== SYSTEM INITIALIZED =====")
for name, df in DATASETS.items():
    print(name, len(df))
print("Graph Nodes:", GRAPH.number_of_nodes())
print("Graph Edges:", GRAPH.number_of_edges())
print("==============================")

app = FastAPI(title="SAP O2C Graph Query System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    answer: str
    result_data: Optional[list] = None
    error: Optional[str] = None


@app.get("/")
def root():
    return {
        "message": "SAP O2C Graph Query System API",
        "endpoints": {
            "/graph": "GET - Retrieve graph data for visualization",
            "/query": "POST - Query the system with natural language"
        }
    }


@app.get("/graph")
def get_graph():
    """Return graph data for visualization"""
    try:
        graph_data = graph_builder.get_graph_data_for_viz()
        return {
            "success": True,
            "graph": graph_data,
            "stats": {
                "total_nodes": GRAPH.number_of_nodes(),
                "total_edges": GRAPH.number_of_edges(),
                "displayed_nodes": len(graph_data['nodes'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
def query_system(request: QueryRequest):
    """Process natural language query and return results"""
    try:
        question = request.question.strip()

        if not question:
            return QueryResponse(
                success=False,
                answer="Please provide a question.",
                error="Empty question"
            )

        # Step 1: Generate SQL query using LLM
        sql_result = generate_sql_query(question, DATASETS)

        if not sql_result['success']:
            return QueryResponse(
                success=False,
                answer=sql_result.get('error', 'Failed to generate query'),
                error=sql_result.get('error')
            )

        sql_query = sql_result['sql_query']

        # Step 2: Execute the query
        query_result = execute_query(sql_query, DATASETS)

        if not query_result['success']:
            return QueryResponse(
                success=False,
                answer=f"Query execution failed: {query_result.get('error')}",
                error=query_result.get('error')
            )

        # Step 3: Generate natural language response
        answer = generate_natural_language_response(question, query_result)

        return QueryResponse(
            success=True,
            answer=answer,
            result_data=query_result['result']
        )

    except Exception as e:
        return QueryResponse(
            success=False,
            answer=f"System error: {str(e)}",
            error=str(e)
        )


@app.get("/stats")
def get_stats():
    """Return dataset statistics"""
    stats = {}
    for name, df in DATASETS.items():
        stats[name] = {
            "rows": len(df),
            "columns": len(df.columns) if len(df) > 0 else 0
        }
    return {"success": True, "stats": stats}


def get_full_o2c_path(graph, start_node):
    path_nodes = set()
    path_edges = []

    if start_node not in graph:
        return {"nodes": [], "edges": []}

    for node in nx.descendants(graph, start_node):
        path_nodes.add(node)

    for node in nx.ancestors(graph, start_node):
        path_nodes.add(node)

    path_nodes.add(start_node)

    for u, v in graph.edges():
        if u in path_nodes and v in path_nodes:
            path_edges.append({"source": u, "target": v})

    return {
        "nodes": list(path_nodes),
        "edges": path_edges
    }


@app.post("/trace-flow")
def trace_flow(request: dict):
    node_id = request.get("node_id")

    result = get_full_o2c_path(GRAPH, node_id)

    return {
        "success": True,
        "flow_nodes": result["nodes"],
        "flow_edges": result["edges"]
    }
@app.get("/detect-broken-flows")
def detect_broken_flows():
    broken = []

    so_df = DATASETS["sales_order_headers"]
    del_df = DATASETS["outbound_delivery_items"]
    bill_df = DATASETS["billing_document_items"]

    delivery_refs = set(del_df["reference_sd_document"])
    billing_refs = set(bill_df["reference_sd_document"])

    for _, so in so_df.iterrows():
        so_id = so["sales_document"]

        missing = []

        if so_id not in delivery_refs:
            missing.append("Delivery")

        if so_id in delivery_refs and so_id not in billing_refs:
            missing.append("Billing")

        if missing:
            broken.append({
                "id": so_id,
                "missing": missing
            })

    return {
        "success": True,
        "broken_flows": broken
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
