from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    Group as _DjangoGroup,
    Permission as _DjangoPermission,
    UserManager,
)

# Create your models here.


class User(AbstractUser):
    objects = UserManager()

    class Meta:
        db_table = "auth_user"


class Group(_DjangoGroup):
    class Meta:
        proxy = True


class Permission(_DjangoPermission):
    class Meta:
        proxy = True
