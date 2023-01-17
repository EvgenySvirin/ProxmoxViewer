from django.db import models


class Connection(models.Model):
    host = models.CharField(max_length=200)
    backend = models.CharField(max_length=200)
    service = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    password  = models.CharField(max_length=200)
    verify_ssl = models.BooleanField(max_length=200)
    port = models.IntegerField()
    
    date = models.DateField()
    
    def __str__(self):
        return self.host + " " + self.backend + " " + self.service + " " +  str(self.port) + " " + str(self.date)
