from django.db import models

# Create your models here.
class User(models.Model):
    '''用户模型'''

    uname = models.CharField(max_length=128, unique=True)
    passwd = models.CharField(max_length=256)  # 留意这个数字，后面会解释
    email = models.EmailField(unique=True)
    ctime = models.DateTimeField(auto_now_add=True)
    mobile = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __srt__(self):
        # 每次输出对象时，输出的是uname
        return self.uname


class Goods(models.Model):
    '''失物模型'''

    gname = models.CharField(max_length=128)
    gtype = models.CharField(max_length=128,default=False)
    gtime = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=128)
    status = models.BooleanField(default=False)
    img = models.ImageField(upload_to='goods/')  # 图片上传，upload_to 结合 media_root 的路径
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 外键关联user
    is_delete = models.BooleanField(default=False)

    class Meta:
        verbose_name = '失物物品'
        verbose_name_plural = '失物物品'

    def __srt__(self):
        # 每次输出对象时，输出的是uname
        return self.gname