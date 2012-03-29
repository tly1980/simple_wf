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
    operator = models.ForeignKey(User)

    def __repr__(self):
        return '<%s, %s:%s>' % (self.id, self.__class__.__name__,
            self.entry)

    def __str__(self):
        return 'wf_id:%s  [%s, %s, %s, %s] ' % (self.instance.id,
            self.entry,
            self.state, self.for_routing_eval, self.timestamp)


class TransitionLog(models.Model):
    LEVEL_CHOICES = (
        ('info', 'info'),
        ('error', 'error'),
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    triger = models.ForeignKey(Entry, related_name='as_triger',
        null=True, blank=True)
    output = models.ForeignKey(Entry, related_name='as_output',
        null=True, blank=True)
    comments = models.TextField()
    level = models.CharField(max_length=32)
    data = models.TextField()
    action = models.CharField(max_length=128)
    instance = models.ForeignKey(WorkflowInstance)
    operator = models.ForeignKey(User)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)

    def __str__(self):
        return '[%s, %s, %s - %s] wf_id:%s, triger:%s, output:%s, %s' % (
            self.operator, self.timestamp, self.level, self.action, self.instance.id,
            repr(self.triger), repr(self.output), self.comments)


class DJPersistentDriver(PersistentDriver):
    """docstring for MemPersistentDriver"""
    def __init__(self, instance_id=None, wf_name='untitled', operator=None):
        super(DJPersistentDriver, self).__init__(instance_id)

        self.operator = operator
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
            msg_array = str(map(lambda the_e: '%s' % repr(the_e), existed_e))
            x = EntryAlreadyActivated(entry_set=inter_set)
            #loggin for exception
            self.log(
                level='error',
                action='activate',
                comments='%s - %s' % (repr(x), msg_array),
            )
            raise x

        triger = kwargs.get('triger', None)
        for e in entries:
            act_eobj = self.create_entry(
                entry=e,
                state='activated')

            self.log(
                triger=triger,
                output=act_eobj,
                level='info',
                action='activate',
                comments='activated:%s' % repr(act_eobj))

    def complete(self, entry, is_4_routing_eval=False):
        try:
            e_obj = Entry.objects.get(instance=self.wf_instance,
                entry=entry,
                state='activated')
        except Entry.DoesNotExist:
            #loggin for exception
            x = EntryNotActivated(entry)
            self.log(
                level='error',
                action='complete',
                comments=repr(x))
            raise x

        e_obj.for_routing_eval = is_4_routing_eval
        e_obj.state = 'completed'
        e_obj.save()

        #loggin for exception
        self.log(
            level='info',
            action='complete',
            comments='completed:%s' % repr(entry))

    def completed_set(self, is_4_routing_eval=False):
        ret = set([])
        for e_obj in Entry.objects.filter(instance=self.wf_instance,
            state='completed',
            for_routing_eval=is_4_routing_eval):
            ret.add(e_obj.entry)
        return ret

    def disable_andjoin(self, set_in, caused_by=None):
        for e_obj in Entry.objects.filter(
                instance=self.wf_instance,
                state='completed',
                for_routing_eval=True,
                entry__in=set_in):
            e_obj.for_routing_eval = False
            e_obj.save()

            # logging ...
            triger = None
            comments = '%s:for_routing_eval set to False' % (repr(e_obj))
            if caused_by:
                triger = Entry.objects.filter(
                    instance=self.wf_instance,
                    entry=caused_by
                ).exclude(state__in=['retired']).order_by('-timestamp')[0]
                comments += ' - caused_by:' + repr(triger)

            self.log(
                triger=triger,
                output=e_obj,
                level='info',
                action='disable_andjoin',
                comments=comments,
            )

    def retire(self, set_in, caused_by=None):
        for e_obj in Entry.objects.filter(
                instance=self.wf_instance,
                state='activated',
                entry__in=set_in):
            e_obj.state = 'retired'
            e_obj.save()

            triger = None
            comments = 'retire:%s' % repr(e_obj)

            #logging....
            if caused_by:
                triger = Entry.objects.get(
                    instance=self.wf_instance,
                    state='activated',
                    entry=caused_by)
                comments += ' - caused_by:' + repr(triger)

            self.log(
                triger=triger,
                output=e_obj,
                level='info',
                action='retire',
                comments=comments)

    def close_wf(self):
        if self.wf_instance.state in ['started']:
            self.wf_instance.state = 'closed'
            self.wf_instance.save()

            self.log(
                level='info',
                action='close_wf',
                comments='workflow closed')
        else:
            raise InvliadWorkflowInstanceStatusChange(self.instance_id,
                self.wf_instance.state, 'closed')

    def start_wf(self):
        if self.wf_instance.state in ['new']:
            self.wf_instance.state = 'started'
            self.wf_instance.save()

            self.log(
                level='info',
                action='start_wf',
                comments='workflow started')
        else:
            raise InvliadWorkflowInstanceStatusChange(self.instance_id,
                self.wf_instance.state, 'started')

    def cancel_wf(self):
        if self.wf_instance.state in ['new', 'started']:
            self.wf_instance.state = 'cancelled'
            self.wf_instance.save()

            self.log(
                level='info',
                action='cancel_wf',
                comments='workflow cancelled')
        else:
            raise InvliadWorkflowInstanceStatusChange(self.instance_id,
                self.wf_instance.state, 'cancelled')

    def log(self, *args, **kwargs):
        kwargs['instance'] = self.wf_instance
        kwargs['operator'] = self.operator
        TransitionLog.objects.create(**kwargs)

    def create_entry(self, *args, **kwargs):
        kwargs['instance'] = self.wf_instance
        kwargs['operator'] = self.operator
        return Entry.objects.create(**kwargs)
