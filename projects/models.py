from django.db import models

class Projects(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=80) 
    features = models.TextField()
    live_url = models.TextField()
    github_url = models.TextField()

    created_at = models.DateTimeField()
    
    def __str__(self):
        return self.name