from django.db import models


class Folder(models.Model):
    id = models.BigAutoField("id", primary_key=True)
    name = models.CharField("name")
    folder_id = models.ForeignKey("self", on_delete=models.CASCADE)

    class Meta:
        db_table = "folder"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "folder_id"], name="unique_name_folder_id"
            )
        ]


class File(models.Model):
    id = models.BigAutoField("id", primary_key=True)
    name = models.CharField("name")
    folder_id = models.ForeignKey(Folder, on_delete=models.CASCADE)

    class Meta:
        db_table = "file"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "folder_id"], name="unique_name_folder_id"
            )
        ]
