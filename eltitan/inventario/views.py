from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login', redirect_field_name='login')
def dashboard (request):
    
    return render(request,'base/body.html')
