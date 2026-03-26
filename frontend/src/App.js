import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import './App.css';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;;

// Node color mapping by type
const getNodeColor = (type) => {
  const colors = {
    'SalesOrder': '#4A90E2',
    'SalesOrderItem': '#7AB8F5',
    'Delivery': '#50C878',
    'DeliveryItem': '#7FD99F',
    'BillingDocument': '#F5A623',
    'BillingDocumentItem': '#F7C66B',
    'JournalEntry': '#9013FE',
    'Payment': '#BD10E0',
    'Customer': '#E91E63',
    'Product': '#00BCD4',
    'Plant': '#8BC34A',
  };
  return colors[type] || '#999999';
};

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [querying, setQuerying] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [highlightedNodes, setHighlightedNodes] = useState([]);
  const [highlightedEdges, setHighlightedEdges] = useState([]);
  const [showFlowPanel, setShowFlowPanel] = useState(false);
  const [currentFlow, setCurrentFlow] = useState(null);
  const { fitView, setCenter } = useReactFlow();

  // Load graph data on mount
  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/graph`);
      
      if (response.data.success) {
        const graphData = response.data.graph;
        
        // Convert nodes to ReactFlow format
        const flowNodes = graphData.nodes.map((node, index) => ({
          id: node.id,
          type: 'default',
          data: { 
            label: `${node.type}\n${node.id}`,
            ...node.data
          },
          position: {
            x: (index % 10) * 200,
            y: Math.floor(index / 10) * 150
          },
          style: {
            background: getNodeColor(node.type),
            color: 'white',
            border: '1px solid #222',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '10px',
            width: 150
          }
        }));
        
        // Convert edges to ReactFlow format
        const flowEdges = graphData.edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label,
          type: 'smoothstep',
          animated: true,
          style: { stroke: '#555' }
        }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);
        
        setChatMessages([{
          role: 'system',
          content: `Graph loaded: ${response.data.stats.displayed_nodes} nodes displayed (${response.data.stats.total_nodes} total)`
        }]);
      }
    } catch (error) {
      console.error('Error loading graph:', error);
      setChatMessages([{
        role: 'error',
        content: 'Failed to load graph. Make sure backend is running.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = inputMessage.trim();
    setInputMessage('');
    setQuerying(true);
    
    // Add user message to chat
    setChatMessages(prev => [...prev, {
      role: 'user',
      content: userMessage
    }]);
    
    try {
      // Check if it's a broken flow query
    
      
      const response = await axios.post(`${API_BASE_URL}/query`, {
        question: userMessage
      });
      
      // Add assistant response
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer,
        sql_query: response.data.sql_query,
        result_data: response.data.result_data
      }]);
      
      // Highlight relevant nodes if results exist
      if (response.data.result_data && response.data.result_data.length > 0) {
        await highlightNodesFromResults(response.data.result_data);
      }
      
    } catch (error) {
      setChatMessages(prev => [...prev, {
        role: 'error',
        content: 'Query failed: ' + (error.response?.data?.detail || error.message)
      }]);
    } finally {
      setQuerying(false);
    }
  };

  const handleBrokenFlowQuery = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/detect-broken-flows`);
      
      if (response.data.success) {
        const brokenFlows = response.data.broken_flows;
        
        let message = `Found ${brokenFlows.length} sales orders with incomplete flows:\n\n`;
        brokenFlows.slice(0, 5).forEach((flow, idx) => {
          message += `${idx + 1}. ${flow.node_id}\n`;
          message += `   Missing: ${flow.missing_stages.join(', ')}\n`;
        });
        
        if (brokenFlows.length > 5) {
          message += `\n...and ${brokenFlows.length - 5} more.`;
        }
        
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: message
        }]);
        
        // Highlight broken flow nodes
        const brokenNodeIds = brokenFlows.map(f => f.node_id);
        highlightNodes(brokenNodeIds, '#FF4444');
      }
    } catch (error) {
      setChatMessages(prev => [...prev, {
        role: 'error',
        content: 'Failed to detect broken flows: ' + error.message
      }]);
    } finally {
      setQuerying(false);
    }
  };
const focusOnNodes = (nodeIds) => {
  if (!nodeIds || nodeIds.length === 0) return;

  const matched = nodes.filter(n => nodeIds.includes(n.id));

  if (matched.length === 0) return;

  const avgX = matched.reduce((sum, n) => sum + n.position.x, 0) / matched.length;
  const avgY = matched.reduce((sum, n) => sum + n.position.y, 0) / matched.length;

  setCenter(avgX, avgY, { zoom: 1.5, duration: 800 });
};
 const highlightNodesFromResults = async (resultData) => {
  try {
    if (!resultData || resultData.length === 0) return;

    // Extract IDs safely
    const nodeIds = resultData.map(r => 
      r.sales_order_id || 
      r.sales_document || 
      r.id
    ).filter(Boolean);

    if (nodeIds.length > 0) {
      highlightNodes(nodeIds, '#FFD700');
      focusOnNodes(nodeIds);
    }

  } catch (error) {
    console.error('Failed to highlight nodes:', error);
  }
};

  const highlightNodes = (nodeIds, color = '#FFD700') => {
    setHighlightedNodes(nodeIds);
    
    setNodes(nds => nds.map(node => {
      if (nodeIds.includes(node.id)) {
        return {
          ...node,
          style: {
            ...node.style,
            border: `4px solid ${color}`,
            boxShadow: `0 0 20px ${color}`
          }
        };
      }
      return {
        ...node,
        style: {
          ...node.style,
          border: '1px solid #222',
          boxShadow: 'none'
        }
      };
    }));
  };

 const traceFlow = async (nodeId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/trace-flow`, {
      node_id: nodeId
    });

    const { flow_nodes, flow_edges } = response.data;

    highlightNodes(flow_nodes, '#00FF00');
    focusOnNodes(flow_nodes);

    // Highlight nodes + dim others
    setNodes(nds => nds.map(node => {
      if (flow_nodes.includes(node.id)) {
        return {
          ...node,
          style: {
            ...node.style,
            border: '3px solid #00FF00',
            boxShadow: '0 0 15px #00FF00',
            opacity: 1
          }
        };
      }
      return {
        ...node,
        style: {
          ...node.style,
          opacity: 0.2
        }
      };
    }));

    // Highlight edges
    setEdges(eds => eds.map(edge => {
      const match = flow_edges.some(
        e => e.source === edge.source && e.target === edge.target
      );

      return {
        ...edge,
        style: {
          stroke: match ? '#00FF00' : '#ccc',
          strokeWidth: match ? 3 : 1,
          opacity: match ? 1 : 0.1
        }
      };
    }));

  } catch (error) {
    console.error(error);
  }
};
  const clearHighlights = () => {
    setHighlightedNodes([]);
    setHighlightedEdges([]);
    setShowFlowPanel(false);
    setCurrentFlow(null);
    
    setNodes(nds => nds.map(node => ({
      ...node,
      style: {
        ...node.style,
        border: '1px solid #222',
        boxShadow: 'none',
        opacity: 1
      }
    })));
    
    setEdges(eds => eds.map(edge => ({
      ...edge,
      style: {
        ...edge.style,
        opacity: 1,
        stroke: '#555',
        strokeWidth: 1
      }
    })));
  };

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const zoomToSelectedNode = (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    if (node) {
      setCenter(node.position.x + 75, node.position.y + 75, { zoom: 1.5, duration: 800 });
    }
  };

  return (
    <div className="App">
      <div className="header">
        <h1>SAP Order-to-Cash Graph Query System</h1>
        <div className="header-actions">
          {highlightedNodes.length > 0 && (
            <button onClick={clearHighlights} className="clear-btn">
              Clear Highlights
            </button>
          )}
        </div>
      </div>
      
      <div className="container">
        {/* Graph Visualization */}
        <div className="graph-panel">
          <h2>Graph Visualization</h2>
          {loading ? (
            <div className="loading">Loading graph...</div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
            >
              <Controls />
              <MiniMap />
              <Background variant="dots" gap={12} size={1} />
            </ReactFlow>
          )}
          
          {/* Node Details */}
          {selectedNode && (
            <div className="node-details">
              <h3>Node Details</h3>
              <button onClick={() => setSelectedNode(null)} className="close-btn">×</button>
              <div className="node-actions">
                <button onClick={() => traceFlow(selectedNode.id)} className="action-btn">
                  🔍 Trace Flow
                </button>
                <button onClick={() => zoomToSelectedNode(selectedNode.id)} className="action-btn">
                  🎯 Zoom to Node
                </button>
              </div>
              <pre>{JSON.stringify(selectedNode.data, null, 2)}</pre>
            </div>
          )}
          
          {/* Flow Panel */}
          {showFlowPanel && currentFlow && (
            <div className="flow-panel">
              <h3>O2C Flow Analysis</h3>
              <button onClick={() => setShowFlowPanel(false)} className="close-btn">×</button>
              <div className="flow-info">
                <p><strong>Start Node:</strong> {currentFlow.start_node}</p>
                <p><strong>Flow Status:</strong> {currentFlow.flow_complete ? 
                  '✅ Complete' : '⚠️ Incomplete'}</p>
                {!currentFlow.flow_complete && (
                  <p><strong>Missing Stages:</strong> {currentFlow.missing_stages.join(', ')}</p>
                )}
                <p><strong>Total Nodes in Flow:</strong> {currentFlow.flow_nodes.length}</p>
                
                <h4>Node Types:</h4>
                <ul>
                  {Object.entries(currentFlow.node_types).map(([type, nodes]) => (
                    <li key={type}>{type}: {nodes.length}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
        
        {/* Chat Interface */}
        <div className="chat-panel">
          <h2>Query Interface</h2>
          <div className="chat-messages">
            {chatMessages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-role">{msg.role}:</div>
                <div className="message-content">
                  {msg.content}
                </div>
              </div>
            ))}
            {querying && (
              <div className="message assistant">
                <div className="message-role">assistant:</div>
                <div className="message-content typing">Thinking...</div>
              </div>
            )}
          </div>
          
          <div className="chat-input">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="Ask a question about the O2C data..."
              disabled={querying}
            />
            <button onClick={handleQuery} disabled={querying || !inputMessage.trim()}>
              Send
            </button>
          </div>
          
          <div className="example-queries">
            <strong>Example queries:</strong>
            <ul>
              <li onClick={() => setInputMessage("Which products have the most billing documents?")}>
                Which products have the most billing documents?
              </li>
              <li onClick={() => setInputMessage("Show me sales orders with broken flows")}>
                Show me sales orders with broken flows
              </li>
              <li onClick={() => setInputMessage("Trace the flow for SO-1")}>
                Trace the flow for SO-1
              </li>
              <li onClick={() => setInputMessage("What is the total sales amount?")}>
                What is the total sales amount?
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// Wrap App with ReactFlowProvider
import { ReactFlowProvider } from 'reactflow';

export default function AppWrapper() {
  return (
    <ReactFlowProvider>
      <App />
    </ReactFlowProvider>
  );
}