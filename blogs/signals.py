from django.db.models.signals import pre_delete
from django.dispatch import receiver
from blogs.models import ImageBlock
from base.managers.cloudinary import CloudinaryImageManager
import logging

logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=ImageBlock)
def delete_cloudinary_image(sender, instance, **kwargs):
    """Delete image from Cloudinary when ImageBlock is deleted"""
    if instance.cloudinary_public_id:
        try:
            cloudinary_manager = CloudinaryImageManager()
            cloudinary_manager.delete(instance.cloudinary_public_id)
            logger.info(f"Deleted Cloudinary image: {instance.cloudinary_public_id}")
        
        except Exception as e:
            logger.error(f"Failed to delete Cloudinary image: {str(e)}")