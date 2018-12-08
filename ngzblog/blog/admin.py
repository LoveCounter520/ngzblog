from django.contrib import admin

# Register your models here.
from blog import models

# 在Django自带的admin管理后台注册我app中的表，注册以后就能够在admin中做增删改查操作了
admin.site.register(models.UserInfo)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)  # 文章-标签
admin.site.register(models.Category)  # 文章分类
admin.site.register(models.Tag)  # 文章标签
admin.site.register(models.Comment)  # 文章评论
admin.site.register(models.Blog)  # 博客站点
admin.site.register(models.ArticleUpDown)  # 点赞
admin.site.register(models.ArticleDetail)  # 文章详情
