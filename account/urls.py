from django.urls import path
from .views import register_view, login_view, logout_view, forgot_password, resetPass, RegisterApi, login_api, VerifyEmail, LogoutApi
from rest_framework_simplejwt.views import ( # type: ignore
    TokenRefreshView,
)



urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-pass/<uidb64>/<token>', resetPass, name='reset-user-pass'),

    # ------------------------- API ENDPOINTS -----------------------------
    path('register_api/', RegisterApi.as_view(), name='register-api'),
    path('login_api/', login_api, name='login-api'),
    path('verify_email/', VerifyEmail.as_view(), name='verify-email'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout_api/', LogoutApi.as_view(), name="logout-api")
]
