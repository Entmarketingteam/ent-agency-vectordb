"""
Pinecone Vector Database Setup for ENT Agency Campaign Data
This script sets up a Pinecone index and provides methods to ingest and query campaign data
Updated to use latest Pinecone patterns: namespaces, upsert_records, search with reranking
"""

import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import time

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manual .env loading if dotenv not available
    import os
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value:
                                os.environ[key] = value
        except:
            pass

try:
    from pinecone import Pinecone
    import openai
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "pinecone", "openai", "--break-system-packages"])
    from pinecone import Pinecone
    import openai


class ENTAgencyVectorDB:
    def __init__(self, pinecone_api_key: str, openai_api_key: str, index_name: str = "ent-agency-campaigns"):
        """
        Initialize the vector database
        
        Args:
            pinecone_api_key: Your Pinecone API key
            openai_api_key: Your OpenAI API key for embeddings (used if index doesn't have integrated embeddings)
            index_name: Name of the Pinecone index to create/use
        """
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.index_name = index_name
        self.index = None
        
        # Embedding model configuration (for manual embeddings if needed)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
    def create_index(self):
        """
        Check if index exists and connect to it.
        
        NOTE: According to best practices, indexes should be created using the Pinecone CLI:
        pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 \\
            --model llama-text-embed-v2 --field_map text=content
        
        This method will check if the index exists and connect to it.
        """
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"⚠️  Index '{self.index_name}' not found!")
            print("\nAccording to best practices, indexes should be created with the Pinecone CLI:")
            print(f"  pc index create -n {self.index_name} -m cosine -c aws -r us-east-1 \\")
            print("    --model llama-text-embed-v2 --field_map text=content")
            print("\nAlternatively, you can create it programmatically (not recommended for production):")
            print("  This will create a basic index without integrated embeddings.")
            
            create_anyway = input("\nCreate index programmatically anyway? (y/n): ").strip().lower()
            if create_anyway == 'y':
                from pinecone import ServerlessSpec
                print(f"Creating basic index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"Index '{self.index_name}' created successfully!")
                print("⚠️  Note: This index uses manual embeddings. For better performance,")
                print("   recreate with CLI using integrated embeddings (llama-text-embed-v2).")
            else:
                raise Exception(f"Index '{self.index_name}' does not exist. Please create it using the CLI first.")
        else:
            print(f"✓ Index '{self.index_name}' found and connected")
        
        self.index = self.pc.Index(self.index_name)
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding
    
    def prepare_campaign_document(self, campaign_data: Dict[str, Any]) -> str:
        """
        Convert campaign data into a searchable text document
        
        Expected fields in campaign_data:
        - quarter: e.g., "2024 Q1"
        - creator: e.g., "Nicki Entenmann"
        - brand: e.g., "Thorne"
        - campaign_type: e.g., "Instagram Post", "Story", "Reel"
        - date: Campaign date
        - metrics: Dict with impressions, engagement, clicks, etc.
        - content_description: Description of the content
        - platform: e.g., "Instagram", "TikTok", "LTK"
        - revenue: Revenue generated (optional)
        - notes: Any additional notes
        """
        doc_parts = []
        
        # Add structured data
        if 'quarter' in campaign_data:
            doc_parts.append(f"Quarter: {campaign_data['quarter']}")
        
        if 'creator' in campaign_data:
            doc_parts.append(f"Creator: {campaign_data['creator']}")
        
        if 'brand' in campaign_data:
            doc_parts.append(f"Brand: {campaign_data['brand']}")
        
        if 'campaign_type' in campaign_data:
            doc_parts.append(f"Campaign Type: {campaign_data['campaign_type']}")
        
        if 'platform' in campaign_data:
            doc_parts.append(f"Platform: {campaign_data['platform']}")
        
        if 'date' in campaign_data:
            doc_parts.append(f"Date: {campaign_data['date']}")
        
        # Add metrics
        if 'metrics' in campaign_data:
            metrics = campaign_data['metrics']
            doc_parts.append("Metrics:")
            for key, value in metrics.items():
                doc_parts.append(f"  - {key}: {value}")
        
        if 'revenue' in campaign_data:
            doc_parts.append(f"Revenue: ${campaign_data['revenue']}")
        
        if 'content_description' in campaign_data:
            doc_parts.append(f"Content: {campaign_data['content_description']}")
        
        if 'notes' in campaign_data:
            doc_parts.append(f"Notes: {campaign_data['notes']}")
        
        return "\n".join(doc_parts)
    
    def ingest_campaign(self, campaign_data: Dict[str, Any], campaign_id: str = None, 
                       namespace: str = "default") -> str:
        """
        Ingest a single campaign into Pinecone using upsert_records with namespace
        
        Args:
            campaign_data: Dictionary containing campaign information
            campaign_id: Unique identifier for the campaign (auto-generated if not provided)
            namespace: Namespace to store the campaign (default: "default", recommended: use quarter or creator)
        
        Returns:
            The campaign_id that was used
        """
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        # Generate campaign ID if not provided
        if not campaign_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            creator = campaign_data.get('creator', 'unknown').replace(' ', '_').replace('/', '_')
            brand = campaign_data.get('brand', 'unknown').replace(' ', '_').replace('/', '_')
            campaign_id = f"{creator}_{brand}_{timestamp}"
        
        # Prepare document text (this will be used for embedding)
        doc_text = self.prepare_campaign_document(campaign_data)
        
        # Prepare record for upsert_records
        # If index has integrated embeddings, we pass text; otherwise we generate embeddings
        record = {
            "_id": campaign_id,
            "content": doc_text,  # For integrated embeddings, this field is used
        }
        
        # Add all metadata fields (must be flat, no nested objects)
        if campaign_data.get('quarter'):
            record['quarter'] = campaign_data['quarter']
        if campaign_data.get('creator'):
            record['creator'] = campaign_data['creator']
        if campaign_data.get('brand'):
            record['brand'] = campaign_data['brand']
        if campaign_data.get('campaign_type'):
            record['campaign_type'] = campaign_data['campaign_type']
        if campaign_data.get('platform'):
            record['platform'] = campaign_data['platform']
        if campaign_data.get('date'):
            record['date'] = campaign_data['date']
        
        # Add metrics as separate fields (flattened)
        if 'metrics' in campaign_data:
            for key, value in campaign_data['metrics'].items():
                if value is not None:
                    record[f'metric_{key}'] = float(value) if isinstance(value, (int, float)) else str(value)
        
        if 'revenue' in campaign_data and campaign_data['revenue']:
            record['revenue'] = float(campaign_data['revenue'])
        
        # Upsert using upsert_records (new API with namespace support)
        try:
            self.index.upsert_records(namespace, [record])
            print(f"✓ Campaign '{campaign_id}' ingested to namespace '{namespace}'")
        except Exception as e:
            # Fallback: if index doesn't have integrated embeddings, use manual embeddings
            if "field_map" in str(e).lower() or "content" in str(e).lower():
                print(f"⚠️  Index may not have integrated embeddings. Using manual embeddings...")
                embedding = self.get_embedding(doc_text)
                
                # Prepare metadata for old API
                metadata = {k: v for k, v in record.items() if k not in ['_id', 'content']}
                
                self.index.upsert(vectors=[{
                    'id': campaign_id,
                    'values': embedding,
                    'metadata': metadata
                }])
                print(f"✓ Campaign '{campaign_id}' ingested (manual embeddings)")
            else:
                raise
        
        return campaign_id
    
    def ingest_bulk_campaigns(self, campaigns: List[Dict[str, Any]], 
                             namespace: str = "default",
                             batch_size: int = 96):
        """
        Ingest multiple campaigns in batches using upsert_records with namespace
        
        Args:
            campaigns: List of campaign data dictionaries
            namespace: Namespace to store campaigns (default: "default", recommended: use quarter)
            batch_size: Number of campaigns to process per batch (max 96 for text records)
        """
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        # Limit batch size for text records
        if batch_size > 96:
            batch_size = 96
            print(f"⚠️  Batch size limited to 96 (max for text records)")
        
        total = len(campaigns)
        print(f"Ingesting {total} campaigns to namespace '{namespace}' in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = campaigns[i:i+batch_size]
            records = []
            
            for idx, campaign in enumerate(batch):
                # Generate campaign ID
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # Include milliseconds
                creator = campaign.get('creator', 'unknown').replace(' ', '_').replace('/', '_')
                brand = campaign.get('brand', 'unknown').replace(' ', '_').replace('/', '_')
                campaign_id = f"{creator}_{brand}_{timestamp}_{idx}"
                
                # Prepare document text
                doc_text = self.prepare_campaign_document(campaign)
                
                # Prepare record
                record = {
                    "_id": campaign_id,
                    "content": doc_text,
                }
                
                # Add metadata fields (flat structure only)
                if campaign.get('quarter'):
                    record['quarter'] = campaign['quarter']
                if campaign.get('creator'):
                    record['creator'] = campaign['creator']
                if campaign.get('brand'):
                    record['brand'] = campaign['brand']
                if campaign.get('campaign_type'):
                    record['campaign_type'] = campaign['campaign_type']
                if campaign.get('platform'):
                    record['platform'] = campaign['platform']
                if campaign.get('date'):
                    record['date'] = campaign['date']
                
                # Add metrics
                if 'metrics' in campaign:
                    for key, value in campaign['metrics'].items():
                        if value is not None:
                            record[f'metric_{key}'] = float(value) if isinstance(value, (int, float)) else str(value)
                
                if 'revenue' in campaign and campaign['revenue']:
                    record['revenue'] = float(campaign['revenue'])
                
                records.append(record)
            
            # Upsert batch using upsert_records
            try:
                self.index.upsert_records(namespace, records)
                print(f"✓ Processed batch {i//batch_size + 1}/{(total-1)//batch_size + 1} ({len(records)} records)")
            except Exception as e:
                # Fallback to manual embeddings if needed
                if "field_map" in str(e).lower() or "content" in str(e).lower():
                    print(f"⚠️  Using manual embeddings for batch {i//batch_size + 1}...")
                    vectors = []
                    for record in records:
                        embedding = self.get_embedding(record['content'])
                        metadata = {k: v for k, v in record.items() if k not in ['_id', 'content']}
                        vectors.append({
                            'id': record['_id'],
                            'values': embedding,
                            'metadata': metadata
                        })
                    self.index.upsert(vectors=vectors)
                    print(f"✓ Processed batch {i//batch_size + 1} (manual embeddings)")
                else:
                    raise
            
            # Small delay to avoid rate limits
            if i + batch_size < total:
                time.sleep(0.1)
        
        print(f"✓ All {total} campaigns ingested successfully to namespace '{namespace}'!")
    
    def search(self, query_text: str, top_k: int = 10, 
              namespace: str = "default",
              filter_dict: Optional[Dict] = None,
              use_reranking: bool = True) -> List[Dict]:
        """
        Search the vector database using the new search() API with reranking
        
        Args:
            query_text: Natural language query
            top_k: Number of results to return
            namespace: Namespace to search in (default: "default")
            filter_dict: Optional metadata filters (e.g., {'quarter': '2024 Q1'})
            use_reranking: Whether to use reranking for better results (recommended)
        
        Returns:
            List of matching campaigns with scores
        """
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        # Build query parameters
        query_params = {
            "top_k": top_k * 2 if use_reranking else top_k,  # Get more candidates for reranking
            "inputs": {
                "text": query_text  # For integrated embeddings
            }
        }
        
        # Add filter if provided
        if filter_dict:
            query_params["filter"] = filter_dict
        
        # Build rerank parameters if enabled
        rerank_params = None
        if use_reranking:
            rerank_params = {
                "model": "bge-reranker-v2-m3",
                "top_n": top_k,
                "rank_fields": ["content"]
            }
        
        try:
            # Use search() method (new API)
            results = self.index.search(
                namespace=namespace,
                query=query_params,
                rerank=rerank_params
            )
            
            # Format results from new API structure
            formatted_results = []
            if 'result' in results and 'hits' in results['result']:
                for hit in results['result']['hits']:
                    formatted_results.append({
                        'id': hit.get('_id', ''),
                        'score': hit.get('_score', 0.0),
                        'metadata': hit.get('fields', {})
                    })
            else:
                # Fallback for different response structure
                for hit in results.get('hits', []):
                    formatted_results.append({
                        'id': hit.get('_id', ''),
                        'score': hit.get('_score', 0.0),
                        'metadata': hit.get('fields', {})
                    })
            
            return formatted_results
            
        except Exception as e:
            # Fallback to old query() API if search() fails
            if "search" in str(e).lower() or "query" in str(e).lower():
                print(f"⚠️  Using fallback query() method (index may not support new search API)")
                query_embedding = self.get_embedding(query_text)
                
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                    filter=filter_dict
                )
                
                formatted_results = []
                for match in results.get('matches', []):
                    formatted_results.append({
                        'id': match['id'],
                        'score': match['score'],
                        'metadata': match.get('metadata', {})
                    })
                
                return formatted_results
            else:
                raise
    
    def query(self, query_text: str, top_k: int = 10, filter_dict: Dict = None) -> List[Dict]:
        """
        Legacy query method - now calls search() for backward compatibility
        
        Args:
            query_text: Natural language query
            top_k: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            List of matching campaigns with scores
        """
        return self.search(query_text, top_k=top_k, filter_dict=filter_dict)
    
    def get_stats(self, namespace: str = None):
        """Get index statistics"""
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        stats = self.index.describe_index_stats()
        
        # If namespace specified, return stats for that namespace
        if namespace and hasattr(stats, 'namespaces'):
            if namespace in stats.namespaces:
                return {
                    'namespace': namespace,
                    'vector_count': stats.namespaces[namespace].vector_count,
                    'total_vector_count': stats.total_vector_count
                }
        
        return stats


def main():
    """Example usage"""
    print("=" * 60)
    print("ENT Agency Pinecone Vector Database Setup")
    print("=" * 60)
    print()
    
    # These should be set as environment variables
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("ERROR: Please set PINECONE_API_KEY and OPENAI_API_KEY environment variables")
        print()
        print("Example (PowerShell):")
        print("  $env:PINECONE_API_KEY='your-pinecone-key'")
        print("  $env:OPENAI_API_KEY='your-openai-key'")
        print()
        print("Example (Bash):")
        print("  export PINECONE_API_KEY='your-pinecone-key'")
        print("  export OPENAI_API_KEY='your-openai-key'")
        return
    
    # Initialize the vector database
    db = ENTAgencyVectorDB(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        index_name="ent-agency-campaigns"
    )
    
    # Check/connect to index
    try:
        db.create_index()
        
        print()
        print("✓ Connected to Pinecone index successfully!")
        print()
        print("📝 RECOMMENDED: For best performance, create index with integrated embeddings:")
        print("   pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 \\")
        print("     --model llama-text-embed-v2 --field_map text=content")
        print()
        print("Next steps:")
        print("1. Use the data_ingestion.py script to load your Google Sheets data")
        print("2. Use the query_interface.py script to search your campaigns")
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease create the index using the Pinecone CLI first.")


if __name__ == "__main__":
    main()
