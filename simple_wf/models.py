from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson as json


"""
# Create your models here.

#one workflow
class Workflow(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    
#transition for the workflow
class Activity(models.Model):
    workflow = models.ForeignKey(Workflow)
    name = models.CharField(max_length=128)
    #The python class for the executor. It works use the last transition context data as input
    app = models.CharField(max_length=512, null=True, blank=True)
    perm_cfg = models.TextField()

class Transition(models.Model):
    activity = models.ForeignKey(Activity)
    status = models.CharField(max_length=128)
    condition = models.TextField()
    

'''
In
'''
class Instance(models.Model):
    STATUS_CHOICES = (
        (u'openned', u'Openned'),
        
        (u'in_prog', u'In progressed'),
        (u'finished', u'Finished'),

        (u'paused', u'Paused'),
        (u'cancelled', u'Cancelled'),
    )

    workflow = models.ForeignKey(Workflow)
    status = models.CharField(max_length=32, choices = STATUS_CHOICES)

'''
Keep the logs to every transition.
'''
class TransitionLog(models.Model):
    STATUS_ACTIVITY = (
        (u'activated'), #bring the workflow forward
        (u'completed'), #just update the data
    )

    LOG_STATUS = (
        (u'activated'), #bring the workflow forward
        (u'completed'), #just update the data
    )



    creation_time = models.DateTimeField(auto_now_add=True)
    msg = models.TextField()
    operator = ForeignKey(User)

    instance = ForeignKey(Instance)
    activity = ForeignKey(Activity)

    in_data = models.TextField(default="{}")
    out_data = models.TextField(default="{}")

    #whether it is a data update or workflow bring forward
    status = models.CharField(max_length=32, choices=STATUS_ACTIVITY)

    def getOutData(self):
        if self.context_data is None:
            return self.context_data

        return self.context_data.getData()
"""
