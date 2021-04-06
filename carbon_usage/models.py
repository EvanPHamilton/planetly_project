from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UsageType(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Usage(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    usage_type = models.ForeignKey(UsageType, on_delete=models.CASCADE)
    usage_at = models.DateTimeField('usage date')

    def __str__(self):
        return self.usage_type.name
