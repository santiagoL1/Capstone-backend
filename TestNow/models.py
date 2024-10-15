from django.db import models

class FlashCardSet(models.Model):
    set_id = models.IntegerField(max_length=100)
    set_name = models.CharField(max_length=100)
    class_id = models.IntegerField(max_length=100)
    user_id = models.