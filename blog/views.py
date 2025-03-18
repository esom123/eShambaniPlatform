from django.shortcuts import render
from . import models as blog_models
# Create your views here.
def index(request):
    return render( request,"blog/blog.html")