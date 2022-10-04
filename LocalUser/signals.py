#Developer : SURENDRA 
#date : 2-Oct-2022
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created, post_password_reset
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.response import Response
from .serializers import CustomTokenSerializer
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.utils import timezone
from datetime import timedelta

site_url = "127.0.0.1:8000/api"



class CustomPasswordResetView:
    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, reset_password_token, *args, **kwargs):


        # send an email to the user
        context = {
            'current_user': reset_password_token.user,
            'username': reset_password_token.user.username,
            'email': reset_password_token.user.email,
            'reset_password_url': "{}/password-token/token/{}".format(site_url, reset_password_token.key),
            'site_name': site_shortcut_name,
            'site_domain': site_url
        }

        # render email text
        email_html_message = render_to_string('email/user_reset_password.html', context)
        print("EMAIL HTMOL MESSAGE = "+email_html_message)
        email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
        print('EMAIL PALINTEXT '+email_plaintext_message)
        msg = EmailMultiAlternatives(
            # title:
            "Password Reset for {}".format(site_full_name),

            # message:
            email_plaintext_message,

            # from:
            "noreply@ {}".format(site_url),

            # to:
            [reset_password_token.user.email]
        )

        msg.attach_alternative(email_html_message, "text/html")
        msg.send()


class CustomPasswordTokenVerificationView(APIView):

    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer, )
    serializer_class = CustomTokenSerializer

    @receiver(post_password_reset)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        # get token validation time
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # find token
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()

        if reset_password_token is None:
            return Response({
                'status': 'invalid'
            }, status=status.HTTP_404_NOT_FOUND)

        # check expiry date
        expiry_date = reset_password_token.created_at + timedelta(hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
     
            reset_password_token.delete()
            return Response({
                'status': 'expired'
            }, status=status.HTTP_404_NOT_FOUND)

     
        if not reset_password_token.user.has_usable_password():
            return Response({'status': 'irrelevant'})

        return Response({'status': 'OK'})

