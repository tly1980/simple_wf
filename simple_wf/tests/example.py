from django.test import TestCase
from ..engine import WorkflowEngine
# from ..persistent_driver import MemPersistentDriver
from ..statemachine import Router, Route

from ..models import DJPersistentDriver

from django.contrib.auth.models import User


class SimpleConditionRoutingTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='wf_user')
        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
            Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
            Route().any('pass').next('_end'),
            Route().any('not_pass').next('_end'),
        )

        self.wf_engine = WorkflowEngine(DJPersistentDriver(operator=user), router)

    def test_pass(self):
        self.wf_engine.wf_start()

        # the first todo should be "check"
        self.assertEqual(self.wf_engine.todo_set(), set(['check']))

        # provide the score to the complete function, it will choose next
        # appropriate workflow activity
        self.wf_engine.complete('check', data={'score': 60})

        # when score is less than 60, the only proper activity is pass
        self.assertEqual(self.wf_engine.todo_set(), set(['pass']))

        self.wf_engine.complete('pass')

        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))
        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')
        self.assertEqual(self.wf_engine.wf_state(), 'closed')

    def test_not_pass(self):
        self.wf_engine.wf_start()

        # the first todo should be "check"
        self.assertEqual(self.wf_engine.todo_set(), set(['check']))

        # provide the score to the complete function, it will choose next
        # appropriate workflow activity
        self.wf_engine.complete('check', data={'score': 59})

        # when score is greater than 60, the only proper activity is pass
        self.assertEqual(self.wf_engine.todo_set(), set(['not_pass']))

        # now you should do sth to handle
        self.wf_engine.complete('not_pass')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')

        self.assertEqual(self.wf_engine.wf_state(), 'closed')


class SimpleAndJoinTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='wf_user')
        router = Router(
            Route().any('_new').next('take_a_photo'),
            Route().any('take_a_photo').next('publish_on_twitter', 'publish_on_facebook'),
            Route().exact('publish_on_twitter', 'publish_on_facebook').next('notify_share_done'),
            Route().any('notify_share_done').next('_end'),
        )

        # basic setup of the wfengine
        self.wf_engine = WorkflowEngine(DJPersistentDriver(operator=user), router)

    def test_publish_on_twitter_first(self):
        self.wf_engine.wf_start()
        # the first step should be take_a_photo
        self.assertEqual(self.wf_engine.todo_set(), set(['take_a_photo']))

        # after you finish taking a photo,
        self.wf_engine.complete('take_a_photo')
        # you enter a split branch: should be publish_on_twitter, publish_on_facebook
        self.assertEqual(self.wf_engine.todo_set(),
            set(['publish_on_twitter', 'publish_on_facebook']))

        # it doesn't matter which step you execute first,
        self.wf_engine.complete('publish_on_twitter')
        self.assertEqual(self.wf_engine.todo_set(), set(['publish_on_facebook']))

        # but you have to finish both to enter the next step: notify_share_done
        # that is what we called and-join
        self.wf_engine.complete('publish_on_facebook')
        self.assertEqual(self.wf_engine.todo_set(), set(['notify_share_done']))

        self.wf_engine.complete('notify_share_done')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))

    def test_publish_on_facebook_first(self):
        '''
        Almost the same thing as test_publish_on_twitter_first,
        just complete 'publish_on_facebook' before 'publish_on_twitter'
        '''

        self.wf_engine.wf_start()
        # the first step should be take_a_photo
        self.assertEqual(self.wf_engine.todo_set(), set(['take_a_photo']))

        # after you finish taking a photo,
        self.wf_engine.complete('take_a_photo')
        # you enter a split branch: should be publish_on_twitter, publish_on_facebook
        self.assertEqual(self.wf_engine.todo_set(),
            set(['publish_on_twitter', 'publish_on_facebook']))

        # it doesn't matter which step you execute first,
        self.wf_engine.complete('publish_on_facebook')
        self.assertEqual(self.wf_engine.todo_set(), set(['publish_on_twitter']))

        # but you have to finish both to enter the next step: notify_share_done
        # that is what we called and-join
        self.wf_engine.complete('publish_on_twitter')
        self.assertEqual(self.wf_engine.todo_set(), set(['notify_share_done']))

        self.wf_engine.complete('notify_share_done')
        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))
