from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class IndexView(TemplateView):
    def get(self, request):
        return render(request, 'lp/index.html')