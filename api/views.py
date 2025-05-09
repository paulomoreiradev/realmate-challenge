import logging
import uuid

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views.generic import DetailView, ListView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Conversation, Message
from .serializers import ConversationSerializer, CloseConversationSerializer, NewConversationSerializer, NewMessageSerializer

logger = logging.getLogger(__name__)


class WebhookView(APIView):
    def post(self, request):
        event_type = request.data.get("type")

        serializer_class = {
            "NEW_CONVERSATION": NewConversationSerializer,
            "NEW_MESSAGE": NewMessageSerializer,
            "CLOSE_CONVERSATION": CloseConversationSerializer,
        }.get(event_type)

        if not serializer_class:
            return Response({"error": "Unsupported event type."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data["data"]

        try:
            if event_type == "NEW_CONVERSATION":
                conversation_id = data["id"]
                _, created = Conversation.objects.get_or_create(id=conversation_id, defaults={"state": "OPEN"})
                return Response({"status": "created" if created else "already exists"})

            elif event_type == "NEW_MESSAGE":
                conversation_id = data["conversation_id"]
                conversation = get_object_or_404(Conversation, id=conversation_id)

                if conversation.state == "CLOSED":
                    return Response({"error": "Conversation is closed."}, status=status.HTTP_403_FORBIDDEN)

                _, created = Message.objects.get_or_create(
                    id=data["id"],
                    defaults={
                        "conversation": conversation,
                        "direction": data["direction"],
                        "content": data["content"]
                    }
                )
                return Response({"status": "message created" if created else "message already exists"})

            elif event_type == "CLOSE_CONVERSATION":
                conversation_id = data["id"]
                conversation = get_object_or_404(Conversation, id=conversation_id)
                conversation.state = "CLOSED"
                conversation.save()
                return Response({"status": "conversation closed"})

        except IntegrityError as e:
            return Response({"error": "Integrity error"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationDetailAPIView(APIView):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class ConversationListView(ListView):
    # context_object_name = "conversations"
    model = Conversation
    template_name = "./conversations.html"
    queryset = Conversation.objects.all()


class ConversationDetailView(DetailView):
    context_object_name = "conversation"
    model = Conversation
    template_name = "./conversation_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.get_object()
        messages = conversation.messages.all()
        context["messages"] = messages
        return context
