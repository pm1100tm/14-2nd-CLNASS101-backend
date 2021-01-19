from django.urls import path
from .views import SignUpView, LogInView, KakaoLogInView, SearchView, MyPageView

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', LogInView.as_view()),
    path('/social-sign-in', KakaoLogInView.as_view()),
    path('/search', SearchView.as_view()),
    path('/my-page', MyPageView.as_view()),
]
