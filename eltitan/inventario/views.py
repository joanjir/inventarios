from django.shortcuts import render

# Create your views here.


def views (request):
    return render(request,'base/base.html')
