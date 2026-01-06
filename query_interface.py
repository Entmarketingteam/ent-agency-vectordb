"""
Query Interface for ENT Agency Campaign Vector Database
Natural language search interface for campaign insights
"""

import os
from typing import List, Dict, Any
from pinecone_setup import ENTAgencyVectorDB

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class CampaignQueryInterface:
    """Interactive query interface for campaign data"""
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str, default_namespace: str = "default"):
        self.db = ENTAgencyVectorDB(
            pinecone_api_key=pinecone_api_key,
            openai_api_key=openai_api_key
        )
        self.db.create_index()
        self.default_namespace = default_namespace
    
    def search(self, query: str, top_k: int = 10, 
               namespace: str = None, 
               filters: Dict = None,
               use_reranking: bool = True) -> List[Dict]:
        """
        Search campaigns using natural language with reranking
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            namespace: Namespace to search (default: self.default_namespace)
            filters: Optional metadata filters
            use_reranking: Whether to use reranking (recommended)
        
        Returns:
            List of matching campaigns
        """
        if namespace is None:
            namespace = self.default_namespace
        
        results = self.db.search(
            query_text=query, 
            top_k=top_k, 
            namespace=namespace,
            filter_dict=filters,
            use_reranking=use_reranking
        )
        return results
    
    def format_results(self, results: List[Dict], show_full: bool = False):
        """Pretty print search results"""
        if not results:
            print("\nNo results found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(results)} results")
        print(f"{'='*80}\n")
        
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            score = result.get('score', 0.0)
            
            print(f"Result #{i} (Relevance: {score:.3f})")
            print("-" * 80)
            
            # Show key fields (handle both old and new API formats)
            quarter = metadata.get('quarter', '')
            if quarter:
                print(f"📅 Quarter: {quarter}")
            
            creator = metadata.get('creator', '')
            if creator:
                print(f"👤 Creator: {creator}")
            
            brand = metadata.get('brand', '')
            if brand:
                print(f"🏢 Brand: {brand}")
            
            campaign_type = metadata.get('campaign_type', '')
            if campaign_type:
                print(f"📱 Type: {campaign_type}")
            
            platform = metadata.get('platform', '')
            if platform:
                print(f"🌐 Platform: {platform}")
            
            date = metadata.get('date', '')
            if date:
                print(f"📆 Date: {date}")
            
            # Show metrics if available
            metrics = {k.replace('metric_', ''): v for k, v in metadata.items() if k.startswith('metric_')}
            if metrics:
                print(f"📊 Metrics:")
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        print(f"   • {metric_name}: {metric_value:,}")
                    else:
                        print(f"   • {metric_name}: {metric_value}")
            
            revenue = metadata.get('revenue')
            if revenue:
                try:
                    print(f"💰 Revenue: ${float(revenue):,.2f}")
                except:
                    print(f"💰 Revenue: {revenue}")
            
            if show_full:
                content = metadata.get('content', metadata.get('text', ''))
                if content:
                    print(f"\n📄 Full Content:")
                    print(content)
            
            print("\n")
    
    def query_best_performing(self, metric: str = "engagement", quarter: str = None, top_k: int = 5, namespace: str = None):
        """Find best performing campaigns by a specific metric"""
        query = f"campaigns with high {metric}"
        
        filters = {}
        if quarter:
            filters['quarter'] = quarter
        
        if namespace is None:
            namespace = self.default_namespace
            if quarter:
                namespace = quarter.replace(' ', '_').lower()
        
        results = self.search(query, top_k=top_k, namespace=namespace, filters=filters)
        
        print(f"\n🏆 Top {top_k} campaigns by {metric}")
        if quarter:
            print(f"   Filtered by: {quarter}")
        if namespace:
            print(f"   Namespace: {namespace}")
        
        self.format_results(results)
        return results
    
    def query_by_brand(self, brand_name: str, top_k: int = 10, namespace: str = None):
        """Find all campaigns for a specific brand"""
        filters = {'brand': brand_name}
        query = f"{brand_name} campaigns"
        
        if namespace is None:
            namespace = self.default_namespace
        
        results = self.search(query, top_k=top_k, namespace=namespace, filters=filters)
        
        print(f"\n🏢 Campaigns for {brand_name}")
        self.format_results(results)
        return results
    
    def query_by_creator(self, creator_name: str, top_k: int = 10, namespace: str = None):
        """Find all campaigns for a specific creator"""
        filters = {'creator': creator_name}
        query = f"{creator_name} campaigns"
        
        if namespace is None:
            namespace = self.default_namespace
        
        results = self.search(query, top_k=top_k, namespace=namespace, filters=filters)
        
        print(f"\n👤 Campaigns by {creator_name}")
        self.format_results(results)
        return results
    
    def analyze_trends(self, topic: str, quarters: List[str] = None):
        """Analyze trends across quarters"""
        if not quarters:
            quarters = ["2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4", "2025 Q1", "2025 Q2", "2025 Q3"]
        
        print(f"\n📈 Trend Analysis: {topic}")
        print("="*80)
        
        for quarter in quarters:
            filters = {'quarter': quarter}
            namespace = quarter.replace(' ', '_').lower()
            results = self.search(topic, top_k=5, namespace=namespace, filters=filters)
            
            if results:
                print(f"\n{quarter}: {len(results)} relevant campaigns")
                # Calculate average metrics if available
                total_engagement = 0
                count = 0
                for result in results:
                    metadata = result.get('metadata', {})
                    if 'metric_engagement' in metadata:
                        total_engagement += metadata['metric_engagement']
                        count += 1
                
                if count > 0:
                    avg_engagement = total_engagement / count
                    print(f"   Average Engagement: {avg_engagement:,.0f}")
    
    def compare_creators(self, creator1: str, creator2: str, metric: str = "engagement", namespace: str = None):
        """Compare performance between two creators"""
        print(f"\n⚖️  Comparing {creator1} vs {creator2}")
        print("="*80)
        
        if namespace is None:
            namespace = self.default_namespace
        
        # Get campaigns for each creator
        results1 = self.search(f"{creator1} {metric}", top_k=10, namespace=namespace, filters={'creator': creator1})
        results2 = self.search(f"{creator2} {metric}", top_k=10, namespace=namespace, filters={'creator': creator2})
        
        print(f"\n{creator1}:")
        print(f"  Total campaigns: {len(results1)}")
        
        print(f"\n{creator2}:")
        print(f"  Total campaigns: {len(results2)}")
    
    def interactive_mode(self):
        """Start interactive query session"""
        print("\n" + "="*80)
        print("🔍 ENT Agency Campaign Search - Interactive Mode")
        print("="*80)
        print("\nExample queries:")
        print("  • 'What were our best Instagram campaigns in Q1 2024?'")
        print("  • 'Show me high engagement Thorne campaigns'")
        print("  • 'Find all campaigns by Nicki Entenmann'")
        print("  • 'What campaigns had over 100k impressions?'")
        print("\nType 'quit' or 'exit' to leave\n")
        
        while True:
            try:
                query = input("🔍 Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if not query:
                    continue
                
                # Parse query for filters
                filters = {}
                
                # Extract quarter filter and determine namespace
                namespace = self.default_namespace
                quarters = ["Q1", "Q2", "Q3", "Q4"]
                for q in quarters:
                    if q in query.upper():
                        for year in ["2023", "2024", "2025"]:
                            if year in query:
                                quarter_str = f"{year} {q}"
                                filters['quarter'] = quarter_str
                                namespace = quarter_str.replace(' ', '_').lower()
                                break
                
                # Search
                results = self.search(query, top_k=10, namespace=namespace, filters=filters or None)
                self.format_results(results)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\nError: {e}")


def main():
    """Main function with example queries"""
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("ERROR: Please set PINECONE_API_KEY and OPENAI_API_KEY environment variables")
        return
    
    # Initialize query interface
    interface = CampaignQueryInterface(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    print("\n" + "="*80)
    print("ENT Agency Campaign Query Interface")
    print("="*80)
    
    # Show menu
    print("\nWhat would you like to do?")
    print("1. Interactive search mode")
    print("2. Find best performing campaigns")
    print("3. Search by brand")
    print("4. Search by creator")
    print("5. Analyze trends")
    print("6. Compare creators")
    
    choice = input("\nEnter choice (1-6) or press Enter for interactive mode: ").strip()
    
    if choice == "1" or not choice:
        interface.interactive_mode()
    
    elif choice == "2":
        metric = input("Enter metric (engagement/impressions/clicks): ").strip() or "engagement"
        quarter = input("Filter by quarter (e.g., '2024 Q1') or press Enter for all: ").strip() or None
        interface.query_best_performing(metric=metric, quarter=quarter)
    
    elif choice == "3":
        brand = input("Enter brand name: ").strip()
        if brand:
            interface.query_by_brand(brand)
    
    elif choice == "4":
        creator = input("Enter creator name: ").strip()
        if creator:
            interface.query_by_creator(creator)
    
    elif choice == "5":
        topic = input("Enter topic to analyze: ").strip() or "engagement"
        interface.analyze_trends(topic)
    
    elif choice == "6":
        creator1 = input("Enter first creator name: ").strip()
        creator2 = input("Enter second creator name: ").strip()
        if creator1 and creator2:
            interface.compare_creators(creator1, creator2)


if __name__ == "__main__":
    main()
