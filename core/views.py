from django.shortcuts import render

def index_view(request):
    return render(request, 'index.html')

def about_view(request):
    return render(request, 'about.html')

def careers_view(request):
    return render(request, 'careers.html')

def contact_view(request):
    return render(request, 'contact.html')

def creator_dashboard_view(request):
    return render(request, 'creator_dashboard.html')

def gallery_view(request):
    return render(request, 'gallery.html')

def login_view(request):
    return render(request, 'login.html')

def news_view(request):
    return render(request, 'news.html')

def projects_view(request):
    return render(request, 'projects.html')

def register_view(request):
    return render(request, 'register.html')

def streaming_view(request):
    return render(request, 'streaming.html')

def subscriptions_view(request):
    return render(request, 'subscriptions.html')

def viewer_dashboard_view(request):
    return render(request, 'viewer_dashboard.html')