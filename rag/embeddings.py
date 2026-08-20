import os
from dotenv import load_dotenv
from openai import OpenAI
 
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions, cheap, high quality
EMBEDDING_DIMENSION = 1536                  # must match Pinecone index dimension
 
 
def get_embedding(text: str) -> list[float]:
    """
    Convert a single text string into a vector.
    Returns a list of 1536 floating point numbers.
    """
    # Clean the text — remove newlines which can affect embedding quality
    text = text.replace("\n", " ").strip()
 
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
 
    # response.data is a list — we take the first (and only) embedding
    return response.data[0].embedding
 
 
def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple texts to vectors in one API call.
    More efficient than calling get_embedding() in a loop.
    Used during ingestion to embed all FAQs at once.
    """
    texts = [t.replace("\n", " ").strip() for t in texts]
 
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts    # pass a list — OpenAI handles all at once
    )
 
    # Sort by index to maintain original order
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

def chunk_faq_entry(faq: dict) -> dict:
    """
    Convert a single FAQ entry into a chunk ready for embedding.
    We combine question and answer into one text for richer embeddings.
    """
    # Combine question and answer — both contribute to the meaning
    combined_text = f"Question: {faq['question']}\nAnswer: {faq['answer']}"
 
    return {
        "id":       faq["id"],          # unique ID for Pinecone
        "text":     combined_text,       # text to embed
        "metadata": {                    # stored alongside vector in Pinecone
            "id":       faq["id"],
            "category": faq["category"],
            "question": faq["question"],
            "answer":   faq["answer"],
        }
    }
 
 
def chunk_all_faqs(faq_database: list[dict]) -> list[dict]:
    """
    Chunk all FAQs in the database.
    Returns a list of chunks ready for embedding and ingestion.
    """
    return [chunk_faq_entry(faq) for faq in faq_database]

# ── Test it ─────────────────────────────────────────────
if __name__ == "__main__":
    text = "App crashes on login"
    embedding = get_embedding(text)
 
    print(f"Text: {text}")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Type: {type(embedding[0])}")
