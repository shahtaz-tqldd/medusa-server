from django.conf import settings
from typing import List, Dict

# models
from base.models import VectorizedContent

# helpers
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def create_vector_entry(self, collection_type: str, title: str, content: str, metadata: Dict = None) -> VectorizedContent:
        """Create a new vector entry"""
        if metadata is None:
            metadata = {}
        
        embedding = self.generate_embedding(f"{title} {content}")
        
        vector_entry = VectorizedContent.objects.create(
            collection_type=collection_type,
            title=title,
            content=content,
            metadata=metadata,
            embedding=embedding
        )
        return vector_entry
    
    def similarity_search(self, query: str, collection_type: str = None, limit: int = 5) -> List[VectorizedContent]:
        """Perform similarity search"""
        query_embedding = self.generate_embedding(query)
        
        # Convert the query_embedding list to a PostgreSQL vector string
        vector_string = f"[{','.join(map(str, query_embedding))}]"
        
        queryset = VectorizedContent.objects.all()
        if collection_type:
            queryset = queryset.filter(collection_type=collection_type)
        
        # Using raw SQL to handle the vector comparison
        results = queryset.extra(
            select={'similarity': '1 - (embedding <=> %s::vector)'},
            select_params=[vector_string],
        ).order_by('-similarity')[:limit]
        
        return list(results)
    
    def create_or_update_vector(self, collection_type: str, title: str, content: str, metadata: Dict = None):
        """Create or update vector entry"""
        existing = VectorizedContent.objects.filter(
            collection_type=collection_type,
            title=title
        ).first()
        
        embedding = self.generate_embedding(f"{title} {content}")
        
        if existing:
            existing.content = content
            existing.metadata = metadata or {}
            existing.embedding = embedding
            existing.save()
            return existing
        else:
            return self.create_vector_entry(collection_type, title, content, metadata)
        