from django.db import models
class ApprovedCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(state='registered')


