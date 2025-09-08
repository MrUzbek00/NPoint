from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.

def unique_slug(instance, base):
    base = slugify(base) or "item"
    Model = instance.__class__
    slug = base
    i = 2
    qs = Model.objects.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug



class UserProfile(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class JSONData(models.Model):

    json_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='json_data')
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True, max_length=500)
    json_picture = models.ImageField(upload_to='json_pictures/', blank=True, null=True)
    json_content = models.JSONField()
    json_api = models.CharField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=220, blank=True, null=True)  # or unique_together with user
    access_count = models.PositiveIntegerField(default=0)
    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = unique_slug(self, self.title)
        else:
            old = type(self).objects.only("title").filter(pk=self.pk).first()
            if old and old.title != self.title:
                self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        constraints = [
            # optional, add after population step:
            models.UniqueConstraint(fields=["user", "slug"], name="uniq_user_slug"),
        ]
        indexes = [models.Index(fields=['title'])]

    def __str__(self):
        return self.title
    
class PasswordResetCode(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reset_codes')
    reset_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset code for {self.user.username}"