from django.db import models
from django.contrib.auth.models import User
from warehouse.wf.exception import EntryAlreadyActivated, EntryNotActivated
from warehouse.wf.persistent_driver import PersistentDriver
# Create your models here.

class InvliadWorkflowInstanceStatusChange(Exception):
    def __init__(self, instance_id, current_status, to_status):
        super(Exception, self).__init__()
        self.instance_id = instance_id
        self.current_status = current_status
        self.to_status = to_status
        self.msg = '%s wf_id %s :[%s] - [%s]' % (self.__class__,
            self.instance_id, self.current_status, self.to_status)

    
    def __repr__(self):
        return self.msg

class WorkflowInstance(models.Model):
    STATUS_CHOICES = (
        (u'new', u'new'),
        (u'started', u'started'),
        (u'finished', u'finished'),
        (u'paused', u'paused'),
        (u'cancelled', u'cancelled'),
    )
    workflow = models.CharField(max_length=512)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)


class Entry(models.Model):
    STATE_CHOICES = (
        (u'activated', u'Activated'),
        (u'completed', u'Completed'),
        (u'retired', u'Retired'),
    )

    instance = models.ForeignKey(WorkflowInstance)
    entry = models.CharField(max_length=512)
    state = models.CharField(max_length=32, choices=STATE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    for_routing_eval = models.BooleanField(default=False)

    def __repr__(self):
        return 'wf_id:%s  [%s, %s, %s, %s] ' % (self.instance.id,
            self.entry,
            self.state, self.for_routing_eval, self.timestamp)


class TransitionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    input = models.ForeignKey(Entry, related_name='as_input',
        null=True, blank=True)
    output = models.ForeignKey(Entry, related_name='as_output',
        null=True, blank=True)
    comments = models.TextField()
    data = models.TextField()
    action = models.CharField(max_length=128)


class DJPersistentDriver(PersistentDriver):
    """docstring for MemPersistentDriver"""
    def __init__(self, instance_id=None, wf_name='untitled'):
        super(DJPersistentDriver, self).__init__(instance_id)

        if instance_id is None:
            self.wf_instance = WorkflowInstance.objects.create(workflow=wf_name,
                status='new')
        else:
            self.wf_instance = WorkflowInstance.objects.filter(id=instance_id)

    def activated_set(self):
        ret = set([])
        for e_obj in Entry.objects.filter(instance=self.wf_instance,
            state='activated'):
            ret.add(e_obj.entry)
        return ret

    def activate(self, *args, **kwargs):
        entries = kwargs.get('entries', set([]))
        entries = set(entries)
        for a in args:
            entries.add(a)

        existed_e = Entry.objects.filter(entry__in=entries, state='activated',
            instance=self.wf_instance)

        if len(existed_e) > 0:
            inter_set = map(lambda e_obj: e_obj.entry,  existed_e)
            raise EntryAlreadyActivated(entry_set=inter_set)

        for e in entries:
            Entry.objects.create(instance=self.wf_instance,
                entry=e,
                state='activated')

    def complete(self, entry, is_4_routing_eval=False):
        try:
            e_obj = Entry.objects.get(instance=self.wf_instance,
                entry = entry,
                state='activated')
        except Entry.DoesNotExist:
            raise EntryNotActivated(entry)

        e_obj.for_routing_eval = is_4_routing_eval
        e_obj.state = 'completed'
        e_obj.save()

    def completed_set(self, is_4_routing_eval=False):
        ret = set([])
        for e_obj in Entry.objects.filter(instance=self.wf_instance,
            state='completed',
            for_routing_eval=is_4_routing_eval):
            ret.add(e_obj.entry)
        return ret

    def disable_andjoin(self, set_in):
        for e_obj in Entry.objects.filter(
                instance=self.wf_instance,
                state='completed',
                for_routing_eval=True,
                entry__in=set_in):
            e_obj.for_routing_eval = False
            e_obj.save()

    def retired_actived(self, set_in):
        for e_obj in Entry.objects.filter(
                instance=self.wf_instance,
                state='activated',
                entry__in=set_in):
            e_obj.state = 'retired'
            e_obj.save()

    def close_wf(self):
        if self.wf_instance.state in ['started']:
            self.wf_instance.state = 'closed'
            self.wf_instance.save()
        else:
            raise InvliadWorkflowInstanceStatusChange(self.instance_id,
                self.wf_instance.state, 'cancelled')

    def start_wf(self):
        if self.wf_instance.state in ['new']:
            self.wf_instance.state = 'started'
            self.wf_instance.save()
        else:
            raise InvliadWorkflowInstanceStatusChange(self.instance_id,
                self.wf_instance.state, 'started')

    def cancel_wf(self):
        if self.wf_instance.state in ['new', 'started']:
            self.wf_instance.state = 'cancelled'
            self.wf_instance.save()
        else:
            raise InvliadWorkflowInstanceStatusChange(self.instance_id,
                self.wf_instance.state, 'cancelled')

