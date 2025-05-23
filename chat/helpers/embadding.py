from google import genai
from typing import List

# Assuming you have your data structured like this (or from a CSV/DB)
portfolio_data = [
    {"type": "project", "name": "Project 1", "description": "Developed a full-stack e-commerce platform using Django, React, and PostgreSQL. Features include user authentication, product catalog, shopping cart, and payment gateway integration with Stripe. Achieved 20% increase in conversion rate.", "tags": ["Django", "React", "E-commerce"]},
    {"type": "project", "name": "Project 2", "description": "Built a real-time data analytics dashboard with Flask, Vue.js, and Redis. Visualizes sensor data from IoT devices. Implemented secure API endpoints and optimized data fetching for low latency.", "tags": ["Flask", "Vue.js", "IoT"]},
    {"type": "skill", "name": "Python", "description": "Expert in Python for web development (Django, Flask), scripting, and data processing.", "tags": ["Language"]},
    {"type": "skill", "name": "AWS", "description": "Proficient in AWS services including EC2, S3, RDS, Lambda, and API Gateway for deploying scalable cloud solutions.", "tags": ["Cloud"]},
    {"type": "onboarding_step", "name": "Discovery Call", "description": "The first step is a free 30-minute discovery call to understand your project vision, goals, and initial requirements.", "tags": ["Onboarding"]},
    {"type": "onboarding_step", "name": "Proposal & Estimate", "description": "Based on detailed requirements, a comprehensive proposal outlining scope, timeline, and cost will be provided.", "tags": ["Onboarding"]},
    # ... add all your detailed data here
]

# Initialize embedding model (one-time)
embedding_model = genai.get_embedding_model("text-embedding-004")

# This is where you'd connect to your vector database and insert embeddings
# For demonstration, let's just create a list of embeddings
embedded_chunks = []
for item in portfolio_data:
    text_to_embed = f"{item['type']}: {item['name']}. {item['description']}"
    embedding = embedding_model.embed_content(model="text-embedding-004", content=text_to_embed)
    embedded_chunks.append({"text": text_to_embed, "embedding": embedding['embedding'], "tags": item['tags']})

# In a real app, you'd insert embedded_chunks into a vector DB like Pinecone, ChromaDB, etc.
# For now, let's simulate a "search" function
def simulated_vector_search(query_embedding: List[float], top_k: int = 3) -> List[str]:
    # In a real vector DB, this would be an efficient similarity search
    # Here, we'll just do a very basic dot product similarity for demonstration
    similarities = []
    for chunk in embedded_chunks:
        # Simple dot product similarity (for demonstration only)
        sim = sum(q * c for q, c in zip(query_embedding, chunk['embedding']))
        similarities.append((sim, chunk['text']))

    similarities.sort(key=lambda x: x[0], reverse=True)
    return [text for sim, text in similarities[:top_k]]