from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Post, Report, Mark

class PostBaseModelSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class ReportBaseModelSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class MarkBaseModelSerializer(ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'

class PostCreateRetrieveModelSerializer(PostBaseModelSerializer):
    writer_username = serializers.ReadOnlyField(source='writer.username')

    class Meta(PostBaseModelSerializer.Meta):
        fields = ['id', 'word', 'meaning', 'writer_username', 'prev_id', 'next_id']

class MarkedPostRetrieveModelSerializer(MarkBaseModelSerializer):
    mark_id = serializers.ReadOnlyField(source='id')
    id = serializers.ReadOnlyField(source='post.id')
    word = serializers.ReadOnlyField(source='post.word')
    meaning = serializers.ReadOnlyField(source='post.meaning')
    writer_username = serializers.ReadOnlyField(source='post.writer.username')
    
    class Meta(MarkBaseModelSerializer.Meta):
        fields = ['mark_id', 'id', 'word', 'meaning', 'writer_username', 'prev_id', 'next_id']