from django.db import models
# Create your models here.

class users(models.Model):
    username = models.CharField(max_length=20,primary_key=True)
    password = models.CharField(max_length=20)
    is_superuser = models.BooleanField(default=0)


class news(models.Model):
    number = models.CharField(max_length=20,primary_key=True)
    category = models.CharField(max_length=20,null=False)
    title = models.CharField(max_length=100,null=False)
    date = models.CharField(max_length=20,null=False)
    content = models.TextField(null=False)
    count = models.IntegerField(null=False,default=0)    
    def __str__(self):
        return "<news:(number:%s,category:%s,title:%s,date:%s,content:%s,count:%s)>"%(self.number,self.category,self.title,self.date,self.content,self.count)
    


#生成迁移脚本文件
#python  manage.py makemigrations

#将新生成的迁移脚本映射到数据库
#python  manage.py migrate

#会自动检测模型的增删改查

