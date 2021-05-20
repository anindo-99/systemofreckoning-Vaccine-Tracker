from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from.views import CustomLoginView

urlpatterns = [
    path('', views.home, name="home"),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('login/', views.loginPage, name="login"),
    # path('handlogin/', views.handleLogin, name="handlelogin"),
    path('register/', views.registerPage, name="register"),
    path('handleregister/', views.handleRegister, name="handleregister"),
]
