from piston.utils import rc
from piston.handler import BaseHandler
from .models import PurchaseRequest, WFLog
from django.db import transaction
from simple_wf.models import DJPersistentDriver
from .routes import pr_router
from simple_wf.engine import WorkflowEngine
from django.utils import simplejson as json
from datetime import datetime

action_display_dict = {
    'request_purchase': 'Request Purchase',
    'admin_check': 'Admin Check',
    'manager_check': 'Manager Check',
    'place_order': 'Place Order',
    'confirm_received': 'Received Confirmed'
}

def wfengine_from_pr(user, pr):
    p_driver = DJPersistentDriver(
        operator=user,
        instance_id=pr.wf_instance.id)
    return WorkflowEngine(p_driver, pr_router)


class PRHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT')
    model = PurchaseRequest

    fields = ('id',
            'request_time',
            'product_name',
            'product_url',
            'amount',
            ('requester', ('id', 'username')),
            'status',
            'pending_action',
            'last_action',
            ('last_action_taker', ('id', 'username')),
            'last_action_time')

    def filter_pr(self, request, filter_param):
        if filter_param == 'created_by_me':
            return PurchaseRequest.objects.filter(requester=request.user)

        if filter_param == 'pending_on_manager_check':
            return PurchaseRequest.objects.filter(
                wf_instance__entry__state='activated',
                wf_instance__entry__entry='manager_check').distinct()

        if filter_param == 'pending_on_admin_check':
            return PurchaseRequest.objects.filter(
                wf_instance__entry__state='activated',
                wf_instance__entry__entry='admin_check').distinct()

        if filter_param == 'confirm_received':
            return PurchaseRequest.objects.filter(
                wf_instance__entry__state='activated',
                wf_instance__entry__entry='confirm_received').distinct()

        if filter_param == 'all':
            return PurchaseRequest.objects.all()


    def read(self, request, **kwargs):
        pr_id = kwargs.get('pr_id')
        if pr_id:
            try:
                prequest = PurchaseRequest.objects.get(id=pr_id)
                return self.decorate_ret(request.user, prequest)

            except PurchaseRequest.DoesNotExist:
                return rc.NOT_FOUND

        filter_param = request.GET.get('filter')
        if filter_param:
            return self.filter_pr(request, filter_param)

        return rc.BAD_REQUEST

    @transaction.commit_on_success
    def create(self, request, **kwargs):
        db_driver = DJPersistentDriver(operator=request.user, wf_name='PurchaseRequest')
        wf_engine = WorkflowEngine(db_driver, pr_router)
        wf_engine.wf_start()

        param_dict = json.loads(request.raw_post_data)
        prequest = PurchaseRequest.objects.create(
            product_name=param_dict.get('product_name'),
            product_url=param_dict.get('product_url'),
            amount=param_dict.get('amount'),
            requester=request.user,
            last_action='create',
            last_action_taker=request.user,
            wf_instance=db_driver.wf_instance
        )

        WFLog.objects.create(
            purchase_request=prequest,
            action_taker=request.user,
            action='create',
            comments='Created by: %s' % request.user.username,
            result="success")

        return self.decorate_ret(request.user, prequest)

    @transaction.commit_on_success
    def update(self, request, **kwargs):
        param_dict = json.loads(request.raw_post_data)
        pr_id = kwargs.get('pr_id')
        if pr_id:
            try:
                prequest = PurchaseRequest.objects.get(id=pr_id)
                old_val = {
                    'pd_name': prequest.product_name,
                    'pd_url': prequest.product_url,
                    'amount': prequest.amount,
                }
                prequest.product_name = param_dict.get('product_name')
                prequest.product_url = param_dict.get('product_url')
                prequest.amount = param_dict.get('amount')
                prequest.save()

                WFLog.objects.create(
                    purchase_request=prequest,
                    action_taker=request.user,
                    action='modify request',
                    comments='old_val: %s' % old_val,
                    result="success")


            except PurchaseRequest.DoesNotExist:
                return rc.NOT_FOUND

        return {'result': 'ok'}

    def decorate_ret(self, user, prequest):
        wf_engine = wfengine_from_pr(user, prequest)

        can_edit = False

        if user.id == prequest.requester.id and 'request_purchase' in wf_engine.todo_set():
            can_edit = True

        ret = {
            'id': prequest.id,
            'request_time': prequest.request_time,
            'product_name': prequest.product_name,
            'product_url': prequest.product_url,
            'amount': prequest.amount,
            'requester': {
                'id': prequest.requester.id,
                'name': prequest.requester.username,
            },
            'last_action': prequest.last_action,
            'last_action_taker': prequest.last_action_taker.username,
            'last_action_time': prequest.last_action_time,
            'can_edit': can_edit,
        }

        todos = []
        for a in wf_engine.todo_set():
            if a != '_end':
                todos.append({'action': a,
                    'action_text': action_display_dict.get(a)
                })

        if len(todos) > 0:
            ret['todos'] = todos

        return ret


class PRWFHandler(BaseHandler):
    allowed_methods = ('PUT', )

    @transaction.commit_on_success
    def update(self, request, **kwargs):
        pr_id = kwargs.get('pr_id', None)

        action = request.POST.get('action', None)
        comments = request.POST.get('comments', '')
        conditions_str = request.POST.get('conditions')
        conditions = None

        if conditions_str:
            conditions = json.loads(conditions_str)

        wf_engine = None

        if pr_id:
            try:
                pr = PurchaseRequest.objects.get(id=pr_id)
                wf_engine = wfengine_from_pr(request.user, pr)
                if action not in  wf_engine.todo_set():
                    return {'error': 'invalid_action'}

            except PurchaseRequest.DoesNotExist:
                return rc.NOT_FOUND

        if action == 'request_purchase':
            conditions = {'amount': pr.amount}

        if wf_engine:
            try:
                if conditions:
                    wf_engine.complete(action, data=conditions)
                else:
                    wf_engine.complete(action)

                pr.last_action = action
                pr.last_action_time = datetime.now()
                pr.save()

                WFLog.objects.create(
                    purchase_request=pr,
                    action_taker=request.user,
                    action=action,
                    comments=comments,
                    result="success")

                if 'place_order' in wf_engine.todo_set():
                    wf_engine.complete('place_order')

                    WFLog.objects.create(
                        purchase_request=pr,
                        action_taker=request.user,
                        action='place_order',
                        comments='AUTO Completed',
                        result="success")

                notify_update(pr, request.user)
                return {'result': 'sucess'}
            except Exception as e:
                    WFLog.objects.create(
                        action_taker=request.user,
                        action=action,
                        comments=comments,
                        result="error",
                        reason='invalid_action: ' + e
                    )

        return rc.BAD_REQUEST



class WFLogHandler(BaseHandler):
    allowed_methods = ('GET', )

    fields = ('id', 'action_time', 'action', 'comments', 'result',
        ('action_taker', ('username', 'id')))

    def read(self, request, **kwargs):
        pr_id = kwargs.get('pr_id', None)

        if pr_id:
            try:
                return WFLog.objects.filter(purchase_request__id=pr_id)

            except PurchaseRequest.DoesNotExist:
                return rc.NOT_FOUND

        return rc.BAD_REQUEST


import requests

def notify_update(prequest, user):
    params = {
        'pr_id': prequest.id,
        'operator': user.username
    }
    r = requests.get("http://localhost:8888/", params={'msg': json.dumps(params)})
