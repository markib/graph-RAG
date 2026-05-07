#!/usr/bin/env python
"""
Ingest sample documents into Neo4j via the Graph RAG backend.
"""
import asyncio
import json
from extract import process_file
import httpx

async def ingest_file(file_path: str):
    """Extract entities from file and ingest into backend."""
    print(f"\n{'='*60}")
    print(f"📄 Processing: {file_path}")
    print(f"{'='*60}")
    
    try:
        # 1️⃣ Extract entities & relationships from document
        data = await process_file(file_path)
        
        print(f"\n✓ Extracted {len(data.get('entities', []))} entities and {len(data.get('relationships', []))} relationships")
        
        # 2️⃣ Send to backend /ingest endpoint
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                'http://localhost:8000/ingest',
                json=data
            )
            result = response.json()
            print(f"✓ Ingested: {result}")
            return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ingest all sample documents."""
    print("\n🚀 Starting Graph RAG Ingestion Pipeline\n")
    
    files = [
        'documents/doc1.txt',
        'documents/doc2.txt',
    ]
    
    results = []
    for file_path in files:
        success = await ingest_file(file_path)
        results.append((file_path, success))
    
    print(f"\n{'='*60}")
    print("📊 Summary:")
    print(f"{'='*60}")
    for file_path, success in results:
        status = "✓ OK" if success else "❌ FAILED"
        print(f"{status} - {file_path}")
    
    print(f"\n✅ Ingestion complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
