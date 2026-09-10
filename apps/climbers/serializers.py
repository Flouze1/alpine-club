from rest_framework import serializers
from .models import climbers, groups, climber_members


class ClimberSerializer(serializers.ModelSerializer):
    class Meta:
        model = climbers
        fields = [
            'id', 'first_name', 'last_name', 'email',
            'sports_category', 'schoole', 'test', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GroupSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source='leader_id.last_name', read_only=True)

    class Meta:
        model = groups
        fields = ['id', 'name', 'max_members', 'created_at']
        read_only_fields = ['id', 'created_at']


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = climber_members
        fields = ['id', 'climber_id', 'group_id', 'joined_date', 'role']
        read_only_fields = ['id']