from django.shortcuts import render
from .models import Post, Category

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories})

def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})