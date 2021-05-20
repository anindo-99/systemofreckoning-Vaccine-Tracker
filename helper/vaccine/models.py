from django.db import models

# Create your models here.


class VaccineSlot(models.Model):
    state_name = models.CharField(max_length=100)
    district_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email_notification = models.EmailField(max_length=254)

    def __str__(self):
        return f'Enquiry from State: {self.state_name} and District: {self.district_name}'
