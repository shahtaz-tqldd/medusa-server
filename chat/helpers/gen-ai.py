from google import genai
from google.generativeai import types
from django.conf import settings
from typing import List, Dict

# --- RAG Specific Imports and Setup (Conceptual) ---
# In a real scenario, you'd initialize your vector DB client here
# e.g., from pinecone import Pinecone; pinecone = Pinecone(api_key="YOUR_API_KEY")
# or from chromadb import Client; chroma_client = Client()

# Initialize the embedding model (can be done once)
embedding_model_name = "text-embedding-004" # Use the latest stable embedding model

class AIModelTesting:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_TOKEN)
        self.generation_model = "gemini-1.5-flash" # Your chosen generation model
        self.embedding_model = genai.get_embedding_model(embedding_model_name)

        # --- IMPORTANT: In a real RAG setup, you'd initialize your vector database client here ---
        # self.vector_db_client = initialize_your_vector_database_client()
        # For this example, we'll use the simulated_vector_search function defined above.

    def _retrieve_relevant_context(self, query: str) -> List[str]:
        """
        Generates an embedding for the query and retrieves relevant text chunks
        from your knowledge base using a vector similarity search.
        """
        # 1. Embed the user query
        query_embedding_response = self.embedding_model.embed_content(
            model=embedding_model_name,
            content=query
        )
        query_embedding = query_embedding_response['embedding']

        # 2. Perform similarity search in your vector database
        # This is where you'd call your vector DB's search method
        # For example:
        # retrieved_chunks = self.vector_db_client.query(query_embedding, top_k=3)
        # return [chunk.text for chunk in retrieved_chunks]

        # --- Using the simulated search for demonstration ---
        retrieved_chunks = simulated_vector_search(query_embedding, top_k=3)
        return retrieved_chunks

    def gemini_response(self, user_query: str) -> str:
        print("----------------------------")
        print(f"User Query: {user_query}")

        # 1. Retrieve relevant context based on the user's query
        relevant_context = self._retrieve_relevant_context(user_query)

        # 2. Construct the dynamic system instruction with retrieved context
        # This is the "magic" of RAG – only relevant data is included!
        dynamic_system_instruction = f"""
            You are Era, Shahtaz's AI assistant for his software development portfolio website. Your primary goals are:
            1. **Answer visitor queries about Shahtaz's projects, skills, and expertise.** based *only* on the provided context.
            2. **Guide visitors interested in software development projects to become clients.** Explain the onboarding process clearly and encourage them to take the next step.
            3. **Maintain a professional, helpful, and positive tone.**
            4. **Never guess or use external knowledge. If unsure, politely suggest connecting with Shahtaz.**
            5. **When appropriate, end with a subtle call to action.**

            ---
            **Relevant Context (BEGIN)**
            {'\n'.join(relevant_context)}
            **Relevant Context (END)**
            """

        # 3. Create the GenerateContentConfig with the dynamic system instruction
        generation_config = types.GenerateContentConfig(
            system_instruction=dynamic_system_instruction
        )

        # 4. Generate the content
        response = self.gemini_client.models.generate_content(
            model=self.generation_model,
            contents=user_query, # The user's query is the direct content
            config=generation_config,
        )

        return response.text

# --- How to use it ---
# You would need to have your vector database populated first.
# ai_tester = AIModelTesting()
# user_question = "Tell me about your e-commerce project and how I can start a project with you."
# response = ai_tester.gemini_response(user_question)
# print(response)