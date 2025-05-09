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
from .serializers import ConversationSerializer

logger = logging.getLogger(__name__)


class WebhookView(APIView):
    def post(self, request):
        logger.info("Recebido webhook: %s", request.data)

        event_type = request.data.get("type")
        timestamp = request.data.get("timestamp")
        data = request.data.get("data", {})

        try:
            if event_type == "NEW_CONVERSATION":
                logger.info("Processando NEW_CONVERSATION")
                conversation_id = uuid.UUID(data["id"])
                Conversation.objects.create(id=conversation_id)
                logger.info("Conversa criada com ID %s", conversation_id)
                return Response({"status": "Conversation created"}, status=201)

            elif event_type == "NEW_MESSAGE":
                logger.info("Processando NEW_MESSAGE")
                message_id = uuid.UUID(data["id"])
                conversation_id = uuid.UUID(data["conversation_id"])
                direction = data["direction"]
                content = data["content"]
                parsed_time = parse_datetime(timestamp)

                logger.debug("Buscando conversa com ID %s", conversation_id)
                conversation = Conversation.objects.filter(id=conversation_id).first()
                if not conversation:
                    logger.warning("Conversa não encontrada")
                    return Response({"error": "Conversation not found"}, status=404)

                if conversation.state == "CLOSED":
                    logger.warning("Conversa está fechada")
                    return Response({"error": "Conversation is closed"}, status=400)

                if direction not in ["SENT", "RECEIVED"]:
                    logger.warning("Direção inválida: %s", direction)
                    return Response({"error": "Invalid direction"}, status=400)

                Message.objects.create(
                    id=message_id,
                    conversation=conversation,
                    state=direction,  # ✅ CORRETO
                    content=content,
                    timestamp=parsed_time
                )
                logger.info("Mensagem criada com ID %s", message_id)
                return Response({"status": "Message created"}, status=201)

            elif event_type == "CLOSE_CONVERSATION":
                logger.info("Processando CLOSE_CONVERSATION")
                conversation_id = uuid.UUID(data["id"])
                conversation = Conversation.objects.filter(id=conversation_id).first()

                if not conversation:
                    logger.warning("Conversa não encontrada para fechamento")
                    return Response({"error": "Conversation not found"}, status=404)

                conversation.state = "CLOSED"
                conversation.save()
                logger.info("Conversa fechada com ID %s", conversation_id)
                return Response({"status": "Conversation closed"}, status=200)

            else:
                logger.warning("Tipo de evento desconhecido: %s", event_type)
                return Response({"error": "Unknown event type"}, status=400)

        except KeyError as e:
            logger.error("Campo ausente: %s", str(e))
            return Response({"error": f"Missing field: {str(e)}"}, status=400)
        except IntegrityError as e:
            logger.error("Erro de integridade: %s", str(e))
            return Response({"error": "ID already exists"}, status=400)
        except Exception as e:
            logger.exception("Erro inesperado")
            return Response({"error": "Unexpected error"}, status=500)


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
