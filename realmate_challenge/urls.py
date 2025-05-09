"""
URL configuration for realmate_challenge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from api import views as api_views


urlpatterns = [
    path("", api_views.ConversationListView.as_view(), name="conversations"),
    path("admin/", admin.site.urls),
    path("webhook/", api_views.WebhookView.as_view(), name="webhook"),
    path("conversations/<uuid:pk>/", api_views.ConversationDetailAPIView.as_view(), name="conversation-detail"),
    path("conversations/<slug:pk>", api_views.ConversationDetailView.as_view(), name="conversation_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
