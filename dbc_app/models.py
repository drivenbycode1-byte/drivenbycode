from django.db import models

# Create your models here.

class Topic(models.Model):
    text = models.CharField(max_length=200)
    data_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Entry(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    data_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text

class IntentoHoneypot(models.Model):
    ip = models.CharField(max_length=45)
    user_agent = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Intento desde {self.ip} el {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"

class VisitNumber(models.Model):
    count = models.IntegerField(default=0)
    last_visit = models.DateTimeField(null=True, blank=True)

class UserIP(models.Model):
    ip = models.CharField(max_length=45)
    count = models.IntegerField(default=0)
    last_visit = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.count} visitas (última: {self.last_visit.strftime('%Y-%m-%d %H:%M:%S') if self.last_visit else 'sin registro'})"

from django.db import models

class Visit(models.Model):
    ip = models.GenericIPAddressField()
    path = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ip} - {self.path} - {self.timestamp}"
