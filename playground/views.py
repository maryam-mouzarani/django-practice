from django.shortcuts import render
from .tasks import notify_customers
import requests
from django.core.cache import cache
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class HelloView(APIView):
    method_decorator(cache_page(5*60))
    def get(self,request):
        
        response=requests.get('https://httpin.org/delay/2')
        data=response.json
        return render(request, 'hello.html', {'name': data})
