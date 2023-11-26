from django.views.decorators.csrf import requires_csrf_token
from django.utils.decorators import method_decorator

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Post, Report, Mark
from .serializers import PostCreateRetrieveModelSerializer, MarkedPostRetrieveModelSerializer


# Create your views here.
# 단어 다 가져오기
class PostListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Post.objects.all()
    serializer_class = PostCreateRetrieveModelSerializer

# 단어 상세보기
class PostRetrieveView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateRetrieveModelSerializer
    
# 첫 번째 단어 가져오기
class FirstPostRetrieveView(APIView):
    def get(self, request):
        try:
            first_post = Post.objects.earliest('id')
            first_post_serializer = PostCreateRetrieveModelSerializer(first_post)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(first_post_serializer.data, status=status.HTTP_200_OK)

# 단어 생성하기
@method_decorator(requires_csrf_token, name='dispatch')
class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateRetrieveModelSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            Post.objects.get(word=request.data['word'])
            return Response({'detail': 'Already Existed'}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            prev_post = Post.objects.latest('id')
            prev_id = prev_post.id
            next_id = Post.objects.only('id').earliest('id').id
        except Post.DoesNotExist:
            # 처음 단어 생성하는 경우
            prev_post = None
            prev_id = None
            next_id = None

        serializer.save(writer=request.user, prev_id=prev_id, next_id=next_id)

        # 처음/이전 단어 업데이트하기
        cur_post = Post.objects.only('id').latest('id')
        if prev_post:
            post_count = Post.objects.all().count()
            cur_id = cur_post.id

            # 처음 단어 업데이트하기
            first_post = Post.objects.earliest('id')
            first_post.prev_id = cur_id

            # 이전 단어 업데이트하기
            if post_count == 2:
                first_post.next_id = cur_id
            else:
                prev_post.next_id = cur_id
                prev_post.save()

            first_post.save()
        else:
            # 처음 단어 생성하는 경우
            cur_post.prev_id = cur_post.id
            cur_post.next_id = cur_post.id
            cur_post.save()
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
# 단어 신고하기
class PostReportView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        queryset = Report.objects.filter(post=post)

        # 이미 신고한 사용자 → 신고 X
        for query in queryset:
            if query.writer == request.user:
                return Response({'detail': 'Already Reported'}, status=status.HTTP_400_BAD_REQUEST)
        # 신고
        report = Report(post=post, writer=request.user)
        report.save()

        # 신고 3번 → 단어 삭제
        if queryset.count() == 2:
            prev_id = post.prev_id
            next_id = post.next_id

            post.delete()

            # 이전/다음 단어 업데이트하기
            post_count = Post.objects.all().count()
            if post_count == 1:
                # 남은 단어 업데이트하기
                post = Post.objects.get()
                post.prev_id = post.id
                post.next_id = post.id
                post.save()
            elif post_count > 1:
                # 이전 단어 업데이트하기
                prev_post = Post.objects.get(id=prev_id)
                prev_post.next_id = next_id
                prev_post.save()
                
                # 다음 단어 업데이트하기
                next_post = Post.objects.get(id=next_id)
                next_post.prev_id = prev_id
                next_post.save()

            return Response({'detail': 'Deleted Post Successfully'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Reported Post Successfully'}, status=status.HTTP_201_CREATED)
    
# 저장한 단어 가져오기
class MarkedPostRetrieveView(APIView):
    def get(self, request, pk):
        try:
            mark = Mark.objects.get(id=pk, writer=request.user)
            marked_post_serializer = MarkedPostRetrieveModelSerializer(mark)
        except Mark.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(marked_post_serializer.data, status=status.HTTP_200_OK)
    
# 저장한 첫 번째 단어 가져오기
class FirstMarkedPostRetrieveView(APIView):
    def get(self, request):
        try:
            first_mark = Mark.objects.filter(writer=request.user).earliest('id')
            marked_first_post_serializer = MarkedPostRetrieveModelSerializer(first_mark)
        except Mark.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(marked_first_post_serializer.data, status=status.HTTP_200_OK)
    
# 단어 저장/저장 취소하기    
class PostMarkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # 단어가 있는 경우
            post = Post.objects.get(id=pk)
        except:
            # 단어가 없는 경우
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # 단어를 이미 저장한 경우: 단어 저장 취소하기
            mark = Mark.objects.get(post=post, writer=request.user)

            prev_id = mark.prev_id
            next_id = mark.next_id

            mark.delete()  # 단어 저장 취소하기
            
            # 이전/다음 저장한 단어 업데이트하기
            mark_count = Mark.objects.filter(writer=request.user).count()
            if mark_count == 1:
                # 남은 저장한 단어 업데이트하기
                mark = Mark.objects.get()
                mark.prev_id = mark.id
                mark.next_id = mark.id
                mark.save()
            elif mark_count > 1:
                # 이전 단어 업데이트하기
                prev_mark = Mark.objects.get(id=prev_id)
                prev_mark.next_id = next_id
                prev_mark.save()

                # 다음 단어 업데이트 하기
                next_mark = Mark.objects.get(id=next_id)
                next_mark.prev_id = prev_id
                next_mark.save()
            
            return Response({'detail': 'Canceled Marking Post Successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Mark.DoesNotExist:
            # 단어를 저장하지 않은 경우: 단어 저장하기
            try:
                prev_mark = Mark.objects.filter(writer=request.user).latest('id')
                prev_id = prev_mark.id
                next_id = Mark.objects.filter(writer=request.user).earliest('id').id
            except Mark.DoesNotExist:
                # 처음 단어를 저장하는 경우
                prev_mark = None
                prev_id = None
                next_id = None
            
            # 단어 저장하기
            mark = Mark(post=post, writer=request.user, prev_id=prev_id, next_id=next_id)
            mark.save()

            # 저장한 처음/이전 단어 업데이트하기
            cur_mark = Mark.objects.only('id').latest('id')
            if prev_mark:
                mark_count = Mark.objects.all().count()
                cur_id = cur_mark.id

                # 처음 단어 업데이트 하기
                first_mark = Mark.objects.earliest('id')
                first_mark.prev_id = cur_id

                # 이전 단어 업데이트하기
                if mark_count == 2:
                    first_mark.next_id = cur_id
                else:
                    prev_mark.next_id = cur_id
                    prev_mark.save()
                
                first_mark.save()
            else:
                # 처음 단어를 저장하는 경우
                cur_mark.prev_id = cur_mark.id
                cur_mark.next_id = cur_mark.id
                cur_mark.save()

            return Response({'datail': 'Marked Post Successfully'}, status=status.HTTP_201_CREATED)