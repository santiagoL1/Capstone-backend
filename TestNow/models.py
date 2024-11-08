from django.db import models

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


class Class(models.Model):
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
    class_model = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.class_model.class_name}"


class FlashCardSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    set_name = models.CharField(max_length=100)
    class_model = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.set_name} by {self.user.username}"


class FlashCard(models.Model):
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
