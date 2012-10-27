from django.conf.urls import patterns, url
from piston.resource import Resource
from .handlers import PRWFHandler, PRHandler, WFLogHandler

handlers = {
    'pr': Resource(PRHandler),
    'pr_wf': Resource(PRWFHandler),
    'pr_log': Resource(WFLogHandler),
}

urlpatterns = patterns(
    url(r'^filter/$', handlers.get('pr')),
    url(r'^$', handlers.get('pr')),
    url(r'^(?P<pr_id>\d+)$', handlers.get('pr')),
    url(r'^(?P<pr_id>\d+)/wf/$', handlers.get('pr_wf')),
    url(r'^(?P<pr_id>\d+)/log/$', handlers.get('pr_log')),
)
