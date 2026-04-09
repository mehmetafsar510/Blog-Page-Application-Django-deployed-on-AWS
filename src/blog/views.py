from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from .models import Post, Like, PostView, Tag, NewsletterSubscriber
from .forms import CommentForm, PostForm, SearchForm, NewsletterSubscriptionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db.models.functions import Coalesce
from django.db.models import F
from django.utils import timezone
from django.utils.text import slugify


def post_list(request):
    newsletter_form = NewsletterSubscriptionForm()
    if request.method == "POST" and 'email' in request.POST:
        newsletter_form = NewsletterSubscriptionForm(request.POST)
        if newsletter_form.is_valid():
            email = newsletter_form.cleaned_data['email'].strip().lower()
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                try:
                    send_mail(
                        subject="Welcome to the Clarusway Blog Newsletter",
                        message="Thank you for subscribing to our newsletter. You'll receive the latest blog updates, author features, and publishing insights.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        fail_silently=False,
                    )
                    messages.success(request, "Subscribed successfully! A welcome email is on its way.")
                except Exception as e:
                    messages.success(request, "Subscribed successfully!")
            else:
                messages.info(request, "You are already subscribed to the newsletter.")
            return redirect('blog:list')
        else:
            for field, errors in newsletter_form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    
    published_filter = Q(status='p') & (
        Q(published_date__lte=timezone.now()) | Q(published_date__isnull=True)
    )
    order_by_field = Coalesce('published_date', 'publish_date').desc()
    if request.user.is_authenticated:
        qs = Post.objects.filter(
            published_filter | Q(author=request.user)
        ).distinct().order_by(order_by_field)
    else:
        qs = Post.objects.filter(published_filter).order_by(order_by_field)
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
    
    # Top authors spotlight
    top_authors = User.objects.annotate(
        post_count=Count('post', filter=Q(post__status='p')),
        follower_count=Count('profile__followers', distinct=True)
    ).filter(post_count__gt=0).order_by('-follower_count', '-post_count')[:3]
    
    subscriber_count = NewsletterSubscriber.objects.count()
    
    context = {
        "object_list": page_obj,
        "search_form": search_form,
        "selected_category": category,
        "selected_tag": tag,
        "recent_posts": recent_posts,
        "popular_posts": popular_posts,
        "top_authors": top_authors,
        "newsletter_form": newsletter_form,
        "subscriber_count": subscriber_count,
    }
    return render(request, "blog/post_list.html", context)


def about(request):
    return render(request, "about.html")


def robots(request):
    content = "User-agent: *\nDisallow:\nSitemap: {}/sitemap.xml\n".format(request.scheme + "://" + request.get_host())
    return HttpResponse(content, content_type="text/plain")


@login_required()
def post_create(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # Generate slug from title with uniqueness check
            base_slug = slugify(post.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = slug
            # Set published_date if status is published
            if post.status == 'p' and not post.published_date:
                post.published_date = timezone.now()
            try:
                post.save()
                form.save_m2m()  # Save tags
                messages.success(request, "Post created successfully!")
                return redirect("blog:list")
            except Exception as e:
                messages.error(request, f"Error creating post: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    context = {
        'form': form
    }
    return render(request, "blog/post_create.html", context)


def post_detail(request, slug):
    form = CommentForm()
    obj = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated:
        PostView.objects.create(user=request.user, post=obj)
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.post = obj
                comment.save()
                return redirect("blog:detail", slug=slug)
        else:
            messages.warning(request, "Please login to leave a comment.")
            return redirect('login')
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
