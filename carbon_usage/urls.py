from django.urls import path, include
from rest_framework import routers
from . import views

"""
Define carbon_usage api routes here
Which are all handled by the router
"""

router = routers.DefaultRouter()
router.register(r'usage_type', views.UsageTypeViewSet)
router.register(r'usage', views.UsageViewSet, 'usage-list')

urlpatterns = [
    # Include router urls
    path('', include(router.urls)),
]
