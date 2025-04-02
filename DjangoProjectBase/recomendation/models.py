from django.db import models

class Recomendation(models.Model):
    prompt = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.prompt