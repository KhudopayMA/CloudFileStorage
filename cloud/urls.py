from django.urls import path

from cloud.views import ResourceView

urlpatterns = [
    path("resource", ResourceView.as_view(), name="get_resource"),
]
