# Pinecone API Updates - Latest Patterns

This document summarizes the updates made to align with the latest Pinecone best practices.

## Key Changes

### 1. **Namespaces for Data Isolation**
- All data operations now use namespaces (default: "default")
- Namespaces are automatically determined from quarter (e.g., "2024_q4")
- Better data isolation and organization

### 2. **New `upsert_records()` API**
- Replaced `upsert()` with `upsert_records()` for text-based records
- Supports integrated embeddings (llama-text-embed-v2)
- Batch size limited to 96 records (max for text records)
- Automatic fallback to manual embeddings if index doesn't support integrated embeddings

### 3. **New `search()` API with Reranking**
- Replaced `query()` with `search()` method
- Always uses reranking by default (bge-reranker-v2-m3)
- Better search relevance and accuracy
- Backward compatibility: `query()` method still available but calls `search()`

### 4. **Index Creation Best Practices**
- Index creation now recommends using Pinecone CLI
- CLI command for integrated embeddings:
  ```bash
  pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 \
    --model llama-text-embed-v2 --field_map text=content
  ```
- Programmatic creation still available but not recommended for production

## Updated Files

### `pinecone_setup.py`
- ✅ Updated `create_index()` to recommend CLI usage
- ✅ Updated `ingest_campaign()` to use `upsert_records()` with namespaces
- ✅ Updated `ingest_bulk_campaigns()` to use `upsert_records()` with namespaces
- ✅ Added new `search()` method with reranking
- ✅ Kept `query()` for backward compatibility
- ✅ Updated `get_stats()` to support namespace filtering

### `data_ingestion.py`
- ✅ Updated to use namespaces (auto-determined from quarter)
- ✅ Calls updated `ingest_bulk_campaigns()` with namespace parameter
- ✅ Added namespace parameter to `ingest_from_google_sheets()`

### `query_interface.py`
- ✅ Updated all search methods to use new `search()` API
- ✅ Added namespace support throughout
- ✅ All searches now use reranking by default
- ✅ Updated result formatting to handle new API response structure

## Migration Guide

### For Existing Users

1. **Recreate Index (Recommended)**
   ```bash
   # Delete old index (if needed)
   pc index delete -n ent-agency-campaigns
   
   # Create new index with integrated embeddings
   pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 \
     --model llama-text-embed-v2 --field_map text=content
   ```

2. **Re-ingest Data**
   ```bash
   python data_ingestion.py
   ```
   Data will now be stored in namespaces (by quarter)

3. **Update Queries**
   - All existing queries will work (backward compatible)
   - New queries automatically use reranking for better results
   - Specify namespace if needed: `search(query, namespace="2024_q4")`

### For New Users

1. **Create Index with CLI** (recommended):
   ```bash
   pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 \
     --model llama-text-embed-v2 --field_map text=content
   ```

2. **Ingest Data**:
   ```bash
   python data_ingestion.py
   ```

3. **Query Data**:
   ```bash
   python query_interface.py
   ```

## Benefits

1. **Better Performance**: Integrated embeddings are faster and more efficient
2. **Better Search Quality**: Reranking improves relevance of search results
3. **Data Isolation**: Namespaces allow better organization and multi-tenant support
4. **Future-Proof**: Aligned with Pinecone's latest best practices
5. **Backward Compatible**: Old code still works, but new features are available

## API Changes Summary

| Old API | New API | Notes |
|---------|---------|-------|
| `index.upsert(vectors=[...])` | `index.upsert_records(namespace, records)` | Namespace required, text-based records |
| `index.query(vector=..., top_k=...)` | `index.search(namespace, query={...}, rerank={...})` | Reranking included, namespace required |
| Manual embeddings | Integrated embeddings (llama-text-embed-v2) | Recommended via CLI |

## Notes

- The code includes automatic fallback to old APIs if the index doesn't support new features
- OpenAI embeddings are still used as fallback if integrated embeddings aren't available
- All changes are backward compatible - existing code will continue to work

## Next Steps

1. ✅ Code updated to latest patterns
2. ⏭️ Test with your Pinecone account
3. ⏭️ Recreate index with integrated embeddings (recommended)
4. ⏭️ Re-ingest your data
5. ⏭️ Enjoy better search quality!


