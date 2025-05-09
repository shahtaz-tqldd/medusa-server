from django.db import models

class Blogs(models.Model):
    name = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=80)
    created_at = models.DateTimeField()
    
    def __str__(self):
        return self.name