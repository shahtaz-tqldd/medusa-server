from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from services.models import Skills, Services
from base.models import VectorizedContent

from base.helpers.vectorize import VectorService
from base.choices import CollectionChoices

import logging

logger = logging.getLogger(__name__)

# Initialize vector service
vector_service = VectorService()

# Skill Signals
@receiver(post_save, sender=Skills)
def update_skill_vector(sender, instance, created, **kwargs):
    """Update vector database when a skill is created or updated"""
    try:
        # Use transaction.on_commit to ensure the database transaction is complete
        transaction.on_commit(lambda: _update_skill_vector_async(instance, created))
    except Exception as e:
        logger.error(f"Error in skill vector update signal: {e}")

def _update_skill_vector_async(instance, created):
    """Async function to update skill vector"""
    try:
        # Prepare content for vectorization
        content = f"{instance.description}"
        if hasattr(instance, 'proficiency_level') and instance.proficiency_level:
            content += f" Proficiency: {instance.proficiency_level}"
        
        # Prepare metadata
        metadata = {
            'id': instance.id,
            'proficiency_level': getattr(instance, 'proficiency_level', ''),
            'model_type': 'skill'
        }
        
        # Create or update vector entry
        vector_service.create_or_update_vector(
            collection_type=CollectionChoices.SKILLS,
            title=instance.name,
            content=content,
            metadata=metadata
        )
        
        action = "created" if created else "updated"
        logger.info(f"Vector entry {action} for skill: {instance.name}")
        
    except Exception as e:
        logger.error(f"Error updating skill vector for {instance.name}: {e}")

@receiver(post_delete, sender=Skills)
def delete_skill_vector(sender, instance, **kwargs):
    """Delete vector entry when a skill is deleted"""
    try:
        VectorizedContent.objects.filter(
            collection_type=CollectionChoices.SKILLS,
            metadata__id=instance.id
        ).delete()
        
        logger.info(f"Vector entry deleted for skill: {instance.name}")
        
    except Exception as e:
        logger.error(f"Error deleting skill vector for {instance.name}: {e}")

# Service Signals
@receiver(post_save, sender=Services)
def update_service_vector(sender, instance, created, **kwargs):
    """Update vector database when a service is created or updated"""
    try:
        transaction.on_commit(lambda: _update_service_vector_async(instance, created))
    except Exception as e:
        logger.error(f"Error in service vector update signal: {e}")

def _update_service_vector_async(instance, created):
    """Async function to update service vector"""
    try:
        # Prepare content for vectorization
        content = f"{instance.description}"
        
        # Prepare metadata
        metadata = {
            'id': instance.id,
            'model_type': 'service'
        }
        
        # Create or update vector entry
        vector_service.create_or_update_vector(
            collection_type=CollectionChoices.SERVICES,
            title=instance.name,
            content=content,
            metadata=metadata
        )
        
        action = "created" if created else "updated"
        logger.info(f"Vector entry {action} for service: {instance.name}")
        
    except Exception as e:
        logger.error(f"Error updating service vector for {instance.name}: {e}")

@receiver(post_delete, sender=Services)
def delete_service_vector(sender, instance, **kwargs):
    """Delete vector entry when a service is deleted"""
    try:
        VectorizedContent.objects.filter(
            collection_type=CollectionChoices.SERVICES,
            metadata__id=instance.id
        ).delete()
        
        logger.info(f"Vector entry deleted for service: {instance.name}")
        
    except Exception as e:
        logger.error(f"Error deleting service vector for {instance.name}: {e}")



