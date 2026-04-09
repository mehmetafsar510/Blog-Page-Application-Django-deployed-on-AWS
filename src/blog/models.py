from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def user_directory_path(instance, filename):
    return 'blog/{0}/{1}'.format(instance.author.id, filename)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-created_at']


# class Category(models.Model):
#     name = models.CharField(max_length=100)

    # class Meta:
    #     verbose_name_plural = "Categories"

    # def __str__(self):
    #     return self.name


class Post(models.Model):
    OPTIONS = (
        ('d', 'Draft'),
        ('p', 'Published')
    )
    CATEGORY_OPT = (
        ('e', 'Entertainment'),
        ('m', 'Music'),
        ('i', 'IT')
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(
        upload_to=user_directory_path, default='django.jpg')
    category = models.CharField(max_length=15, choices=CATEGORY_OPT, default='e')
    publish_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(blank=True, null=True, help_text="Set a publish date for scheduled posts")
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=OPTIONS, default='d')
    slug = models.SlugField(blank=True, unique=True)  # how-to-learn-django
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO title (if different from post title)")
    meta_description = models.TextField(blank=True, help_text="SEO description (150-160 characters)")
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def is_published(self):
        return self.status == 'p' and (self.published_date is None or self.published_date <= timezone.now())

    def get_published_date(self):
        return self.published_date if self.published_date else self.publish_date

    def get_meta_title(self):
        return self.meta_title if self.meta_title else self.title
    
    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description
        return self.content[:160] + "..." if len(self.content) > 160 else self.content
    
    def get_reading_time(self):
        word_count = len(self.content.split())
        # Average reading speed: 200 words per minute
        minutes = word_count // 200
        return max(1, minutes)  # At least 1 minute
    
    def get_related_posts(self):
        # Get posts with same tags or category
        related = Post.objects.filter(
            models.Q(tags__in=self.tags.all()) | models.Q(category=self.category)
        ).exclude(id=self.id).distinct()[:3]
        return related
    
    def comment_count(self):
        return self.comment_set.all().count()

    def view_count(self):
        return self.postview_set.all().count()

    def like_count(self):
        return self.like_set.all().count()

    def comments(self):
        return self.comment_set.all()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return self.user.username


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
