from django.urls import path

from posts.views import PostListView, PostRetrieveView, FirstPostRetrieveView, PostCreateView, PostReportView, MarkedPostRetrieveView, FirstMarkedPostRetrieveView, PostMarkView

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostRetrieveView.as_view(), name='post-detail'),
    path('first-post/', FirstPostRetrieveView.as_view(), name='first-post-detail'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('report/<int:pk>/', PostReportView.as_view(), name='post-report'),
    path('marked/<int:pk>/', MarkedPostRetrieveView.as_view(), name='marked-post-detail'),
    path('first-marked-post/', FirstMarkedPostRetrieveView.as_view(), name='first-marked-post-detail'),
    path('mark/<int:pk>/', PostMarkView.as_view(), name='post-mark'),
]