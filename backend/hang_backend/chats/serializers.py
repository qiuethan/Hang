"""
ICS4U
Paul Chen
This module contains serializers for the messaging system.
"""

from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from knox.auth import TokenAuthentication
from rest_framework import serializers, validators
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.relations import PrimaryKeyRelatedField

from .models import UserMessage, MessageChannel, DirectMessageChannel, GroupMessageChannel, Reaction, SystemMessage


class MessageChannelSerializer(serializers.ModelSerializer):
    """
    Serializes a MessageChannel to JSON.
    """

    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "created_at", "message_last_sent"]
        read_only_fields = ["channel_type", "created_at", "message_last_sent"]


class DirectMessageChannelSerializer(MessageChannelSerializer):
    """
    Serializes a DirectMessageChannel to JSON.

    Attributes:
      users (PrimaryKeyRelatedField): Users in the direct message channel.
      has_read (SerializerMethodField): Whether the message channel has been read.
    """

    users = PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta(MessageChannelSerializer.Meta):
        model = DirectMessageChannel
        fields = MessageChannelSerializer.Meta.fields + ["users", "created_at", "has_read"]
        read_only_fields = ["id", "channel_type", "created_at", "has_read"]

    def get_has_read(self, obj):
        """
        Checks if the message channel has been read by the user.

        Arguments:
          obj (DirectMessageChannel): The direct message channel.

        Returns:
          bool: True if the message channel has been read, False otherwise.
        """
        return obj.has_read_message_channel(self.context["request"].user)

    def create(self, validated_data):
        """
        Creates a new direct message channel.

        Arguments:
          validated_data (dict): The validated data for the direct message channel.

        Returns:
          DirectMessageChannel: The created direct message channel.
        """
        users = validated_data["users"]
        return MessageChannel.objects.create_direct_message(users[0], users[1])

    def validate(self, data):
        """
        Validates the data for the direct message channel.

        Arguments:
          data (dict): The data for the direct message channel.

        Returns:
          dict: The validated data.

        Raises:
          ValidationError: If the data is invalid.
        """
        current_user = self.context["request"].user
        users = data["users"]

        # Verifies data.
        if current_user not in users:
            raise serializers.ValidationError("The creation of a DM must include the current user.")
        if len(users) != 2:
            raise serializers.ValidationError("A DM must have exactly 2 people.")

        to_user = users[0] if users[1] == current_user else users[1]
        if current_user.message_channels.filter(channel_type="DM").filter(users=to_user).exists():
            raise serializers.ValidationError("DM already exists.")

        return data


class GroupMessageChannelSerializer(MessageChannelSerializer):
    """
    Serializes a GroupMessageChannel to JSON.

    Attributes:
      owner (PrimaryKeyRelatedField): The owner of the group message channel.
      users (PrimaryKeyRelatedField): The users in the group message channel.
      channel_type (CharField): The type of the message channel.
      has_read (SerializerMethodField): Whether the message channel has been read.
    """

    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    channel_type = serializers.CharField(required=False)
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta(MessageChannelSerializer.Meta):
        model = GroupMessageChannel
        fields = MessageChannelSerializer.Meta.fields + ["name", "owner", "users", "created_at", "has_read"]
        read_only_fields = ["id", "channel_type", "created_at", "has_read"]

    def get_has_read(self, obj):
        """
        Checks if the message channel has been read by the user.

        Arguments:
          obj (GroupMessageChannel): The group message channel.

        Returns:
          bool: True if the message channel has been read, False otherwise.
        """
        return obj.has_read_message_channel(self.context["request"].user)

    def create(self, validated_data):
        """
        Creates a new group message channel.

        Arguments:
          validated_data (dict): The validated data for the group message channel.

        Returns:
          GroupMessageChannel: The created group message channel.
        """
        current_user = self.context["request"].user
        users = validated_data["users"]

        if current_user not in users:
            raise validators.ValidationError("The creation of a group chats must include the current user.")

        return MessageChannel.objects.create_group_chat(name=validated_data["name"], owner=current_user, users=users)

    def validate_users(self, new_users):
        """
        Validates the users for the group message channel.

        Arguments:
          new_users (list): The new users for the group message channel.

        Returns:
          list: The validated users.

        Raises:
          ValidationError: If the users are invalid.
        """
        if self.instance:
            current_user = self.context["request"].user
            users = set(self.instance.users.all())
            new_users_copy = set(new_users.copy())

            users.remove(current_user)
            new_users_copy.discard(current_user)

            if len(users.intersection(new_users_copy)) != len(users) and self.instance.owner.id != current_user.id:
                raise serializers.ValidationError("Permission Denied.")

        return new_users

    def validate_owner(self, new_owner):
        """
        Validates the owner for the group message channel.

        Arguments:
          new_owner (User): The new owner for the group message channel.

        Returns:
          User: The validated owner.

        Raises:
          ValidationError: If the owner is invalid.
        """
        current_user = self.context["request"].user
        instance = self.instance

        if instance.owner != new_owner and current_user != instance.owner:
            raise serializers.ValidationError("Permission Denied.")
        if ("users" in self.initial_data and new_owner.id not in self.initial_data["users"]) or \
                ("users" not in self.initial_data and not instance.users.filter(id=new_owner.id).exists()):
            raise serializers.ValidationError("Owner is not in the group chats.")
        return new_owner

    def update(self, instance, validated_data):
        """
        Updates the group message channel.

        Arguments:
          instance (GroupMessageChannel): The group message channel to update.
          validated_data (dict): The validated data for the group message channel.

        Returns:
          GroupMessageChannel: The updated group message channel.
        """
        current_user = self.context["request"].user

        if "users" in validated_data:
            instance.update_users(current_user, validated_data["users"])

        if "owner" in validated_data:
            instance.update_owner(current_user, validated_data["owner"])

        if "name" in validated_data:
            instance.update_name(current_user, validated_data["name"])

        return instance


class ReadMessageChannelSerializer(serializers.ModelSerializer):
    """
    Serializes a MessageChannel to JSON, including a flag indicating whether the channel has been read.
    
    Attributes:
      has_read (SerializerMethodField): Whether the message channel has been read.
    """
    has_read = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MessageChannel
        fields = ["id", "channel_type", "users", "created_at", "message_last_sent", "has_read"]
        read_only_fields = ["id", "channel_type", "users", "created_at", "message_last_sent", "has_read"]

    def update(self, instance, validated_data):
        """
        Marks the message channel as read by the user.

        Arguments:
          instance (MessageChannel): The message channel to update.
          validated_data (dict): The validated data for the message channel.

        Returns:
          MessageChannel: The updated message channel.
        """
        instance.read_message_channel(self.context["request"].user)
        return instance

    def get_has_read(self, obj):
        """
        Checks if the message channel has been read by the user.

        Arguments:
          obj (MessageChannel): The message channel.

        Returns:
          bool: True if the message channel has been read, False otherwise.
        """
        return obj.has_read_message_channel(self.context["request"].user)


class ReactionSerializer(serializers.ModelSerializer):
    """
    Serializes a Reaction to JSON.
    """

    class Meta:
        model = Reaction
        fields = ("user", "emoji")
        read_only_fields = ("user", "emoji")


class MessageSerializer(serializers.Serializer):
    """
    Serializes a Message to JSON, selecting the appropriate serializer based on the message type.
    """

    @classmethod
    def get_serializer(cls, _type):
        """
        Returns the appropriate serializer for the given message type.

        Arguments:
          _type (str): The type of the message.

        Returns:
          Serializer: The appropriate serializer for the message type.
        """
        if _type == "user_message":
            return UserMessageSerializer
        if _type == "system_message":
            return SystemMessageSerializer

    def to_representation(self, instance):
        """
        Returns a dictionary representing the message.

        Arguments:
          instance (Message): The message to represent.

        Returns:
          dict: A dictionary representing the message.
        """
        serializer = self.get_serializer(instance.type)
        return serializer(serializer.Meta.model.objects.get(pk=instance.pk)).data


class UserMessageSerializer(serializers.ModelSerializer):
    """
    Serializes a UserMessage to JSON.

    Attributes:
      user (PrimaryKeyRelatedField): The user who sent the message.
      message_channel (PrimaryKeyRelatedField): The channel in which the message was sent.
      reply (PrimaryKeyRelatedField): The message to which this message is a reply.
      reactions (ReactionSerializer): The reactions to the message.
    """

    user = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    reply = PrimaryKeyRelatedField(queryset=UserMessage.objects.all(), allow_null=True)
    reactions = ReactionSerializer(many=True, required=False)

    class Meta:
        model = UserMessage
        fields = ("type", "id", "user", "created_at", "updated_at", "content", "message_channel", "reply", "reactions")
        read_only_fields = ("type", "id", "user", "created_at", "updated_at", "reactions")

    def validate_user(self, instance):
        """
        Validates the user of the message.

        Arguments:
          instance (UserMessage): The message.

        Raises:
          ValidationError: If the user is invalid.
        """
        if instance.user.username != self.context["user"].username:
            raise serializers.ValidationError("Message does not exist.")

    def validate_message_channel(self, value):
        """
        Validates the message channel of the message.

        Arguments:
          value (MessageChannel): The message channel.

        Returns:
          MessageChannel: The validated message channel.

        Raises:
          ValidationError: If the message channel is invalid.
        """
        try:
            value.users.get(username=self.context["user"].username)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Message channel does not exist.")
        return value

    def validate_reply(self, value):
        """
        Validates the reply of the message.

        Arguments:
          value (UserMessage): The reply.

        Returns:
          UserMessage: The validated reply.

        Raises:
          ValidationError: If the reply is invalid.
        """
        message_channel = self.initial_data.get("message_channel")
        if value is not None and value.message_channel_id != message_channel:
            raise serializers.ValidationError("Replied message does not exist.")
        return value

    def create(self, validated_data):
        """
        Creates a new user message.

        Arguments:
          validated_data (dict): The validated data for the user message.

        Returns:
          UserMessage: The created user message.
        """
        message = UserMessage.objects.create(user=self.context["user"], **validated_data)
        validated_data["message_channel"].message_last_sent = datetime.now()
        validated_data["message_channel"].save()
        return message

    def update(self, instance, validated_data):
        """
        Updates a user message.

        Arguments:
          instance (UserMessage): The user message to update.
          validated_data (dict): The validated data for the user message.

        Returns:
          UserMessage: The updated user message.
        """
        self.validate_user(instance)
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class SystemMessageSerializer(serializers.ModelSerializer):
    """
    Serializes a SystemMessage to JSON.

    Attributes:
      message_channel (PrimaryKeyRelatedField): The channel in which the system message was sent.
      reactions (ReactionSerializer): The reactions to the system message.
    """

    message_channel = PrimaryKeyRelatedField(queryset=MessageChannel.objects.all())
    reactions = ReactionSerializer(many=True, required=False)

    class Meta:
        model = SystemMessage
        fields = ("type", "id", "created_at", "updated_at", "content", "message_channel", "reactions")
        read_only_fields = ("type", "id", "created_at", "updated_at", "message_channel", "reactions")


class AuthenticateWebsocketSerializer(serializers.Serializer):
    """
    Serializes a token for websocket authentication.

    Attributes:
      token (CharField): The authentication token.
    """

    token = serializers.CharField(max_length=100)

    def validate_token(self, data):
        """
        Validates the authentication token.

        Arguments:
          data (str): The authentication token.

        Returns:
          User: The user associated with the token.

        Raises:
          ValidationError: If the token is invalid.
        """
        # Checks if the AuthToken is valid.
        try:
            auth = TokenAuthentication().authenticate_credentials(data.encode("utf-8"))
            return auth[0]
        except AuthenticationFailed:
            raise serializers.ValidationError("Invalid Token.")

    def validate(self, data):
        """
        Validates the data for websocket authentication.

        Arguments:
          data (dict): The data for websocket authentication
        """
        if data["token"].username != self.context["user"].username:
            raise serializers.ValidationError("Token does not match user.")
        return data["token"]