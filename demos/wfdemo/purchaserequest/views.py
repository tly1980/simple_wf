# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response


#@login_required
def home(request):
    return render_to_response('purchaserequest/app-index.html',
        {},
        context_instance=RequestContext(request))
