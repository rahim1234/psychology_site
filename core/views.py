from django.views.generic import TemplateView
from django.shortcuts import render

class HomeView(TemplateView):
    template_name = 'core/home.html'


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'
    
    


def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'core/403.html', status=403)

def custom_400(request, exception):
    return render(request, 'core/400.html', status=400)    
