from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Userprofile(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, blank=True, on_delete=models.CASCADE)
    # profile_pic = models.ImageField(
    #     upload_to='images', default='default/user.png')
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)

    phone = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return str(self.user.first_name)
