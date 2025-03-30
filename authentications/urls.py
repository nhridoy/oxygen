from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from authentications.views import (
    AdminUserViewSet,
    AppleLoginView,
    FCMDeleteView,
    GithubCallbackView,
    GithubLoginView,
    GithubWebLoginView,
    GoogleCallbackView,
    GoogleLoginView,
    GoogleWebLoginView,
    KakaoCallbackView,
    KakaoLoginView,
    KakaoWebLoginView,
    LoginView,
    LogoutView,
    MyTokenRefreshView,
    NaverCallbackView,
    NaverLoginView,
    NaverWebLoginView,
    OTPLoginView,
    OTPView,
    PasswordViewSet,
    ProfileViewSet,
    RegistrationView,
    ResetPasswordViewSet,
)

router = DefaultRouter()
router.register(r"register", RegistrationView, basename="register")
router.register(r"admin/user", AdminUserViewSet, basename="admin-user")
router.register(r"profile", ProfileViewSet, basename="profile")
router.register(r"otp", OTPView, basename="otp")
router.register(r"password", PasswordViewSet, basename="password")
router.register(r"password-reset", ResetPasswordViewSet, basename="password-reset")

login_urls = [
    path("login/user/", LoginView.as_view(), name="user-login"),
    path("login/admin/", LoginView.as_view(), name="admin-login"),
    path("otp/login/", OTPLoginView.as_view(), name="otp-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("fcm-delete/", FCMDeleteView.as_view(), name="fcm-delete"),
]
otp_urls = [
    # path("otp/", OTPView.as_view(), name="otp"),
]
profile_urls = [
    path(
        "profile/",
        ProfileViewSet.as_view(
            {
                "get": "profile",
                "put": "profile",
                "patch": "profile",
            }
        ),
        name="profile",
    ),
]

social_urls = [
    # We are using these for now
    path("google/", GoogleLoginView.as_view()),
    path("kakao/", KakaoLoginView.as_view()),
    path("naver/", NaverLoginView.as_view()),
    path("github/", GithubLoginView.as_view()),
    path("apple/", AppleLoginView.as_view()),
    # We are not using these for now
    path("kakao-auth/", KakaoWebLoginView.as_view(), name="kakao_login"),
    path("kakao-callback/", KakaoCallbackView.as_view(), name="kakao_callback"),
    path("naver-auth/", NaverWebLoginView.as_view(), name="naver_login"),
    path("naver-callback/", NaverCallbackView.as_view(), name="naver_callback"),
    path("google-auth/", GoogleWebLoginView.as_view(), name="google_login"),
    path("google-callback/", GoogleCallbackView.as_view(), name="google_callback"),
    path("github-auth/", GithubWebLoginView.as_view(), name="github_login"),
    path("github-callback/", GithubCallbackView.as_view(), name="github_callback"),
    # For testing ! TODO: Comment before shipping to production
    path("social/", include("social_django.urls", namespace="social")),
]
urlpatterns = []
urlpatterns += router.urls
urlpatterns += login_urls
urlpatterns += profile_urls
urlpatterns += otp_urls
urlpatterns += social_urls
