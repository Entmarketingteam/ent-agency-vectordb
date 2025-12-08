"""
Pinecone Vector Database Setup for ENT Agency Campaign Data
This script sets up a Pinecone index and provides methods to ingest and query campaign data
"""

import os
from typing import List, Dict, Any
import json
from datetime import datetime

try:
    from pinecone import Pinecone, ServerlessSpec
    import openai
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "pinecone", "openai", "--break-system-packages"])
    from pinecone import Pinecone, ServerlessSpec
    import openai


class ENTAgencyVectorDB:
    def __init__(self, pinecone_api_key: str, openai_api_key: str, index_name: str = "ent-agency-campaigns"):
        """
        Initialize the vector database
        
        Args:
            pinecone_api_key: Your Pinecone API key
            openai_api_key: Your OpenAI API key for embeddings
            index_name: Name of the Pinecone index to create/use
        """
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.index_name = index_name
        self.index = None
        
        # Embedding model configuration
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
    def create_index(self):
        """Create a new Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating new index: {self.index_name}")
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
        else:
            print(f"Index '{self.index_name}' already exists")
        
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
    
    def ingest_campaign(self, campaign_data: Dict[str, Any], campaign_id: str = None):
        """
        Ingest a single campaign into Pinecone
        
        Args:
            campaign_data: Dictionary containing campaign information
            campaign_id: Unique identifier for the campaign (auto-generated if not provided)
        """
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        # Generate campaign ID if not provided
        if not campaign_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            creator = campaign_data.get('creator', 'unknown').replace(' ', '_')
            campaign_id = f"{creator}_{timestamp}"
        
        # Prepare document text
        doc_text = self.prepare_campaign_document(campaign_data)
        
        # Generate embedding
        embedding = self.get_embedding(doc_text)
        
        # Prepare metadata (flatten for Pinecone)
        metadata = {
            'text': doc_text,
            'quarter': campaign_data.get('quarter', ''),
            'creator': campaign_data.get('creator', ''),
            'brand': campaign_data.get('brand', ''),
            'campaign_type': campaign_data.get('campaign_type', ''),
            'platform': campaign_data.get('platform', ''),
            'date': campaign_data.get('date', ''),
        }
        
        # Add metrics as separate metadata fields
        if 'metrics' in campaign_data:
            for key, value in campaign_data['metrics'].items():
                metadata[f'metric_{key}'] = value
        
        if 'revenue' in campaign_data:
            metadata['revenue'] = campaign_data['revenue']
        
        # Upsert to Pinecone
        self.index.upsert(vectors=[{
            'id': campaign_id,
            'values': embedding,
            'metadata': metadata
        }])
        
        print(f"Campaign '{campaign_id}' ingested successfully")
        return campaign_id
    
    def ingest_bulk_campaigns(self, campaigns: List[Dict[str, Any]], batch_size: int = 100):
        """
        Ingest multiple campaigns in batches
        
        Args:
            campaigns: List of campaign data dictionaries
            batch_size: Number of campaigns to process per batch
        """
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        total = len(campaigns)
        print(f"Ingesting {total} campaigns in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = campaigns[i:i+batch_size]
            vectors = []
            
            for idx, campaign in enumerate(batch):
                campaign_id = f"campaign_{i+idx}"
                doc_text = self.prepare_campaign_document(campaign)
                embedding = self.get_embedding(doc_text)
                
                metadata = {
                    'text': doc_text,
                    'quarter': campaign.get('quarter', ''),
                    'creator': campaign.get('creator', ''),
                    'brand': campaign.get('brand', ''),
                    'campaign_type': campaign.get('campaign_type', ''),
                    'platform': campaign.get('platform', ''),
                    'date': campaign.get('date', ''),
                }
                
                if 'metrics' in campaign:
                    for key, value in campaign['metrics'].items():
                        metadata[f'metric_{key}'] = value
                
                if 'revenue' in campaign:
                    metadata['revenue'] = campaign['revenue']
                
                vectors.append({
                    'id': campaign_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            self.index.upsert(vectors=vectors)
            print(f"Processed batch {i//batch_size + 1}/{(total-1)//batch_size + 1}")
        
        print(f"All {total} campaigns ingested successfully!")
    
    def query(self, query_text: str, top_k: int = 10, filter_dict: Dict = None) -> List[Dict]:
        """
        Query the vector database
        
        Args:
            query_text: Natural language query
            top_k: Number of results to return
            filter_dict: Optional metadata filters (e.g., {'quarter': '2024 Q1'})
        
        Returns:
            List of matching campaigns with scores
        """
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        # Generate query embedding
        query_embedding = self.get_embedding(query_text)
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        formatted_results = []
        for match in results['matches']:
            formatted_results.append({
                'id': match['id'],
                'score': match['score'],
                'metadata': match['metadata']
            })
        
        return formatted_results
    
    def get_stats(self):
        """Get index statistics"""
        if not self.index:
            raise Exception("Index not initialized. Call create_index() first.")
        
        stats = self.index.describe_index_stats()
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
        print("Example:")
        print("  export PINECONE_API_KEY='your-pinecone-key'")
        print("  export OPENAI_API_KEY='your-openai-key'")
        return
    
    # Initialize the vector database
    db = ENTAgencyVectorDB(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        index_name="ent-agency-campaigns"
    )
    
    # Create index
    db.create_index()
    
    print()
    print("✓ Pinecone index created successfully!")
    print()
    print("Next steps:")
    print("1. Use the data_ingestion.py script to load your Google Sheets data")
    print("2. Use the query_interface.py script to search your campaigns")
    print()


if __name__ == "__main__":
    main()
