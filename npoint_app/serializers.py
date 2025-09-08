from rest_framework import serializers
from .models import JSONData

class JSONDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = JSONData
        fields = ['json_id', 'user', 'title', 'description', 'json_content']
        read_only_fields = ['json_id', 'user', 'json_api', 'created_at', 'updated_at', 'slug', 'access_count']
