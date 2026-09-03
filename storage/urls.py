from django.urls import path

from storage.views import ResourceView, ResourceDownloadView, ResourceMoveView, DirectoryView, ResourceSearchView

urlpatterns = [
    path("resource", ResourceView.as_view(), name="resource"),
    path("resource/download", ResourceDownloadView.as_view(), name="download_resource"),
    path("resource/move", ResourceMoveView.as_view(), name="move_resource"),
    path("directory", DirectoryView.as_view(), name="directory"),
    path("resource/search", ResourceSearchView.as_view(), name="search_resource")
]
