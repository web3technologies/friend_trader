from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid as uuid4


class FriendTraderUserManager(BaseUserManager):
    def create_user(self, public_address, password=None, **extra_fields):
        if not public_address:
            raise ValueError(('The public address must be set'))
        user = self.model(public_address=public_address, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, public_address, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))
        return self.create_user(public_address, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    public_address = models.CharField(max_length=255, unique=True, default=None)
    nonce = models.UUIDField(default=uuid4.uuid4, editable=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'public_address'
    REQUIRED_FIELDS = []

    objects = FriendTraderUserManager()

    def __str__(self):
        return self.public_address


class Connection(models.Model):

    ip_address = models.CharField(max_length=255, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_connected = models.DateTimeField(auto_now_add=True)
    #status = successful || failure