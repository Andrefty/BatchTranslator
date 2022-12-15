from django.db import models

# Create your models here.
class Emailaddress(models.Model):
    email = models.EmailField(max_length=100,blank=True)
    # language chooser
    # language = models.CharField(max_length=2, choices=[('en', 'English'), ('de', 'German')], default='en')
    filename = models.CharField(max_length=100,blank=True)
    def __str__(self):
        return self.email