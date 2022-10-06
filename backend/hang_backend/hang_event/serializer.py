from rest_framework import serializers

from hang_event.models import HangEvent


class HangEventSerializer(serializers.ModelSerializer):
    # owner = UserReaderSerializer()
    # # location = LocationSerializer()
    # attendees = UserReaderSerializer(many=True)

    class Meta:
        model = HangEvent
        fields = "__all__"
