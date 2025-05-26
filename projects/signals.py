from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from projects.models import Project
from base.models import VectorizedContent

from base.helpers.vectorize import VectorService
from base.choices import CollectionChoices

import logging

logger = logging.getLogger(__name__)

# Initialize vector service
vector_service = VectorService()


# Project Signals
@receiver(post_save, sender=Project)
def update_project_vector(sender, instance, created, **kwargs):
    """Update vector database when a project is created or updated"""
    try:
        transaction.on_commit(lambda: _update_project_vector_async(instance, created))
    except Exception as e:
        logger.error(f"Error in project vector update signal: {e}")

def _update_project_vector_async(instance, created):
    """Async function to update project vector"""
    try:
        # Prepare content for vectorization
        content = f"{instance.description}"
        
        # Add technologies if available
        if hasattr(instance, 'tech_stacks') and instance.tech_stacks:
            if isinstance(instance.tech_stacks, list):
                tech_str = ', '.join(instance.tech_stacks)
            else:
                tech_str = str(instance.tech_stacks)
            content += f" Technologies: {tech_str}"
        
        # Add URLs if available
        url_info = []
        if hasattr(instance, 'github_url') and instance.github_url:
            url_info.append(f"GitHub: {instance.github_url}")
        if hasattr(instance, 'live_url') and instance.live_url:
            url_info.append(f"Live Link: {instance.live_url}")
        
        if url_info:
            content += f" Links: {', '.join(url_info)}"
        
        # Prepare metadata
        metadata = {
            'id': instance.id,
            'technologies': getattr(instance, 'technologies', []),
            'github_url': getattr(instance, 'github_url', ''),
            'live_url': getattr(instance, 'live_url', ''),
            'model_type': 'project'
        }
        
        # Create or update vector entry
        vector_service.create_or_update_vector(
            collection_type=CollectionChoices.PROJECT,
            title=instance.name,
            content=content,
            metadata=metadata
        )
        
        action = "created" if created else "updated"
        logger.info(f"Vector entry {action} for project: {instance.name}")
        
    except Exception as e:
        logger.error(f"Error updating project vector for {instance.name}: {e}")

@receiver(post_delete, sender=Project)
def delete_project_vector(sender, instance, **kwargs):
    """Delete vector entry when a project is deleted"""
    try:
        VectorizedContent.objects.filter(
            collection_type=CollectionChoices.PROJECT,
            metadata__id=instance.id
        ).delete()
        
        logger.info(f"Vector entry deleted for project: {instance.name}")
        
    except Exception as e:
        logger.error(f"Error deleting project vector for {instance.name}: {e}")
