import json
from rest_framework.permissions import IsAuthenticated, AllowAny  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import status  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from account.serializers import UserSerializer
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, logout, authenticate
from .models import Accounts
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import account_activation_token
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
# import threading
# import validate_email
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from validate_email import validate_email  # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView  # type: ignore

# Create your views here.

# You will find the API's View below.


# User Register View


def register_view(request):
    if request.user.is_authenticated:
        print("Your are already Logged In")
    context = {}

    if request.POST:

        form = RegisterForm(request.POST or None)

        if form.is_valid():
            user_form = form.save()
            # print(user_form)
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            # print(user)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect("index")
                else:
                    print("User not active")
            else:
                print("Invalid User")
        else:
            print(form.errors.as_data())
            context["reg_form"] = form
    else:
        print("Http request not valid")
    return render(request, 'account/register.html', context)


# User Login View
def login_view(request):
    context = {}
    if request.method == "POST":
        login_form = LoginForm(request.POST or None)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']

            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    destination = get_redirect_if_exist(request)
                    if destination:
                        return redirect(destination)
                    return redirect("index")
        context["login_form"] = login_form

    return render(request, 'account/login.html', context)


def get_redirect_if_exist(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get('next'))
    return redirect


# User logout View
@login_required
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')


# User Reset Password Form.
'''
Here Pasword reset Link is being sent to a regestered email
'''


def forgot_password(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get('email')
        # print(email)

        context = {
            'values': request.POST
        }

        current_site = get_current_site(request)
        user = Accounts.objects.filter(email=email)
        if user.exists():
            email_content = {
                'user': user[0],
                'doamin': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            }

            link = reverse('reset-user-pass', kwargs={
                'uidb64': email_content['uid'], 'token': email_content['token']
            })

            reset_url = f'http://{current_site.domain}{link}'

            message = f"Hi {user[0].username}, Click the link below to reset your password\n {reset_url}"
            print(message)

            messages.success(
                request, f"You copy the link in the console")
            redirect('login')
        else:
            messages.success(
                request, "Account not valid, Kindly provide a valid email account")
            redirect('forgot-password')
    return render(request, 'account/forget_password_form.html', context)


# User Reset Password
def resetPass(request, uidb64, token):
    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.info(request, "Password deos not match")
            return render(request, "account/password_reset_form.html")
        if len(password1) < 6:
            messages.info(request, "Password too short")
            return render(request, "account/password_reset_form.html")

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = Accounts.objects.get(pk=user_id)
            user.set_password(password1)
            user.save()
            if PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password link invalid, Pls request for a new one')
                return redirect('forgot-password')
            messages.info(request, "Password was set successfully")
            return redirect('login')
        except Exception as identifier:
            messages.info(request, 'something went wrong')
            return render(request, "account/reset_password_form.html")
    else:
        print("Enter something")
    return render(request, "account/password_reset_form.html")


# --------------------------------------- API VIEWS ----------------------------------------------

# REGISTER USER API
class RegisterApi(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        user_register = UserSerializer(data=request.data or None)
        if user_register.is_valid():
            user = user_register.save()
            user.set_password(user.password)
            user.save()
            data = {
                "msg": "Registration Successful"
            }
            return Response(data=data, status=status.HTTP_200_OK)
        data = {
            "msg": "Error Registration"
        }
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


# GET MANUAL JWT FOR USER


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'token': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "user": {
                'username': user.username,
                'name': f'{user.first_name} {user.last_name}'
            },
            "name": f'{user.first_name} {user.last_name}'
        },
        'msg': 'Login Successfully'
    }

# LOGIN USER API VIEW


@api_view(['POST',])
@permission_classes((AllowAny,))
def login_api(request,):
    email = request.data["email"]
    password = request.data["password"]
    user = authenticate(email=email, password=password)
    if user:
        if user.is_active:
            login(request, user)
            data = get_tokens_for_user(user)
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response({"msg": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

# VERIFY EMAIL API VIEW


class VerifyEmail(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        data = {}
        data_json = json.loads(request.body)
        email = data_json.get("email")
        get_email = Accounts.objects.filter(email=email)
        is_email = validate_email(email)
        if get_email.exists():
            data["msg"] = "Email Already Exist"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        elif is_email:
            data["msg"] = "Email Valid"
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data['msg'] = "Invalid Email"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

# LOGOUT API VIEW


class LogoutApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            data = {
                "msg": "Logout Successfully"
            }
            return Response(data=data, status=status.HTTP_200_OK)


class UserApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        data = {}
        if request.user.is_authenticated:
            user_id = request.user.id
            user = Accounts.objects.get(pk=user_id)
            user_serializer = UserSerializer(user)
            data = {
                'msg': user_serializer.data
            }
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {
                'msg': "Error User Data"
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token["name"] = f'{user.first_name} {user.last_name}'
        token['profile_pic'] = f'{settings.BASE_URL}{user.profile_image.url}'
        return token


class MyTokenObatinPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
