import logging
from typing import List, Dict, Any
from django.conf import settings

from cloudinary import (
    uploader, 
    api, 
    config as clodunary_config
)

logger = logging.getLogger(__name__)

class CloudinaryImageManager:
    def __init__(self):
        clodunary_config(
            cloud_name=settings.CLOUDINARY_CLOUDE_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

    def upload(self, image_file, folder: str = "tourtoise") -> Dict[str, Any]:
        """
        Upload a single image to Cloudinary
        """
        try:
            result = uploader.upload(
                image_file,
                folder=folder,
                resource_type="image",
            )

            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"],
            }

        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise RuntimeError("Image upload failed") from e

    def bulk_upload(self, image_files: List, folder: str = "tourtoise") -> List[Dict[str, Any]]:
        """
        Upload multiple images to Cloudinary
        """
        results = []

        for image in image_files:
            results.append(self.upload(image, folder=folder))

        return results

    def delete(self, public_id: str) -> bool:
        """
        Delete a single image from Cloudinary
        """
        try:
            result = uploader.destroy(public_id)

            return result.get("result") == "ok"

        except Exception as e:
            logger.error("Cloudinary delete failed")
            raise RuntimeError("Image deletion failed") from e

    def bulk_delete(self, public_ids: List[str]) -> Dict[str, str]:
        """
        Delete multiple images from Cloudinary
        """
        try:
            result = api.delete_resources(public_ids)

            # returns dict: {public_id: "deleted"}
            return result.get("deleted", {})

        except Exception as e:
            logger.error("Cloudinary bulk delete failed")
            raise RuntimeError("Bulk image deletion failed") from e
