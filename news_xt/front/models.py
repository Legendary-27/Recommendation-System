from django.db import models

class user_center(models.Model):
    username = models.ForeignKey('cms.users',on_delete=models.CASCADE)
    news_id = models.ForeignKey('cms.news',on_delete=models.CASCADE)
    

