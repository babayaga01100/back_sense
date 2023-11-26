from django.contrib import admin

from .models import Post, Report, Mark

# Register your models here.
@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Report)
class ReportModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Mark)
class ReportModelAdmin(admin.ModelAdmin):
    pass