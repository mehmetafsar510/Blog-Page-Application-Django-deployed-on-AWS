from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Like, PostView, Tag
from .forms import CommentForm, PostForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.text import slugify


def post_list(request):
    qs = Post.objects.filter(status='p').filter(
        Q(published_date__lte=timezone.now()) | Q(published_date__isnull=True)
    ).order_by('-published_date')
    search_form = SearchForm(request.GET or None)
    category = request.GET.get('category')
    tag = request.GET.get('tag')
    
    # Category filter
    if category:
        qs = qs.filter(category=category)
    
    # Tag filter
    if tag:
        qs = qs.filter(tags__name=tag)
    
    # Search query
    if search_form.is_valid() and search_form.cleaned_data.get('query'):
        query = search_form.cleaned_data['query']
        qs = qs.filter(Q(title__icontains=query) | Q(content__icontains=query))
    
    # Pagination
    paginator = Paginator(qs, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Recent posts (sidebar widget)
    recent_posts = Post.objects.filter(status='p').filter(
        Q(published_date__lte=timezone.now()) | Q(published_date__isnull=True)
    ).order_by('-published_date')[:5]
    
    # Popular posts (sidebar widget) - annotate view count
    popular_posts = Post.objects.filter(status='p').filter(
        Q(published_date__lte=timezone.now()) | Q(published_date__isnull=True)
    ).annotate(
        view_count=Count('postview')
    ).order_by('-view_count')[:5]
    
    context = {
        "object_list": page_obj,
        "search_form": search_form,
        "selected_category": category,
        "selected_tag": tag,
        "recent_posts": recent_posts,
        "popular_posts": popular_posts,
    }
    return render(request, "blog/post_list.html", context)


def about(request):
    return render(request, "about.html")


def robots(request):
    content = "User-agent: *\nDisallow:\nSitemap: {}/sitemap.xml\n".format(request.scheme + "://" + request.get_host())
    return HttpResponse(content, content_type="text/plain")


@login_required()
def post_create(request):
    # form = PostForm(request.POST or None, request.FILES or None)

    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # Generate slug from title
            post.slug = slugify(post.title)
            if post.status == 'p' and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            form.save_m2m()  # Save tags
            messages.success(request, "Post created succesfully!")
            return redirect("blog:list")
    context = {
        'form': form
    }
    return render(request, "blog/post_create.html", context)


def post_detail(request, slug):
    # print(request.get_host())
    # print(slug)
    # Post.objects.get(slug=learn-drf-3c78be2186)
    # slug = learn-drf-3c78be2186
    form = CommentForm()
    obj = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated:
        PostView.objects.create(user=request.user, post=obj)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = obj
            comment.save()
            return redirect("blog:detail", slug=slug)
            # return redirect(request.path)
    context = {
        "object": obj,
        "form": form
    }
    return render(request, "blog/post_detail.html", context)


@login_required()
def post_update(request, slug):
    obj = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=obj)
    if request.user != obj.author:
        messages.warning(request, "You're not a writer of this post")
        return redirect('blog:list')
    if form.is_valid():
        post = form.save(commit=False)
        if post.status == 'p' and not post.published_date:
            post.published_date = timezone.now()
        post.save()
        form.save_m2m()
        messages.success(request, "Post updated!!")
        return redirect("blog:list")

    context = {
        "object": obj,
        "form": form
    }
    return render(request, "blog/post_update.html", context)


@login_required()
def post_delete(request, slug):
    obj = get_object_or_404(Post, slug=slug)

    if request.user.id != obj.author.id:
        messages.warning(request, "You're not a writer of this post")
        return redirect('blog:list')
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Post deleted!!")
        return redirect("blog:list")
    context = {
        "object": obj
    }
    return render(request, "blog/post_delete.html", context)


@login_required()
def like(request, slug):
    if request.method == "POST":
        obj = get_object_or_404(Post, slug=slug)
        like_qs = Like.objects.filter(user=request.user, post=obj)
        if like_qs:
            like_qs.delete()
        else:
            Like.objects.create(user=request.user, post=obj)
        return redirect('blog:detail', slug=slug)
    return redirect('blog:detail', slug=slug)
