#Developer : SURENDRA 
#date : 2-Oct-2022
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import LocalUser, GmailAccount, UserProfile, Company
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from knox.auth import TokenAuthentication

from itertools import chain
from operator import attrgetter


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'email', 'first_name', 'last_name', 'company_name', 'regular')


class LoginSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=300)
    password = serializers.CharField(max_length=300)



    def validate(self, data):
        user = authenticate(**data)
        # print(user)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials ")


class RegisterSerializer(serializers.HyperlinkedModelSerializer):
 
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    company_name = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    regular = serializers.BooleanField(default=False)

    def myqueryset(self):
        queryset = list(sorted(chain(
            UserProfile.objects.filter(UserProfile.objects.all()),
            LocalUser.objects.filter(LocalUser.objects.all())
        ),
            key=attrgetter('email'),
        ))
        return queryset

    email = serializers.EmailField(validators=[UniqueValidator(
                                                queryset=LocalUser.objects.all(),
                                                message="A user with email already exists")
                                            ])

    class Meta:
        # model = User
        model = LocalUser
        fields = ('id', 'company_name', 'email', 'password', 'date_of_birth', 'first_name', 'last_name', 'regular')

    authentication_classes = (
        TokenAuthentication,
    )

    def create(self, validated_data, *args, **kwargs)



        userprofile = UserProfile.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            company_name=validated_data['company_name'],
            regular = validated_data['regular']
        )
        # CALLING SAVE IS IMPORTANT
        userprofile.save()

        if userprofile:
            user = LocalUser.objects.create_user(

                validated_data['email'],
                userprofile,
                validated_data['date_of_birth'],
                validated_data['password'],

            )


            user.save()
        if user and userprofile:

            return userprofile

        raise serializers.ValidationError("Incorrect data")


# User Serializer
class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())

    class Meta:
        model = LocalUser
        fields = ('id', 'username', 'email', 'profile_id')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name', 'address', 'gst', 'employees', 'disabled', 'allotted')

    def validate_used_till_date(self, value):
        qs = Company.objects.all()

        return value

