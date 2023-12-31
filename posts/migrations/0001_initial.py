# Generated by Django 4.2.4 on 2023-08-08 05:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.TextField(verbose_name='단어')),
                ('meaning', models.TextField(verbose_name='의미')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='작성일')),
                ('report_count', models.IntegerField(default=0, verbose_name='신고 수')),
                ('writer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
