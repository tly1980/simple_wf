from django.db import models
from django.contrib.auth.models import User
from simple_wf.models import WorkflowInstance


class PurchaseRequest(models.Model):
    request_time = models.DateTimeField(auto_now_add=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    product_url = models.CharField(max_length=512, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9, null=True, blank=True)
    requester = models.ForeignKey(User)
    wf_instance = models.ForeignKey(WorkflowInstance)
    last_action = models.CharField(max_length=64, null=True, blank=True)
    last_action_taker = models.ForeignKey(User, related_name='last_operated_pr')
    last_action_time = models.DateTimeField(auto_now_add=True)


class WFLog(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest)
    action_taker = models.ForeignKey(User)
    action_time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=64)
    comments = models.TextField(default='', null=True, blank=True)
    result = models.CharField(max_length=64, blank=True, null=True)
