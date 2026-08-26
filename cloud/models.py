from django.db import models


class Folder(models.Model):
    id = models.BigAutoField("id", primary_key=True)
    name = models.CharField("name")
    folder = models.ForeignKey(
        "self",
        related_name="folders",
        on_delete=models.CASCADE,
        null=True)
    # path = models.CharField("full_path", unique=True)

    class Meta:
        db_table = "folder"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "folder_id"], name="unique_folder_name_folder_id"
            )
        ]


class File(models.Model):
    id = models.BigAutoField("id", primary_key=True)
    name = models.CharField("name")
    folder = models.ForeignKey(
        Folder,
        related_name="files",
        on_delete=models.CASCADE
    )
    # path = models.CharField("full_path", unique=True)
    size = models.BigIntegerField("size")

    class Meta:
        db_table = "file"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "folder_id"], name="unique_file_name_folder_id"
            )
        ]
