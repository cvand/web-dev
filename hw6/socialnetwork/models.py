from django.db import models
from datetime import datetime
from django.db.models.signals import post_delete
from django.dispatch import receiver

# User class for built-in authentication module
from django.contrib.auth.models import User
    
class Comment(models.Model):
    comment = models.TextField(max_length=160, blank=False)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(default=datetime.now, editable=False)
    
    def __unicode__(self):
        return self.comment
    
    class Meta:
        get_latest_by = 'creation_date'

class Post(models.Model):
    post_content = models.TextField(max_length=160)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(default=datetime.now, editable=False)
    comments = models.ManyToManyField(Comment, related_name="comments+")
    
    def __unicode__(self):
        return self.post_content
    
    class Meta:
        get_latest_by = 'creation_date'
      
class UserInfo(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    age = models.IntegerField(blank=True, null=True)
    short_bio = models.TextField(max_length=430, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='uploads/')
    content_type = models.CharField(max_length=50)
    
@receiver(post_delete, sender=UserInfo)
def image_post_delete_handler(sender, **kwargs):
    UserInfo = kwargs['instance']
    storage, path = UserInfo.image.storage, UserInfo.image.path
    storage.delete(path)
    
class Followers(models.Model):
    follower = models.ForeignKey(User)
    following = models.ForeignKey(UserInfo)
