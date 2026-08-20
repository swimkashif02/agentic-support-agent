import re
import sys, os
import json
from data.database import get_cached_result, save_to_cache
from rag.embeddings import get_embedding
from rag.vector_store import search_vectors
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def retrieve_faqs(query: str,
                  top_k: int = 3,
                  category: str = None,
                  score_threshold: float = 0.30) -> list[dict]:
    """
    Core retrieval function.
    Converts query text to a vector then searches Pinecone.
    Returns formatted list of matching FAQ dicts.
    """
 
    # Step 1: Convert the user query text into a vector
    # get_embedding() calls OpenAI embeddings API — returns 1536 floats
    query_vector = get_embedding(query)
 
    # Step 2: Search Pinecone with the query vector
    # search_vectors() finds stored FAQ vectors most similar to query_vector
    raw_results = search_vectors(
        query_vector=query_vector,
        top_k=top_k,
        score_threshold=score_threshold
    )
 
    # Step 3: Optional category filter
    # If agent knows the category (BILLING/TECHNICAL/ACCOUNT)
    # only return FAQs from that category
    # Step 3: Filter by category if provided
    # Removed — category filter was too strict and removed valid results
    # if category:
    #     raw_results = [
    #         r for r in raw_results
    #         if r["metadata"].get("category") == category
    #     ]
 
    # Step 4: Format results into clean dicts for the agent
    # Pinecone returns raw match objects — we extract only what we need
    formatted = []
    for result in raw_results:
        formatted.append({
            "id":       result["id"],
            "score":    round(result["score"], 3),
            "category": result["metadata"]["category"],
            "question": result["metadata"]["question"],
            "answer":   result["metadata"]["answer"],
        })
 
    return formatted

def rerank_results(results: list[dict],
                   query: str,
                   category: str = None) -> list[dict]:
    """
    Applies small boosts to improve result ordering.
    Called AFTER retrieve_faqs() returns initial results.
    Pinecone orders by cosine similarity — reranking adds
    domain-specific logic on top.
    """
    for result in results:
        boost = 0.0
 
        # BOOST 1: Category match (+0.05)
        # If agent knows this is a BILLING issue and FAQ is also BILLING
        # give it a small bump — same category = more likely relevant
        if category and result["category"] == category:
            boost += 0.05
 
        # BOOST 2: Word overlap (+0.01 per matching word)
        # If query words also appear in the FAQ question
        # give a tiny boost — combines semantic with keyword signal
        query_words = query.lower().split()
        question_lower = result["question"].lower()
        word_matches = sum(1 for w in query_words if w in question_lower)
        if word_matches > 0:
            boost += word_matches * 0.01
 
        # Store final score = Pinecone score + boost
        result["final_score"] = result["score"] + boost
 
    # Sort by final_score descending — best result first
    return sorted(results, key=lambda x: x["final_score"], reverse=True)

def multi_stage_retrieve(query: str,
                          category: str = None) -> list[dict]:
    """
    Two-stage retrieval:
    Stage 1: Ask Pinecone for top 10 with low threshold (wide net)
    Stage 2: Rerank those 10, return best 3
    Result: better top 3 than asking Pinecone for top 3 directly.
    """
 
    # STAGE 1: Broad search — low threshold, more candidates
    # We use score_threshold=0.30 to capture borderline matches
    # top_k=10 gives reranking more candidates to work with
    broad_results = retrieve_faqs(
        query=query,
        top_k=10,
        category=category,
        score_threshold=0.30
    )
 
    # If nothing found even with broad search — return empty
    # Agent will escalate (system prompt rule: no results = escalate)
    if not broad_results:
        return []
 
    # STAGE 2: Rerank the 10 candidates
    reranked = rerank_results(broad_results, query, category)
 
    # Return only the top 3 after reranking
    # These are better than the top 3 Pinecone would give directly
    return reranked[:3]

# Rule-based query rewriter
# Maps common customer phrasings to optimised search terms
# The rewrite terms are chosen to be closer to FAQ question language
QUERY_REWRITES = {
    # Login related
    r"cannot (log|sign) in":                              "app crashes login",
    r"login (button|page) (not working|broken|does nothing)": "app crashes login",
    r"stuck on login":                                    "app crashes login",
    r"cannot get into (my )?account":                    "app crashes login",
    r"login.*nothing":                                    "app crashes login",
 
    # Billing related
    r"charged (twice|double|2x|two times)": "double charge invoice",
    r"extra charge":                         "double charge invoice",
    r"billed (twice|double)":                "double charge invoice",
 
    # Account related
    r"change (my )?(email|mail)":    "change account email",
    r"update (my )?email":           "change account email",
    r"new email address":            "change account email",
 
    # Password related
    r"(forgot|lost|reset) password":              "password reset email",
    r"password (not working|expired|forgotten)":  "password reset email",
}
 
 
def rewrite_query(query: str) -> str:
    """
    Check if query matches any rewrite rule.
    If yes: return the optimised search term.
    If no:  return original query unchanged.
    """
    query_lower = query.lower()
 
    for pattern, rewrite in QUERY_REWRITES.items():
        if re.search(pattern, query_lower):
            # Print so you can see rewrites happening during testing
            print(f"  [REWRITE] '{query}' → '{rewrite}'")
            return rewrite
 
    # No rule matched — use original query as-is
    return query


# Update retrieve_with_rewrite() to check cache first:
def retrieve_with_rewrite(query: str, category: str = None) -> list[dict]:
    """Full retrieval pipeline with SQLite caching."""
 
    # Step 1: Check cache first
    cache_key = f"{query}|{category}"
    cached = get_cached_result(cache_key)
    if cached is not None:
        return cached
 
    # Step 2: Not in cache — run full pipeline
    rewritten_query = rewrite_query(query)
    result = multi_stage_retrieve(rewritten_query, category)
 
    # Step 3: Store in cache for next time
    save_to_cache(cache_key, result)
 
    return result

# ── Test retrieval — run with: py -m rag.retriever ──────
if __name__ == "__main__":
 
    print("=" * 60)
    print("  RETRIEVER TEST — with debug output")
    print("=" * 60)
 
    test_queries = [
        "the login button does nothing",      # Was Week 1 failure
        "I cannot get into my account",       # Was Week 1 failure
        "charged twice this month",           # Was Week 1 failure
        "quantum flux capacitor is broken",   # Should still escalate
        "how do I cancel my subscription",    # Should match faq-009
        "forgot my password",                 # Should match faq-002
    ]
 
    for query in test_queries:
        print(f"\n{'─'*60}")
        print(f"  Original query : {query}")
 
        # Step 1: Show what the query rewrites to
        from rag.retriever import rewrite_query
        # Show what the query rewrites to — suppress the print inside rewrite_query
        rewritten = query.lower()
        for pattern, rw in QUERY_REWRITES.items():
            if re.search(pattern, rewritten):
                rewritten = rw
                print(f"  Rewritten to   : {rewritten}")
                break
        else:
            rewritten = query
            print(f"  No rewrite     : using original query")
 
        # Step 2: Show raw Pinecone scores BEFORE threshold filter
        from rag.embeddings import get_embedding
        from rag.vector_store import index, NAMESPACE
        query_vector = get_embedding(rewritten)
        raw = index.query(
            vector=query_vector,
            top_k=5,
            namespace=NAMESPACE,
            include_metadata=True
        )
        print(f"  Raw Pinecone scores (top 5):")
        for m in raw.matches:
            print(f"    {m.score:.4f} | {m.metadata.get('question', 'N/A')}")
 
        # Step 3: Show final results after full pipeline
        results = retrieve_with_rewrite(query)
        print(f"  Final results after pipeline:")
        if results:
            for r in results:
                print(f"    Score {r['score']} | {r['question']}")
        else:
            print(f"    No matches — agent will escalate")
