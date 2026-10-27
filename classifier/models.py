from django.db import models

class PlantImage(models.Model):
    image = models.ImageField(upload_to='plant_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prediction = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Plant Image {self.id} - {self.prediction}"
