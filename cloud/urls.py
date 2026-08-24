from django.urls import path

from cloud.views import ResourceView, ResourceDownloadView

urlpatterns = [
    path("resource", ResourceView.as_view(), name="get_resource"),
    path("resource/download", ResourceDownloadView.as_view(), name="download_resource"),
]
