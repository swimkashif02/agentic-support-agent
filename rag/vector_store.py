import os
from dotenv import load_dotenv
from pinecone import Pinecone
 
load_dotenv()
 
# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
 
# Connect to our index
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
 
NAMESPACE = "faqs"   # partition for FAQ vectors within the index
 
 
def upsert_vectors(vectors: list[dict]) -> dict:
    """
    Upload vectors to Pinecone.
    vectors = list of dicts with id, values, and metadata.
    """
    return index.upsert(vectors=vectors, namespace=NAMESPACE)
 
 
def search_vectors(query_vector: list[float],
                   top_k: int = 3,
                   score_threshold: float = 0.70) -> list[dict]:
    """
    Search Pinecone for vectors similar to query_vector.
    Returns top_k results above score_threshold.
    """
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=NAMESPACE,
        include_metadata=True   # return FAQ text alongside vectors
    )
 
    # Filter out results below score threshold
    matches = [
        {
            "id":       match.id,
            "score":    match.score,
            "metadata": match.metadata
        }
        for match in results.matches
        if match.score >= score_threshold
    ]
 
    return matches
 
 
def get_index_stats() -> dict:
    """Return stats about our Pinecone index — useful for debugging."""
    return index.describe_index_stats()
 
 
# ── Test connection ─────────────────────────────────────
if __name__ == "__main__":
    stats = get_index_stats()
    print(f"Index stats: {stats}")
    print(f"Total vectors: {stats.total_vector_count}")
