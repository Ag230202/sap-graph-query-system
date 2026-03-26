# Development Guide

This guide explains how to extend and customize the SAP O2C Graph Query System.

---

## 🛠️ Development Setup

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## 📝 Adding New Features

### 1. Adding New Query Types

**File: `backend/query_handler.py`**

To support new query patterns, update the `SYSTEM_PROMPT`:

```python
SYSTEM_PROMPT = """
...existing content...

New capabilities:
- Time-series analysis: "Show sales trend over time"
- Customer segmentation: "Group customers by revenue"
...
"""
```

### 2. Improving Graph Construction

**File: `backend/graph_builder.py`**

To add new entity types or relationships:

```python
def _add_custom_entity(self):
    """Add your custom entity"""
    custom_data = self.datasets['your_custom_table']
    
    for _, row in custom_data.iterrows():
        entity_id = row['id_field']
        self.graph.add_node(
            f"CUSTOM-{entity_id}",
            type="CustomEntity",
            data=row.to_dict()
        )
        
        # Add relationships
        self.graph.add_edge(
            source_node,
            f"CUSTOM-{entity_id}",
            relationship="YOUR_RELATIONSHIP"
        )
```

### 3. Customizing Visualization

**File: `frontend/src/App.js`**

To change node appearance:

```javascript
const getNodeColor = (type) => {
  const colors = {
    'YourNewType': '#FF5733',  // Add your color
    ...existing colors...
  };
  return colors[type] || '#999999';
};
```

To add custom node interactions:

```javascript
const onNodeDoubleClick = useCallback((event, node) => {
  // Your custom action
  console.log('Node double-clicked:', node);
}, []);

// Add to ReactFlow component
<ReactFlow
  ...
  onNodeDoubleClick={onNodeDoubleClick}
/>
```

---

## 🔧 Switching LLM Providers

### Using Groq (Faster, Free)

**File: `backend/query_handler.py`**

```python
import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

def generate_sql_query(question: str, datasets: Dict[str, pd.DataFrame]):
    # ... guardrails check ...
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        model="mixtral-8x7b-32768",
        temperature=0.1
    )
    
    sql_query = extract_sql_from_response(response.choices[0].message.content)
    # ... rest of the function ...
```

### Using OpenAI

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ],
    temperature=0.1
)
```

---

## 🧪 Testing

### Backend API Testing

```bash
# Start backend
cd backend
python main.py

# Test graph endpoint
curl http://localhost:8000/graph

# Test query endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total sales amount?"}'
```

### Frontend Testing

```bash
cd frontend
npm test
```

---

## 📊 Adding Advanced Analytics

### Example: Flow Completion Analysis

**File: `backend/graph_builder.py`**

```python
def analyze_flow_completion(self):
    """Analyze O2C flow completion rates"""
    stats = {
        'total_sales_orders': 0,
        'delivered': 0,
        'billed': 0,
        'paid': 0,
        'completion_rate': 0
    }
    
    for node_id, node_data in self.graph.nodes(data=True):
        if node_data.get('type') == 'SalesOrder':
            stats['total_sales_orders'] += 1
            
            # Check if delivered
            successors = list(self.graph.successors(node_id))
            # ... analyze flow ...
    
    return stats
```

### Example: Product Popularity

```python
def get_product_popularity(self):
    """Rank products by number of sales"""
    product_counts = {}
    
    for node_id, node_data in self.graph.nodes(data=True):
        if node_data.get('type') == 'Product':
            # Count incoming edges from sales order items
            predecessors = list(self.graph.predecessors(node_id))
            product_counts[node_id] = len(predecessors)
    
    return sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
```

---

## 🎨 UI Customization

### Changing Theme Colors

**File: `frontend/src/App.css`**

```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --background: #f5f5f5;
  --text-color: #333;
}

.header {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}
```

### Adding Dark Mode

```css
[data-theme="dark"] {
  --primary-color: #4a5fd9;
  --background: #1a1a1a;
  --text-color: #ffffff;
}
```

```javascript
// In App.js
const [theme, setTheme] = useState('light');

useEffect(() => {
  document.documentElement.setAttribute('data-theme', theme);
}, [theme]);
```

---

## 🚀 Performance Optimization

### 1. Graph Visualization Performance

For large graphs (>1000 nodes), limit displayed nodes:

```javascript
// In App.js
const loadGraph = async () => {
  // ... existing code ...
  
  // Limit to first 500 nodes
  const limitedNodes = flowNodes.slice(0, 500);
  setNodes(limitedNodes);
  
  // Filter edges to only show those between displayed nodes
  const nodeIds = new Set(limitedNodes.map(n => n.id));
  const limitedEdges = flowEdges.filter(e => 
    nodeIds.has(e.source) && nodeIds.has(e.target)
  );
  setEdges(limitedEdges);
};
```

### 2. Query Caching

**File: `backend/query_handler.py`**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def execute_query_cached(sql_query: str, datasets_hash: str):
    """Cached query execution"""
    # ... query execution logic ...
    pass
```

### 3. Lazy Loading Data

Load datasets on-demand instead of all at startup:

```python
class LazyDataLoader:
    def __init__(self):
        self._datasets = {}
    
    def __getitem__(self, key):
        if key not in self._datasets:
            self._datasets[key] = load_jsonl(key)
        return self._datasets[key]
```

---

## 🔒 Security Enhancements

### 1. API Key Security

Never commit API keys. Use environment variables:

```python
# Bad
GEMINI_API_KEY = "AIza..."

# Good
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set")
```

### 2. Input Validation

```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    question: str
    
    @validator('question')
    def validate_question(cls, v):
        if len(v) > 500:
            raise ValueError('Question too long')
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v
```

### 3. Rate Limiting

```python
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("10/minute")
def query_system(request: QueryRequest):
    # ... existing code ...
```

---

## 📦 Deployment Best Practices

### 1. Environment-Specific Configs

```python
# config.py
import os

class Config:
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    API_KEY = os.getenv("GEMINI_API_KEY")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
```

### 2. Health Checks

```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "graph_nodes": GRAPH.number_of_nodes(),
        "datasets_loaded": len(DATASETS)
    }
```

### 3. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.post("/query")
def query_system(request: QueryRequest):
    logger.info(f"Query received: {request.question}")
    # ... existing code ...
```

---

## 🐛 Debugging Tips

### Backend Debugging

```bash
# Run with debug mode
uvicorn main:app --reload --log-level debug

# Check graph construction
python -c "from graph_builder import GRAPH; print(GRAPH.number_of_nodes())"

# Test query handler directly
python -c "from query_handler import generate_sql_query; print(generate_sql_query('test', {}))"
```

### Frontend Debugging

```javascript
// Add console logs in App.js
console.log('Graph data:', graphData);
console.log('Query response:', response.data);

// Use React DevTools
// Install: https://chrome.google.com/webstore/detail/react-developer-tools
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Flow Documentation](https://reactflow.dev/)
- [NetworkX Documentation](https://networkx.org/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Pandas Documentation](https://pandas.pydata.org/)

---

**Happy Coding! 🚀**
