from rest_framework import serializers
from .models import climbs


class AscentSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group_id.name', read_only=True)

    class Meta:
        model = climbs
        fields = [
            'id', 'group_id',
            'start_event', 'end_event',
            'result', 'comment', 'note'
        ]
        read_only_fields = ['id']