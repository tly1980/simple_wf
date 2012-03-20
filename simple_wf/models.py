from django.db import models
from django.contrib.auth.models import User
9: from django.utils import simplejson as json

# Create your models here.

#one workflow
class Workflow(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    
#transition for the workflow
class Transition(models.Model):
    workflow = models.ForeignKey(Workflow)
    title = models.CharField(max_length=128)
    #should be run automatically or not ?
    is_auto = models.BooleanField(default=False)
    #The python class for the executor. It works use the last transition context data as input
    executor = models.CharField(max_length=512, null=True, blank=True)
    previous_transition = models.ForeignKey(Transition, related_name = 'next_transition')

    is_first = BooleanField(default=False)
    is_last = BooleanField(default=False)

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
    current_transitionlog = models.ForeignKey(TransitionLog)
    status = models.CharField(max_length=32, choices = STATUS_CHOICES)

'''
Keep the logs to every transition.
'''
class TransitionLog(models.Model):
    OPERATION_CHOISE = (
        (u'forward', u'Forward'), #bring the workflow forward
        (u'update_data', u'Update Data'), #just update the data
        (u'reopen', u'Reopen'), #just update the data
        (u'cancel', u'Cancel'), #just update the data

    )

    action_time = models.DateTimeField(auto_now_add=True)
    msg = models.Textfield()
    operator = ForeignKey(User)

    instance = ForeignKey(Instance)

    #the related transition
    from_transition = ForeignKey(Transition)

    #the related transition
    to_transition = ForeignKey(Transition)

    '''
    context data should be reused as much as possible.
    Which means, the TransitionLog with operation = reopen/cancel will not create new context_data, but reuse the existing transition.
    if there is no data modification, the "forward" transitionLog will kept use the old one.
    if there is data modificcation, the "forward" transitionLog should create the new context data.
    '''
    context_data = ForeignKey(ContextData)

    #whether it is a data update or workflow bring forward
    operation = models.CharField(max_length=32, choices=OPERATION_CHOISE)

    def getData(self):
        if self.context_data is None:
            return self.context_data

        return self.context_data.getData()


'''
Keeps the context data for every transition.
So we can trace the data changes for every transition.
'''
class ContextData(models.Model):
    #when the context is being created
    creation_time = models.DateTimeField(auto_now_add=True)

    #it belongs to which workflow
    transition = models.ForeignKey(TransitionLog)

    #store as the JSON here
    data = models.Textfield(default="{}")

    def getData(self):
        return json.loads(self.data)


class InvalidNextTransition(Exception):
    pass




'''
from_transition,
next_transition,
'''
def forward(instance, context_data, *args, **kwargs):
    from_transition = kwargs.get('from_transition', None)
    next_transition = kwargs.get('next_transition', None)
    

    if None in (next_transition, from_transition, instance):
        raise Exception, 'instance, from_transition and next_transition are required'

    try:
        from_trans.next_transition_set.objects.get(id=to_trans.id)
    except Transition.DoesNotExist:
        raise InvalidNextTransition()

    

    translog = TransitionLog.objects.create( **kwargs)
    


def update_latest_contextdata(instance, new_data):
    if new_data is None:
        return

    need_create_new = False
    current_data = instance.current_transitionlog.getData()

        



def update_data(transition):
    pass



