from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "state", "content", "timestamp"]

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "state", "created_at", "messages"]


class NewConversationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["NEW_CONVERSATION"])
    timestamp = serializers.DateTimeField()
    data = serializers.DictField()

    def validate_data(self, value):
        if "id" not in value:
            raise serializers.ValidationError("Field 'id' is required in data.")
        return value


class NewMessageSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["NEW_MESSAGE"])
    timestamp = serializers.DateTimeField()
    data = serializers.DictField()

    def validate_data(self, value):
        required_fields = {"id", "direction", "content", "conversation_id"}
        missing = required_fields - value.keys()
        if missing:
            raise serializers.ValidationError(f"Missing fields in data: {', '.join(missing)}")
        if value["direction"] not in ("SENT", "RECEIVED"):
            raise serializers.ValidationError("Invalid direction.")
        return value


class CloseConversationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["CLOSE_CONVERSATION"])
    timestamp = serializers.DateTimeField()
    data = serializers.DictField()

    def validate_data(self, value):
        if "id" not in value:
            raise serializers.ValidationError("Field 'id' is required in data.")
        return value
