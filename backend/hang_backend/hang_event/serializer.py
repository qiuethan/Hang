from rest_framework import serializers

from hang_event.models import HangEvent


class HangEventSerializer(serializers.ModelSerializer):
    # owner = UserSerializer()
    # # location = LocationSerializer()
    # attendees = UserSerializer(many=True)

    class Meta:
        model = HangEvent
        fields = "__all__"
