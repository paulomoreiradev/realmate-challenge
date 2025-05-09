from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
# router.register(r'conversations', ConversationViewSet)
# router.register(r'messages', MessageViewSet)

urlpatterns = [
    # path("", views.ConversationListView.as_view(), name="conversation_list"),
    path("webhook/", views.WebhookView.as_view(), name="webhook"),
    path("conversations/<uuid:pk>/", views.ConversationDetailAPIView.as_view(), name="conversation-detail"),
]