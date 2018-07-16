from django.shortcuts import render,redirect,HttpResponse,reverse
from django.contrib import auth
from CNBLOG.models import Article,UserInfo,Comment,ArticleUpDown,Article2Tag,Category,Tag
import json
from django.http import JsonResponse
from django.db.models import F
from django.db import transaction
from bs4 import BeautifulSoup
from xwblog import settings
import os

from django.db.models import Count

def login(request):

    if request.method == "POST":

        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        user = auth.authenticate(username=user,password=pwd)

        if user:
            auth.login(request,user)
            return redirect('/index/')

    return render(request,'login.html')

def index(request):

    article_list = Article.objects.all()

    return render(request,'index.html',{'article_list':article_list})

def logout(request):

    auth.logout(request)

    return redirect('/index/')

def homesite(request,username,**kwargs):
    """
    查询
    :param request:
    :param username:
    :return:
    """

    print("kwargs",kwargs)


    # 查询当前站点的用户对象
    user=UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,"not_found.html")
    # 查询当前站点对象
    blog=user.blog

    # 查询当前用户发布的所有文章
    if not kwargs:
        article_list=Article.objects.filter(user__username=username)

    else:
        condition=kwargs.get("condition")
        params=kwargs.get("params")

        if condition=="category":
            article_list=Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition=="tag":
            article_list = Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            year,month=params.split("/")
            article_list=Article.objects.filter(user__username=username).filter(create_time__year=year,create_time__month=month)


    if not article_list:
        return render(request,"not_found.html")

    return render(request,"homesite.html",locals())

def article_detail(request,username,article_id):

    user = UserInfo.objects.filter(username=username).first()

    blog = user.blog

    article_obj = Article.objects.filter(pk=article_id).first()

    comment_list = Comment.objects.filter(article_id = article_id)

    return render(request,'article_detail.html',locals())

def digg(request):
    print(request.POST)
    # bool值
    is_up = json.loads(request.POST.get("is_up"))
    article_id = request.POST.get("article_id")
    user_id = request.user.pk
    response ={"state":True,"msg":None}

    obj = ArticleUpDown.objects.filter(user_id = user_id,article_id=article_id).first()
    if obj:
        response["state"]=False
        response["handled"]=obj.is_up

    else:
        with transaction.atomic():
            new_obj = ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)

            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)
    return JsonResponse(response)

def comment(request):

    user_id = request.user.pk
    article_id = request.POST.get('article_id')
    content = request.POST.get("content")
    pid = request.POST.get("pid")

    with transaction.atomic():
        comment = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response={"state":True}
    response["timer"]=comment.create_time.strftime("%Y-%m-%d %X")
    response["content"]=comment.content
    response["user"]=request.user.username

    return JsonResponse(response)

def backend(request):
    user = request.user
    article_list = Article.objects.filter(user=user)
    return render(request,'backend/backend.html',locals())

def add_article(request):
    if request.method == "POST":

        title=request.POST.get("title")
        content=request.POST.get("content")
        user = request.user
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")

        # 防止用户在页面写script标签
        soup = BeautifulSoup(content,"html.parser")
        #文章过滤
        for tag in soup.find_all():
            if tag.name in ["script",]:
                # 删除
                tag.decompose()

#         切片文章文本
        desc = soup.text[0:150]

        article_obj = Article.objects.create(title=title,content=str(soup),user=user,category_id=cate_pk,desc=desc)

        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)
        return redirect("/backend/")

    else:

        blog=request.user.blog
        cate_list = Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        return render(request,"backend/add_article.html",locals())

def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")
    name = obj.name

    path = os.path.join(settings.BASE_DIR,"static","upload",name)
    with open(path,'wb') as f:
        for line in obj:
            f.write(line)


    res = {
        "error":0,
        "url":"/static/upload/"+name
    }

    return HttpResponse(json.dumps(res))



def edit_article(request,edit_id):
    article_obj = Article.objects.get(nid=edit_id)
    print(article_obj)

    if request.method == "POST":
        title=request.POST.get("title")
        content = request.POST.get("content")
        cate = request.POST.get("cate")
        tags = request.POST.getlist("tags")


        article_obj.title=title
        article_obj.content=content
        article_obj.cate=cate
        article_obj.save()

        article_obj.tags.set("tags")

        return redirect('/index/')

    cate_list = Category.objects.all()
    tags = Tag.objects.all()
    return render(request,"backend/edit_article.html",{"article_obj":article_obj,"cate_list":cate_list,"tags":tags})


def delete_article(request):
    print(request.POST)

    del_id = request.POST.get("del_id")
    print(del_id)

    ret = {"status":True}

    try:
        Article.objects.filter(id=del_id).delete()

    except Exception as e:

        ret['status']=False

    return HttpResponse(json.dumps(ret))














