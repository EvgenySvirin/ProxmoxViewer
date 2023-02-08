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
   
    @classmethod
    def get_default_pk(cls):
        return 1
        
        
class UserConnection(models.Model):
    username = models.CharField(max_length=200)
    connection =  models.ForeignKey(to=Connection, on_delete=models.CASCADE, default=Connection.get_default_pk)
    date = models.DateField()
    
    def __str__(self):
        return self.username + " " + str(self.connection) + " " + str(self.date)
        
        
class NodePassword(models.Model):
    nodename = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    connection =  models.ForeignKey(to=Connection, on_delete=models.CASCADE, default=Connection.get_default_pk)
    date = models.DateField()
    
    def __str__(self):
        return self.nodename + " " + str(self.password) + " " + str(self.connection) + " " + str(self.date)
