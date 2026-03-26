import networkx as nx
from data_loader import load_all_data

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.datasets = load_all_data()
        
    def build_graph(self):
        """Build the complete O2C graph with nodes and relationships"""
        print("Building graph...")
        
        # Add Sales Order nodes and relationships
        self._add_sales_orders()
        self._add_deliveries()
        self._add_billing_documents()
        self._add_journal_entries()
        self._add_payments()
        self._add_master_data()
        
        print(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph
    
    def _add_sales_orders(self):
        """Add sales order headers and items"""
        so_headers = self.datasets['sales_order_headers']
        so_items = self.datasets['sales_order_items']
        
        for _, row in so_headers.iterrows():
            so_id = row['salesOrder']
            self.graph.add_node(
                f"SO-{so_id}",
                type="SalesOrder",
                data=row.to_dict()
            )
        
        for _, row in so_items.iterrows():
            so_id = row['salesOrder']
            item_id = row['salesOrderItem']
            node_id = f"SO-{so_id}-ITEM-{item_id}"
            
            self.graph.add_node(
                node_id,
                type="SalesOrderItem",
                data=row.to_dict()
            )
            
            # Link item to header
            self.graph.add_edge(f"SO-{so_id}", node_id, relationship="HAS_ITEM")
    
    def _add_deliveries(self):
        """Add delivery documents and link to sales orders"""
        del_headers = self.datasets['outbound_delivery_headers']
        del_items = self.datasets['outbound_delivery_items']
        
        for _, row in del_headers.iterrows():
            del_id = row['deliveryDocument']
            self.graph.add_node(
                f"DEL-{del_id}",
                type="Delivery",
                data=row.to_dict()
            )
        
        for _, row in del_items.iterrows():
            del_id = row['deliveryDocument']
            item_id = row['deliveryDocumentItem']
            ref_so = row.get('referenceSDDocument', '')
            ref_so_item = row.get('referenceSDDocumentItem', '')
            
            node_id = f"DEL-{del_id}-ITEM-{item_id}"
            self.graph.add_node(
                node_id,
                type="DeliveryItem",
                data=row.to_dict()
            )
            
            # Link to delivery header
            self.graph.add_edge(f"DEL-{del_id}", node_id, relationship="HAS_ITEM")
            
            # Link to sales order item
            if ref_so and ref_so_item:
                so_item_node = f"SO-{ref_so}-ITEM-{ref_so_item}"
                if self.graph.has_node(so_item_node):
                    self.graph.add_edge(so_item_node, node_id, relationship="DELIVERED_BY")
    
    def _add_billing_documents(self):
        """Add billing documents (invoices) and link to deliveries"""
        bill_headers = self.datasets['billing_document_headers']
        bill_items = self.datasets['billing_document_items']
        
        for _, row in bill_headers.iterrows():
            bill_id = row['billingDocument']
            self.graph.add_node(
                f"BILL-{bill_id}",
                type="BillingDocument",
                data=row.to_dict()
            )
        
        for _, row in bill_items.iterrows():
            bill_id = row['billingDocument']
            item_id = row['billingDocumentItem']
            ref_doc = row.get('referenceSDDocument', '')
            ref_doc_item = row.get('referenceSDDocumentItem', '')
            
            node_id = f"BILL-{bill_id}-ITEM-{item_id}"
            self.graph.add_node(
                node_id,
                type="BillingDocumentItem",
                data=row.to_dict()
            )
            
            # Link to billing header
            self.graph.add_edge(f"BILL-{bill_id}", node_id, relationship="HAS_ITEM")
            
            # Link to delivery item
            if ref_doc and ref_doc_item:
                del_item_node = f"DEL-{ref_doc}-ITEM-{ref_doc_item}"
                if self.graph.has_node(del_item_node):
                    self.graph.add_edge(del_item_node, node_id, relationship="BILLED_BY")
    
    def _add_journal_entries(self):
        """Add journal entries (accounting records)"""
        journal_entries = self.datasets['journal_entry_items_accounts_receivable']
        
        for _, row in journal_entries.iterrows():
            acc_doc = row.get('accountingDocument', '')
            fiscal_year = row.get('fiscalYear', '')
            company = row.get('companyCode', '')
            ref_doc = row.get('referenceDocument', '')
            
            if not acc_doc:
                continue
                
            je_id = f"JE-{company}-{acc_doc}-{fiscal_year}"
            self.graph.add_node(
                je_id,
                type="JournalEntry",
                data=row.to_dict()
            )
            
            # Link to billing document
            if ref_doc:
                bill_node = f"BILL-{ref_doc}"
                if self.graph.has_node(bill_node):
                    self.graph.add_edge(bill_node, je_id, relationship="POSTED_AS")
    
    def _add_payments(self):
        """Add payment records"""
        payments = self.datasets['payments_accounts_receivable']
        
        for _, row in payments.iterrows():
            payment_doc = row.get('paymentDocument', '')
            company = row.get('companyCode', '')
            fiscal_year = row.get('fiscalYear', '')
            
            if not payment_doc:
                continue
                
            pay_id = f"PAY-{company}-{payment_doc}-{fiscal_year}"
            self.graph.add_node(
                pay_id,
                type="Payment",
                data=row.to_dict()
            )
    
    def _add_master_data(self):
        """Add master data: customers, products, plants"""
        # Add customers
        customers = self.datasets['business_partners']
        for _, row in customers.iterrows():
            bp_id = row['businessPartner']
            self.graph.add_node(
                f"CUST-{bp_id}",
                type="Customer",
                data=row.to_dict()
            )
        
        # Link customers to sales orders
        so_headers = self.datasets['sales_order_headers']
        for _, row in so_headers.iterrows():
            so_id = row['salesOrder']
            customer_id = row.get('soldToParty', '')
            if customer_id:
                cust_node = f"CUST-{customer_id}"
                so_node = f"SO-{so_id}"
                if self.graph.has_node(cust_node) and self.graph.has_node(so_node):
                    self.graph.add_edge(cust_node, so_node, relationship="PLACED")
        
        # Add products
        products = self.datasets['products']
        for _, row in products.iterrows():
            prod_id = row['product']
            self.graph.add_node(
                f"PROD-{prod_id}",
                type="Product",
                data=row.to_dict()
            )
        
        # Link products to sales order items
        so_items = self.datasets['sales_order_items']
        for _, row in so_items.iterrows():
            material = row.get('material', '')
            so_id = row['salesOrder']
            item_id = row['salesOrderItem']
            
            if material:
                prod_node = f"PROD-{material}"
                item_node = f"SO-{so_id}-ITEM-{item_id}"
                if self.graph.has_node(prod_node) and self.graph.has_node(item_node):
                    self.graph.add_edge(item_node, prod_node, relationship="FOR_PRODUCT")
        
        # Add plants
        plants = self.datasets['plants']
        for _, row in plants.iterrows():
            plant_id = row['plant']
            self.graph.add_node(
                f"PLANT-{plant_id}",
                type="Plant",
                data=row.to_dict()
            )
    def get_graph_data_for_viz(self):
        """Convert NetworkX graph to format for React Flow visualization"""
        import math
        import numpy as np

        def clean_value(val):
            # Handle NaN / Inf
            if isinstance(val, float):
                if math.isnan(val) or math.isinf(val):
                    return None
                return float(val)

            # Handle numpy types
            if isinstance(val, (np.integer,)):
                return int(val)
            if isinstance(val, (np.floating,)):
                return float(val)

            return val

        def clean_dict(d):
            if not isinstance(d, dict):
                return d
            return {k: clean_value(v) for k, v in d.items()}

        nodes = []
        edges = []

        node_list = list(self.graph.nodes(data=True))[:500]
        node_ids = set([n[0] for n in node_list])

        # ✅ Clean nodes
        for node_id, node_data in node_list:
            raw_metadata = node_data.get("data", {})
            cleaned_metadata = clean_dict(raw_metadata)

            nodes.append({
                "id": str(node_id),
                "type": str(node_data.get("type", "Unknown")),
                "data": {
                    "label": str(node_id),
                    "type": str(node_data.get("type", "Unknown")),
                    "metadata": cleaned_metadata
                }
            })

        # ✅ Clean edges
        for source, target, edge_data in self.graph.edges(data=True):
            if source in node_ids and target in node_ids:
                edges.append({
                    "id": f"{source}-{target}",
                    "source": str(source),
                    "target": str(target),
                    "label": str(edge_data.get("relationship", ""))
                })

        # 🔥 FINAL SAFE RETURN (forces JSON compliance)
        import json
        return json.loads(json.dumps({"nodes": nodes, "edges": edges}))
    def get_full_o2c_path(graph, start_node):
        import networkx as nx

        path_nodes = set()
        path_edges = []

        # Traverse forward
        for target in nx.descendants(graph, start_node):
            path_nodes.add(target)

        # Traverse backward
        for source in nx.ancestors(graph, start_node):
            path_nodes.add(source)

        path_nodes.add(start_node)

        # Get edges
        for u, v in graph.edges():
            if u in path_nodes and v in path_nodes:
                path_edges.append({"source": u, "target": v})

        return {
            "nodes": list(path_nodes),
            "edges": path_edges
        }
        
        