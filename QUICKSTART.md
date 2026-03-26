# 🚀 Quick Start Guide

Get the SAP O2C Graph Query System running in 5 minutes!

---

## ✅ Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Docker** installed ([Download here](https://www.docker.com/get-started))
- [ ] **Docker Compose** installed (usually comes with Docker Desktop)
- [ ] **Google Gemini API Key** (free tier) - [Get it here](https://ai.google.dev)
- [ ] **The SAP O2C dataset** (already included in `/data` folder)

---

## 📦 Option 1: Docker (Recommended - Easiest)

### Step 1: Get Your API Key

1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Create a new project and API key
4. Copy the key (starts with `AIza...`)

### Step 2: Configure Environment

```bash
# Clone/navigate to the project
cd sap-graph-query-system

# Create .env file
cp .env.example .env

# Edit .env and paste your API key
nano .env  # or use any text editor
```

Your `.env` should look like:
```
GEMINI_API_KEY=AIzaSyC...your_actual_key_here...
```

### Step 3: Start Everything

```bash
# Build and start (first time takes 2-3 minutes)
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### Step 4: Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 5: Try Example Queries

In the chat interface, try:
1. "Which products have the most billing documents?"
2. "Show me sales order 740506"
3. "What is the total sales amount?"

---

## 💻 Option 2: Local Development (Manual)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY=your_key_here  # Windows: set GEMINI_API_KEY=your_key_here

# Run backend
python main.py
```

Backend will start on http://localhost:8000

### Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm start
```

Frontend will open automatically at http://localhost:3000

---

## 🎯 What You Should See

### 1. Graph Visualization (Left Panel)

You'll see a network graph with:
- **Colored nodes** representing different entities
- **Edges** showing relationships
- **Interactive controls** to zoom, pan, and inspect

**Node Colors:**
- 🔵 Blue: Sales Orders
- 🟢 Green: Deliveries
- 🟠 Orange: Billing Documents
- 🔴 Red: Customers
- 🟦 Cyan: Products

### 2. Chat Interface (Right Panel)

A chat window where you can:
- Type natural language questions
- See SQL queries generated
- View results
- Click example queries to get started

---

## 🧪 Verify Everything Works

### Test 1: Check Backend is Running

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "SAP O2C Graph Query System API",
  "endpoints": { ... }
}
```

### Test 2: Check Graph is Loaded

```bash
curl http://localhost:8000/graph
```

Should return graph data with nodes and edges.

### Test 3: Try a Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total sales amount?"}'
```

Should return a natural language answer.

---

## 🛑 Stopping the Application

### If using Docker:
```bash
docker-compose down
```

### If running manually:
- Press `Ctrl+C` in the terminal running the backend
- Press `Ctrl+C` in the terminal running the frontend

---

## 🐛 Troubleshooting

### Problem: "Port already in use"

**Solution:** Stop the service using that port:

```bash
# Find process using port 8000
lsof -i :8000  # or: netstat -ano | findstr :8000 on Windows
kill -9 <PID>  # or: taskkill /PID <PID> /F on Windows
```

### Problem: "GEMINI_API_KEY not configured"

**Solution:** Make sure your `.env` file exists and has the correct key:

```bash
cat .env  # Should show: GEMINI_API_KEY=AIza...
```

### Problem: "Cannot connect to backend"

**Solution:** Check if backend is running:

```bash
docker-compose logs backend  # if using Docker
# or check http://localhost:8000 in browser
```

### Problem: "Graph not loading"

**Solution:** Check data files are present:

```bash
ls data/  # Should show 19 folders
ls data/sales_order_headers/  # Should show .jsonl files
```

### Problem: Docker build fails

**Solution:** Make sure Docker has enough resources:
- Docker Desktop → Settings → Resources
- Recommended: 4GB RAM, 2 CPUs minimum

---

## 📝 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Slow graph loading | Normal for first load, graph has 1000+ nodes |
| Query returns "not in dataset" | Try different phrasing, check example queries |
| Frontend shows "Network Error" | Backend not running, start it first |
| "Module not found" errors | Run `pip install -r requirements.txt` |
| Graph looks cluttered | Use zoom controls, or limit nodes in code |

---

## 🎓 Next Steps

Now that it's running:

1. **Explore the Graph**: Click nodes to see details
2. **Try Example Queries**: Click suggested queries in the chat
3. **Read the README**: Full documentation in `README.md`
4. **Customize**: See `DEVELOPMENT.md` for extending the system

---

## 📞 Getting Help

If something doesn't work:

1. Check the console/terminal for error messages
2. Look at `docker-compose logs` if using Docker
3. Verify all prerequisites are installed
4. Read the full README.md for detailed troubleshooting

---

## ✨ You're All Set!

The system is now running. Head to http://localhost:3000 and start exploring your SAP O2C data with natural language queries!

**Pro tip:** Start with the example queries to see how it works, then try your own questions.

---

**Built for SAP Forward Deployed Engineer Assessment** 🚀
