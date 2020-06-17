from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic


# Create your views here.
def home(request):
    return render(request, "base.html")

def search(request):
    search_query = request.POST["search_query"]
    return HttpResponse(content=search_query)

'''
 Set up list view model which takes query, stores it, and then passes
 it to the actual search function (which should be somewhere else) which will
 then make the request of craigs list and pass back a json-like list of dicts
 which will include hrefs, imgs, descriptive text, price, and authors. This
 will be the context object which is used in the currently unmade view
 '''