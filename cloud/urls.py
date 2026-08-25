from django.urls import path

from cloud.views import ResourceView, ResourceDownloadView, ResourceMoveView

urlpatterns = [
    path("resource", ResourceView.as_view(), name="resource"),
    path("resource/download", ResourceDownloadView.as_view(), name="download_resource"),
    path("resource/move", ResourceMoveView.as_view(), name="move_resource")
]
