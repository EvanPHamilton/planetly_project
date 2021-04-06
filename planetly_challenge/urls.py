from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from carbon_usage import views as views
from rest_framework.authtoken.views import obtain_auth_token

"""
Define project wide routes in this folder
"""

urlpatterns = [
    # Carbon usage app
    path('carbon_usage/', include('carbon_usage.urls')),
    # Admin app
    path('admin/', admin.site.urls),
    # Get auth token
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # Sign up
    path('signup/', views.signup, name='signup'),
    #Account login/home page
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
