#Developer : SURENDRA 
#date : 2-Oct-2022
from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.response import Response

from requests.exceptions import HTTPError
from django.contrib.auth import login
from rest_framework.exceptions import PermissionDenied
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from .models import LocalUser, GmailAccount, UserProfile, Company

from .serializers import (
                        UserSerializer,
                          RegisterSerializer,
                          LoginSerializer,

                        UserProfileSerializer,
                        CompanySerializer
                          )


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        fortoken = LocalUser.objects.get(profile_id=user)

        return Response({
            "user": UserProfileSerializer(user, context=self.get_serializer_context()).data,

            "token": AuthToken.objects.create(fortoken)[1]
        })


# Login API
class LoginAPI(generics.GenericAPIView):
    # login_url = 'api/auth/login/'
    print("BEFORE SERIALIZER CLASS")
    permission_classes = [
    ]

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        print("REQUEST.DATA = " + str(request.data))
        serializer = self.get_serializer(data=request.data)
        print("BEFORE IS_VALID IS CALLED! ")
        serializer.is_valid(raise_exception=True)

        print(str(serializer))

        user = serializer.validated_data
        userprofile = UserProfile.objects.get(localuser=user)
        # login(request, user)
        return Response({
            "user": UserProfileSerializer(userprofile, context=self.get_serializer_context()).data,
            # "token": AuthToken.objects.create(user)[1]
            "token": AuthToken.objects.create(user=user)[1],
        })

class UserAPI(generics.RetrieveAPIView):

    permission_classes = [

        permissions.IsAuthenticated,
        # permissions.AllowAny,
    ]

    authentication_classes = (
        TokenAuthentication,
    )

    queryset = UserProfile.objects.all()

    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(localuser=self.request.user)

    def get_object(self):
        return UserProfile.objects.get(localuser=self.request.user)



class UserViewSet(viewsets.ModelViewSet):
    queryset = LocalUser.objects.all()
    serializer_class = UserSerializer

    authentication_classes = (
        TokenAuthentication,
    )

    # print(permissions.IsAuthenticated)

    def retrieve(self, request, pk=None):
        print("User is "+self.request.user)


class CompanyAPIView(
                    viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    viewsets.mixins.UpdateModelMixin,
                    viewsets.mixins.RetrieveModelMixin,
                    viewsets.mixins.DestroyModelMixin):

    serializer_class = CompanySerializer

    queryset = Company.objects.all()

    def get_queryset(self):
        return Company.objects.all()

    def create(self, request, *args, **kwargs):
        print("INSIDE CREATE!! ")
        serializer = self.get_serializer(data=request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.is_admin:
            raise PermissionDenied("You cannot create company if you are not admin")
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

