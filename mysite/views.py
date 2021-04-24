from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse

from django.views import View
from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from users.models import Goods, User


# Create your views here.
# def index(request):
#     # 判断是否是get请求
#     if request.method == 'GET':
#         # 返回并渲染模板文件
#         return render(request, 'index.html')



class IndexView(View):
    '''首页'''

    def get(self, request):
        # 获取页码
        page_num = request.GET.get('page_num', 1)  # 首页就是默认的页码
        # 查询所有物品
        goods = Goods.objects.filter(is_delete=False).order_by('-gtime')

        # 分页操作
        try:
            paginator = Paginator(goods, 4)
            # 获取当前页的对象
            goods_list = paginator.page(int(page_num))
            # 总页数
            total_num = paginator.page_range
        except:
            return render(request, 'index.html')

        # 响应上下文
        context = {
            'total_num': total_num,
            'goods_list': goods_list
        }

        return render(request, 'index.html', context)

class SentEmailVial(View):
    def get(self, request):
        email = request.session.get('email')
        user_id = request.session.get('user_id')
        serializer = Serializer(settings.SECRET_KEY, 300)
        token = serializer.dumps({'user_id': user_id})
        token = token.decode()
        verify_url = 'http://127.0.0.1:8000/email/verification/?token=' + token
        subject = '校园便利中心邮箱验证'
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用校园失物管理中心。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p>%s</p>' \
                       '<p><a href="%s">点击激活</a></p>' % (email, verify_url, verify_url)
        try:
            send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)
        except:
            return JsonResponse({'code': 0})
        return JsonResponse({'code': 1})

class VerificationEmail(View):
    def get(self, request):
        serializer = Serializer(settings.SECRET_KEY, 300)
        token = request.GET.get('token')
        try:
            data = serializer.loads(token)
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return redirect(reverse('mysite:index'))
        except BadData:
            return None