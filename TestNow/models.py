from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    university = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

'''
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    university = models.CharField(max_length=100, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    username = models.CharField(max_length=50, unique=True)
    last_login = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.email})"
'''

class ClassTable(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    university = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('class_name', 'university')

    def __str__(self):
        return f"{self.class_name} ({self.university})"


class UserClass(models.Model):
    user_class_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_model = models.ForeignKey(ClassTable, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.class_model.class_name}"


class FlashCardSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    set_name = models.CharField(max_length=100)
    class_model = models.ForeignKey(ClassTable, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.set_name} by {self.user.username}"


class FlashCards(models.Model):
    card_id = models.AutoField(primary_key=True)
    flash_card_set = models.ForeignKey(FlashCardSet, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Card in {self.flash_card_set.set_name}: {self.question}"


class ActivityLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_done = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log by {self.user.username}: {self.action_done} at {self.timestamp}"
