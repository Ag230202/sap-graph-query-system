#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_data_loading():
    """Test that data files can be loaded"""
    print("Testing data loading...")
    try:
        from data_loader import load_all_data
        datasets = load_all_data()
        
        assert len(datasets) > 0, "No datasets loaded"
        
        # Check key datasets
        key_datasets = ['sales_order_headers', 'billing_document_headers', 'business_partners']
        for ds in key_datasets:
            assert ds in datasets, f"Missing dataset: {ds}"
            print(f"  ✓ {ds}: {len(datasets[ds])} records")
        
        print("✅ Data loading test passed\n")
        return True
    except Exception as e:
        print(f"❌ Data loading test failed: {e}\n")
        return False

def test_graph_construction():
    """Test that graph can be constructed"""
    print("Testing graph construction...")
    try:
        from graph_builder import GraphBuilder
        
        builder = GraphBuilder()
        graph = builder.build_graph()
        
        assert graph.number_of_nodes() > 0, "Graph has no nodes"
        assert graph.number_of_edges() > 0, "Graph has no edges"
        
        print(f"  ✓ Nodes: {graph.number_of_nodes()}")
        print(f"  ✓ Edges: {graph.number_of_edges()}")
        
        # Check node types
        node_types = set()
        for _, data in graph.nodes(data=True):
            node_types.add(data.get('type', 'Unknown'))
        
        print(f"  ✓ Node types: {', '.join(sorted(node_types))}")
        
        print("✅ Graph construction test passed\n")
        return True
    except Exception as e:
        print(f"❌ Graph construction test failed: {e}\n")
        return False

def test_graph_visualization_data():
    """Test that graph data can be formatted for visualization"""
    print("Testing graph visualization data...")
    try:
        from graph_builder import graph_builder
        
        viz_data = graph_builder.get_graph_data_for_viz()
        
        assert 'nodes' in viz_data, "Missing nodes in viz data"
        assert 'edges' in viz_data, "Missing edges in viz data"
        assert len(viz_data['nodes']) > 0, "No nodes in viz data"
        
        print(f"  ✓ Visualization nodes: {len(viz_data['nodes'])}")
        print(f"  ✓ Visualization edges: {len(viz_data['edges'])}")
        
        print("✅ Graph visualization test passed\n")
        return True
    except Exception as e:
        print(f"❌ Graph visualization test failed: {e}\n")
        return False

def test_query_handler_guardrails():
    """Test that query guardrails work"""
    print("Testing query guardrails...")
    try:
        from query_handler import is_query_allowed
        
        # Should be allowed
        allowed_queries = [
            "Which products have the most billing documents?",
            "Show me sales orders",
            "What is the total amount?"
        ]
        
        for q in allowed_queries:
            assert is_query_allowed(q), f"Should allow: {q}"
            print(f"  ✓ Allowed: {q}")
        
        # Should be rejected
        rejected_queries = [
            "Write me a story",
            "What is the capital of France?",
            "Calculate 2 + 2"
        ]
        
        for q in rejected_queries:
            assert not is_query_allowed(q), f"Should reject: {q}"
            print(f"  ✓ Rejected: {q}")
        
        print("✅ Query guardrails test passed\n")
        return True
    except Exception as e:
        print(f"❌ Query guardrails test failed: {e}\n")
        return False

def main():
    print("=" * 60)
    print("SAP O2C Graph Query System - Backend Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_data_loading,
        test_graph_construction,
        test_graph_visualization_data,
        test_query_handler_guardrails
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! Backend is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
