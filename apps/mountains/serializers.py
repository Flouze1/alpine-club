from rest_framework import serializers
from .models import mountains

class MountainSerializer(serializers.ModelSerializer):
        class Meta:
            model = mountains
            fields = ['id', 'name', 'height', 'country', 'difficulty']