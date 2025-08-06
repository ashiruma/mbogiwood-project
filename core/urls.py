from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('about/', views.about_view, name='about'),
    path('careers/', views.careers_view, name='careers'),
    path('contact/', views.contact_view, name='contact'),
    path('creator-dashboard/', views.creator_dashboard_view, name='creator-dashboard'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('login/', views.login_view, name='login'),
    path('news/', views.news_view, name='news'),
    path('projects/', views.projects_view, name='projects'),
    path('register/', views.register_view, name='register'),
    path('streaming/', views.streaming_view, name='streaming'),
    path('subscriptions/', views.subscriptions_view, name='subscriptions'),
    path('viewer-dashboard/', views.viewer_dashboard_view, name='viewer-dashboard'),
]