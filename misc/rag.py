import os
import anthropic
from sentence_transformers import SentenceTransformer, util

DOCUMENTS = [
    {"id": 1, "content": "Python is a popular programming language for AI."},
    {"id": 2, "content": "Marcel is the CEO of Anthropic."},
    {"id": 3, "content": "George is the CTO of Anthropic."},
]

model = SentenceTransformer('all-MiniLM-L6-v2')
DOCUMENT_EMBEDDINGS = [model.encode(doc["content"]) for doc in DOCUMENTS]


def retrieve(query, top_k=2):
    query_embedding = model.encode(query)
    scores = [util.cos_sim(query_embedding, doc_emb)[0][0].item() for doc_emb in DOCUMENT_EMBEDDINGS]
    ranked_docs = sorted(zip(DOCUMENTS, scores), key=lambda x: x[1], reverse=True)
    print([doc for doc, score in ranked_docs[:top_k]])
    return [doc for doc, score in ranked_docs[:top_k]]

def generate_prompt(query, retrieved_docs):
    context = "\n".join([f"Document {doc['id']}: {doc['content']}" for doc in retrieved_docs])
    prompt = (
        f"You are an AI assistant. Use the following documents to answer the user's question.\n"
        f"{context}\n"
        f"User question: {query}\n"
        f"Answer:"
    )
    return prompt

def rag_assistant(query):
    retrieved_docs = retrieve(query)
    prompt = generate_prompt(query, retrieved_docs)
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

if __name__ == "__main__":
    print("Welcome to the RAG AI Assistant!")
    print("Type 'exit' to quit.")

    while True:
        user_query = input("Ask a question: ")
        if user_query.lower() == 'exit':
            break
        answer = rag_assistant(user_query)
        print("AI Assistant:", answer)