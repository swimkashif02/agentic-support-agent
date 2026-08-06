# Run this script ONCE to populate Pinecone with FAQ vectors.
# Run again whenever FAQs are updated.
 
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from tools.search_tool import FAQ_DATABASE
from rag.embeddings import chunk_all_faqs, get_embeddings_batch
from rag.vector_store import upsert_vectors, get_index_stats
 
 
def ingest_faqs():
    """
    Full ingestion pipeline:
    1. Chunk all FAQs
    2. Embed all chunks in one batch API call
    3. Upload vectors + metadata to Pinecone
    4. Verify upload was successful
    """
 
    print("="*50)
    print("  FAQ INGESTION PIPELINE")
    print("="*50)
 
    # ── STEP 1: Chunk ────────────────────────────────
    print(f"\nStep 1: Chunking {len(FAQ_DATABASE)} FAQs...")
    chunks = chunk_all_faqs(FAQ_DATABASE)
    print(f"  Created {len(chunks)} chunks")
 
    # ── STEP 2: Embed ────────────────────────────────
    print(f"\nStep 2: Generating embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = get_embeddings_batch(texts)
    print(f"  Generated {len(embeddings)} embeddings")
    print(f"  Each embedding: {len(embeddings[0])} dimensions")
 
    # ── STEP 3: Prepare vectors for Pinecone ─────────
    print(f"\nStep 3: Preparing vectors...")
    vectors = []
    for chunk, embedding in zip(chunks, embeddings):
        vectors.append({
            "id":       chunk["id"],        # faq-001, faq-002, etc.
            "values":   embedding,           # list of 1536 floats
            "metadata": chunk["metadata"]   # question, answer, category
        })
    print(f"  Prepared {len(vectors)} vectors")
 
    # ── STEP 4: Upload to Pinecone ────────────────────
    print(f"\nStep 4: Uploading to Pinecone...")
    result = upsert_vectors(vectors)
    print(f"  Upload result: {result}")
 
    # ── STEP 5: Verify ───────────────────────────────
    print(f"\nStep 5: Verifying...")
    stats = get_index_stats()
    print(f"  Total vectors in Pinecone: {stats.total_vector_count}")
 
    print(f"\n✅ Ingestion complete! {len(vectors)} FAQs in Pinecone.")
    print("="*50)
 
 
if __name__ == "__main__":
    ingest_faqs()
