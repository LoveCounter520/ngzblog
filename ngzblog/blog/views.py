from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from django import views
from blog.forms import LoginForm, RegisterForm
from django.contrib import auth
from django.views.decorators.cache import never_cache
from blog import models
from utils.mypage import MyPage
from django.db.models import Count, F
from django.db import transaction
import os
from django.conf import settings
from bs4 import BeautifulSoup
# Create your views here.

class Login(views.View):
    def get(self, request):
        form_obj = LoginForm()
        return render(request, "login.html", locals())

    def post(self, request):
        res = {"code": 0}
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        v_code = request.POST.get('v_code')
        # 先判断验证码是否正确
        if v_code.upper() != request.session.get("v_code", ""):
            res["code"] = 1
            res["msg"] = "验证码错误"
        else:
            # 校验用户名密码是否正确
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                auth.login(request, user)
            else:
                # 用户名或密码错误
                res["code"] = 1
                res["msg"] = "用户名或密码错误"
        return JsonResponse(res)


@never_cache
def v_code(request):
    # 随机生成图片
    from PIL import Image, ImageDraw, ImageFont
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    # 生成图片对象
    image_obj = Image.new(
        "RGB",  # 生成图片的模式
        (140, 35),  # 图片大小
        random_color()
    )
    # 生成一个准备写字的画笔
    draw_obj = ImageDraw.Draw(image_obj)  # 在哪里写
    font_obj = ImageFont.truetype('static/font/qs.otf', size=28)  # 加载本地的字体文件

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i*25+10, 0),  # 坐标
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )

    # # 加干扰线
    # width = 140  # 图片宽度（防止越界）
    # height = 35
    # for i in range(5):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=random_color())
    #
    # # 加干扰点
    # for i in range(40):
    #     draw_obj.point([random.randint(0, width), random.randint(0, height)], fill=random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x+4, y+4), 0, 90, fill=random_color())

    v_code = "".join(tmp)  # 得到最终的验证码
    # global V_CODE
    # V_CODE = v_code  # 保存在全局变量不行！！！
    # 将该次请求生成的验证码保存在该请求对应的session数据中
    request.session['v_code'] = v_code.upper()

    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, "png")
    # 从内存读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type="image/png")

class RegView(views.View):
    def get(self, request):
        form_obj = RegisterForm()
        return render(request, "register.html", {"form_obj": form_obj})

    def post(self, request):
        res = {"code": 0}
        # 先进行验证码的校验
        v_code = request.POST.get("v_code", "")
        if v_code.upper() == request.session.get("v_code"):
            # 验证码正确
            form_obj = RegisterForm(request.POST)
            # 使用form做校验
            if form_obj.is_valid():
                # 数据有效
                # 1. 注册用户
                # 注意移除不需要的re_password
                form_obj.cleaned_data.pop("re_password")
                # 拿到用户上传的头像文件
                avatar_file = request.FILES.get("avatar")
                models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_file)
                # 登录成功之后跳转到登录页面
                res["msg"] = '/login/'
            else:
                # 用户填写的数据不正经
                res["code"] = 1
                res["msg"] = form_obj.errors  # 拿到所有字段的错误提示信息
        else:
            res["code"] = 2
            res["msg"] = '验证码错误'
        return JsonResponse(res)


def logout(request):
    auth.logout(request)
    return redirect("/index/")





class Index(views.View):
    def get(self, request):
        article_list = models.Article.objects.all()
        # 分页
        data_amount = article_list.count()
        page_num = request.GET.get("page", 1)
        page_obj = MyPage(page_num, data_amount, per_page_data=5, url_prefix='index')
        # 按照分页的设置对总数据进行切片
        data = article_list[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()
        return render(request, "index.html", {"article_list": data, "page_html": page_html})


def article(request,username,id):
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog = user_obj.blog
    category_list = models.Category.objects.filter(blog=blog)
    tag_list = models.Tag.objects.filter(blog=blog)
    article_obj = models.Article.objects.filter(id=id).first()
    comment_list = models.Comment.objects.filter(article=article_obj)

    return render(request, 'article.html', {
        'blog':blog,
        'username':username,
        'article':article_obj,
        'comment_list':comment_list,
    })


def dianzan(request):
    if request.method == 'POST':
        res = {'code':0}
        user_id = request.POST.get('userId')
        article_id = request.POST.get('articleId')
        is_up = request.POST.get('isUP')
        is_up = True if is_up.upper() == 'TRUE' else False
        article_obj = models.Article.objects.filter(id=article_id,user_id=user_id)
        if article_obj:
            res['code'] = 1
            res['msg'] = '不能给自己的文章点赞!' if is_up else '不能反对自己的内容！'
        else:
            is_exist = models.ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
            if is_exist:
                res['code'] = 1
                res['msg'] = '已经点过赞' if is_exist.is_up else '已经反对过'
            else:
                with transaction.atomic():
                    models.ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
                    if is_up:
                        models.Article.objects.filter(id=article_id).update(up_count=F('up_count')+1)
                    else:
                        models.Article.objects.filter(id=article_id).update(dowm_count=F('dowm_count')+1)
                res['msg'] = '点赞成功' if is_up else '反对成功'
        return JsonResponse(res)



def comment(request):
    if request.method == 'POST':
        res = {'code': 0}
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        user_id = request.user.id
        parent_id = request.POST.get('parent_id')

        with transaction.atomic():
            if parent_id:
                comment_obj = models.Comment.objects.create(content=content,user_id=user_id,article_id=article_id,parent_comment_id=parent_id)
            else:
                comment_obj = models.Comment.objects.create(content=content,user_id=user_id,article_id=article_id)

            models.Article.objects.filter(id=article_id).update(comment_count=F('comment_count')+1)

            res['data'] = {
                'id':comment_obj.id,
                'content':comment_obj.content,
                'create_time':comment_obj.create_time.strftime('%Y-%m-%d %H:%M'),
                'username':comment_obj.user.username,
            }
    return JsonResponse(res)


class Comment(views.View):

    def get(self, request, article_id):
        res = {"code": 0}
        # 根据文章id把评论都找出来
        comment_list = models.Comment.objects.filter(article_id=article_id)
        data = [{
                "id": comment.id,
                "create_time": comment.create_time.strftime("%Y-%m-%d %H:%M"),
                "content": comment.content,
                "pid": comment.parent_comment_id,
                "username": comment.user.username} for comment in comment_list]
        res["data"] = data
        return JsonResponse(res)

    def post(self, request, id):
        res = {"code": 0}
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        user_id = request.user.id
        parent_id = request.POST.get("parent_id")

        # 创建评论内容
        with transaction.atomic():
            # 1. 先去创建新评论
            if parent_id:
                # 添加子评论
                comment_obj = models.Comment.objects.create(content=content, user_id=user_id, article_id=article_id,
                                                            parent_comment_id=int(parent_id))
            else:
                # 添加父评论
                comment_obj = models.Comment.objects.create(content=content, user_id=user_id, article_id=article_id)
            # 2. 去更新该文章的评论数
            models.Article.objects.filter(id=article_id).update(comment_count=F("comment_count") + 1)
            res["data"] = {
                "id": comment_obj.id,
                "content": comment_obj.content,
                "create_time": comment_obj.create_time.strftime("%Y-%m-%d %H:%M"),
                "username": comment_obj.user.username
            }
        return JsonResponse(res)


def home(request,username,*args):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse('404...')
    blog = user_obj.blog

    category_list = models.Category.objects.filter(blog=blog)
    tag_list = models.Tag.objects.filter(blog=blog)

    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={'y_m':"DATE_FORMAT(create_time, '%%Y-%%m')"}
    ).values('y_m').annotate(c=Count('id')).values('y_m','c')

    article_list = models.Article.objects.filter(user=user_obj)

    user_obj = models.UserInfo.objects.filter(username=username).first()
    data_amount = article_list.count()
    page_num = request.GET.get("page", 1)
    page_obj = MyPage(page_num, data_amount, per_page_data=10, url_prefix='index')
    # 按照分页的设置对总数据进行切片
    data = article_list[page_obj.start:page_obj.end]
    page_html = page_obj.ret_html()

    if args:
        if args[0] == 'category':
            article_list = article_list.filter(category__title=args[1])
        elif args[0] == 'tag':
            article_list = article_list.filter(tags__title=args[1])
        else:
            try:
                year, month = args[1].split("-")
                article_list = article_list.filter(create_time__year=year,create_time__month=month)
            except Exception as e:
                article_list = []

    return render(request,'home.html',{'blog':blog,'article_list':article_list,'category_list':category_list,'tag_list':tag_list,'archive_list':archive_list,'user':user_obj,'username':username,'page_html':page_html,})
