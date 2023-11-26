from django.urls import path

from users.views import UsernameView

app_name = 'users'

urlpatterns = [
    path('username/', UsernameView.as_view(), name='user-username'),
]