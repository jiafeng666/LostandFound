import os
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render,redirect,reverse
from django.views import View
import re,hashlib
#导出模型对象
from users.models import User, Goods


#util
def hash_str(str, salt='mysite_'):
    # 创建hash对象
    hash = hashlib.sha256()
    # 拼接字符串
    str = str + salt
    # 对字符串进行编码，注意hashlib的update方法只接收bytes类型，所以要进行编码
    hash.update(str.encode())
    # 返回处理过后的密文
    return hash.hexdigest()


# Create your views here.

class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''返回注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''注册表单提交'''
        # 定义错误消息
        message = ''
        # 获取数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # 校验数据
        # 先检验是否有空数据
        if not all([username, password, password2, email, mobile]):
            message = '不要输入空的内容'
            return render(request, 'register.html', {'message': message})

        # 检验用户名，长度5-20个字符
        if not re.match(r'^[a-zA-Z0-9-_]{5,20}$', username):
            message = '请输入5-20位的用户名'
            return render(request, 'register.html', {'message': message})

        # 检验密码，8-20个字符
        if not re.match(r'^[a-z0-9A-Z]{8,20}$', password):
            message = '请输入8-20个字符的密码'
            return render(request, 'register.html', {'message': message})

        # 检验邮箱
        if not re.match(r'^[0-9a-zA-Z-_]+@[0-9a-zA-Z-_]+(\.[0-9a-zA-Z-_]+)+$', email):
            message = '请输入正确的邮箱地址'
            return render(request, 'register.html', {'message': message})

        # 检验手机
        if not re.match(r'^1[3456789]\d{9}$', mobile):
            message = '请输入正确的手机号'
            return render(request, 'register.html', {'message': message})

        # 确认密码
        if password2 != password:
            message = '请输入两个同样的密码'
            return render(request, 'register.html', {'message': message})
        else:
            # 检查用户名是否存在
            check_same_user = User.objects.filter(uname=username)
            if check_same_user:
                message = '用户名已存在'
                return render(request, 'register.html', {'message': message})

            # 手机是否存在
            check_same_mobile = User.objects.filter(mobile=mobile)
            if check_same_mobile:
                message = '手机号已存在'
                return render(request, 'register.html', {'message': message})

            # 邮箱是否已被注册
            check_same_email = User.objects.filter(email=email)
            if check_same_email:
                message = '邮箱已被注册'
                return render(request, 'register.html', {'message': message})

            # 创建用户
            user = User()
            user.uname = username
            user.passwd = hash_str(password)
            user.email = email
            user.mobile = mobile
            user.save()

            # 重定向页面
            return redirect(reverse('users:login'))

class LoginView(View):
    '''登录'''

    def get(self, request):
        '''返回登录界面'''
        return render(request, 'login.html')

    def post(self, request):
        '''验证登录'''
        if request.method == 'POST':
            '''登录验证表单'''
            # 错误信息
            message = ''
            # 获取数据
            username = request.POST.get('username')
            password = request.POST.get('password')
            allow = request.POST.get('allow')

            # 校验数据
            if not all([username, password]):
                message = '请补全用户名/密码'
                return render(request, 'login.html', {'message': message})

            # 检验用户名，长度5-20个字符
            if not re.match(r'^[a-zA-Z0-9-_]{5,20}$', username):
                message = '请输入5-20位的用户名'
                return render(request, 'login.html', {'message': message})

            # 检验密码，8-20个字符
            if not re.match(r'^[a-z0-9A-Z]{8,20}$', password):
                message = '请输入8-20个字符的密码'
                return render(request, 'login.html', {'message': message})

            # 查找用户
            try:
                user = User.objects.get(uname=username)
            except Exception as e:
                message = '用户名不存在！'
                return render(request, 'login.html', {'message': message})

            # 对比密码
            if hash_str(password) != user.passwd:
                '''密码不正确'''
                message = '用户名或密码不正确'
                return render(request, 'login.html', {'message': message})

            # 状态保持
            request.session['islogin'] = True
            request.session['user_id'] = user.id
            request.session['username'] = username
            request.session['email'] = user.email

            # 判断是否勾选 allow
            if allow == 'yes':
                '''已勾选，设置保存天数为两周'''
                request.session.set_expiry(None)
            else:
                '''未勾选，保存到浏览器关闭'''
                request.session.set_expiry(0)

            # 返回用户点击的界面
            # next = request.GET.get('next', '/')

            # 重定向页面
            return redirect(reverse('mysite:index'))

# views.py
class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        # 清除session
        request.session.flush()
        return redirect(reverse('mysite:index'))


class LostView(View):
    '''管理已挂失物界面'''

    def get(self, request):
        # 一查多，使用查询集
        if not request.session.get('islogin',False):
            return redirect(reverse('users:login'))
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        goods_list = user.goods_set.filter(is_delete=False).order_by('-gtime')
        return render(request, 'user_info.html',{'goods_list':goods_list})

class SubmitGoodsView(View):
    '''提交失物的表单'''

    def post(self, request):
        # 获取参数
        goods_name = request.POST.get('goods_info')
        goods_type = request.POST.get('goods_type')
        loss_date = request.POST.get('datetime')
        address = request.POST.get('address')
        img = request.FILES.get('pictureFile')

        # 校验参数
        if not all([goods_name, loss_date, address,img]):
            message = '请补齐参数'
            return render(request, 'user_info.html', {'message': message})

        # 匹配datetime 2020-12-16 14:45
        if not re.match(r'^\d{4}(-\d{2}){2} \d{2}:\d{2}$', loss_date):
            datetime_error = '时间格式不对，请重新输入'
            return render(request, 'user_info.html', {'datetime_error': datetime_error})

        # 转换日期
        loss_date = datetime.strptime(loss_date, '%Y-%m-%d %H:%M')

        # 验证图片拓展名
        types = ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.jfif', '.bmp']
        if os.path.splitext(img.name)[-1].lower() not in types:
            img_error = '请上传正确的图片信息'
            return render(request, 'user_info.html', {'img_error': img_error})

        # 处理表单的提交，并处理上传的文件
        user_id = request.session.get('user_id')
        Goods.objects.create(
            gname=goods_name,
            gtype=goods_type,
            gtime=loss_date,
            address=address,
            img=img,
            user_id=user_id,
        )

        # 响应页面
        return redirect(reverse('users:info'))

class ChangeStatus(View):
    '''改变状态'''

    def get(self, request):
        goods_id = request.GET.get('goods_id')
        try:
            goods = Goods.objects.get(id=goods_id)
            # 做出状态的修改
            goods.status = True
            goods.save()
        except:
            return JsonResponse({'code': '1'})
        return JsonResponse({'code': 0})

class DeleteGoods(View):
    '''删除物品'''

    def get(self, request):
        goods_id = request.GET.get('goods_id')
        try:
            goods = Goods.objects.get(id=goods_id)
            # 做出状态的修改
            goods.is_delete = True
            goods.save()
        except:
            return JsonResponse({'code': '1'})
        return JsonResponse({'code': 0})