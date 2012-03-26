from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson as json

# Create your models here.

'''
In
'''
class WorkflowInstance(models.Model):
    STATUS_CHOICES = (
        (u'openned', u'openned'),
        
        (u'in_proc', u'in_proc'),
        (u'finished', u'finished'),

        (u'paused', u'paused'),
        (u'cancelled', u'cancelled'),
    )
    workflow = models.CharField(max_length=512)
    status = models.CharField(max_length=32, choices = STATUS_CHOICES)

class Entry(models.Model):
    STATE_CHOICES = (
        (u'activated', u'Activated'),
        (u'completed', u'Completed'),
        (u'retired', u'Retired'),
    )

    instance = models.ForeignKey(WorkflowInstance)
    entry = models.CharField(max_length=512)
    state = models.CharField(max_length=32, choices = STATE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    for_routing_eval = models.BooleanField(default=False)

class TransitionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)    
    input = models.ForeignKey(Entry, related_name='as_input')
    output = models.ForeignKey(Entry, related_name='as_output')
    comments = models.TextField()
    data = models.TextField()
    action = models.CharField(max_length=128)
    