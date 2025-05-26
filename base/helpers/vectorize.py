from django.conf import settings
from typing import List, Dict

# models
from base.models import VectorizedContent
from services.models import Services, Skills
from projects.models import Project

# helpers
from base.choices import CollectionChoices
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
        
        queryset = VectorizedContent.objects.all()
        if collection_type:
            queryset = queryset.filter(collection_type=collection_type)
        
        # Using cosine similarity
        results = queryset.extra(
            select={
                'similarity': '1 - (embedding <=> %s)'
            },
            select_params=[query_embedding],
        ).order_by('-similarity')[:limit]
        
        return list(results)
    
    def update_embeddings_for_collection(self, collection_type: str):
        """Update embeddings for all items in a collection"""
        if collection_type == CollectionChoices.SKILLS:
            items = Skills.objects.all()
            for item in items:
                self.create_or_update_vector(
                    collection_type=CollectionChoices.SKILLS,
                    title=item.name,
                    content=f"{item.description} Proficiency: {item.proficiency_level}",
                    metadata={'id': item.id, 'proficiency': item.proficiency_level}
                )
        
        elif collection_type == CollectionChoices.SERVICES:
            items = Services.objects.all()
            for item in items:
                self.create_or_update_vector(
                    collection_type=CollectionChoices.SERVICES,
                    title=item.name,
                    content=f"{item.description}",
                    metadata={'id': item.id}
                )
        
        elif collection_type == CollectionChoices.PROJECT:
            items = Project.objects.all()
            for item in items:
                tech_str = ', '.join(item.tech_stacks) if item.tech_stacks else ''
                self.create_or_update_vector(
                    collection_type=CollectionChoices.PROJECT,
                    title=item.name,
                    content=f"{item.description} Technologies: {tech_str}",
                    metadata={'id': item.id, 'technologies': item.tech_stacks, 'live_url': item.live_url}
                )
    
    def create_or_update_vector(self, collection_type: str, title: str, content: str, metadata: Dict = None):
        """Create or update vector entry"""
        # Check if entry exists
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
