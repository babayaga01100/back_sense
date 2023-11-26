from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class UsernameView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'username': request.user.username}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)