from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Post(models.Model):
    word = models.TextField(verbose_name='단어')
    meaning = models.TextField(verbose_name='의미')
    created_at = models.DateTimeField(verbose_name='작성일', auto_now_add=True)
    writer = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    prev_id = models.IntegerField(verbose_name='이전 단어 ID', null=True, blank=True, editable=False)
    next_id = models.IntegerField(verbose_name='다음 단어 ID', null=True, blank=True, editable=False)

class Report(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    writer = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)

class Mark(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    prev_id = models.IntegerField(verbose_name='이전 저장한 단어 ID', null=True, blank=True, editable=False)
    next_id = models.IntegerField(verbose_name='다음 저장한 단어 ID', null=True, blank=True, editable=False)
    writer = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)