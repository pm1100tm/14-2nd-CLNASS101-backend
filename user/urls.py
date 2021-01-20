from django.urls import path
from .views import SignUpView, SignInView, SocialSignInKaKaoView, SearchView, MyPageView

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/social-sign-in', SocialSignInKaKaoView.as_view()),
    path('/search', SearchView.as_view()),
    path('/my-page', MyPageView.as_view()),
]
