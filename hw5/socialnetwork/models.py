from django.db import models
from datetime import datetime

# User class for built-in authentication module
from django.contrib.auth.models import User

class Post(models.Model):
    post_content = models.TextField(max_length=160)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(default=datetime.now, editable=False)
    
    def __unicode__(self):
        return self.post_content
    
    class Meta:
      get_latest_by = 'creation_date'