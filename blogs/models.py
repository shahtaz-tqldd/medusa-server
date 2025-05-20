import uuid
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from user.models import CustomUser

class Category(models.Model):
    """Categories for organizing blogs"""
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

class Tag(models.Model):
    """Tags for blogs"""
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    name = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]

class Blog(models.Model):
    """Main blog model"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
    )
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blogs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs', blank=True)
    tags = models.ManyToManyField(Tag, related_name='blogs', blank=True)
    
    # Meta
    excerpt = models.TextField(blank=True, null=True, help_text=_("Short description for SEO and previews"))
    featured_image = models.ImageField(upload_to='blog/featured_images/', blank=True, null=True)
    reading_time = models.PositiveIntegerField(default=0, help_text=_("Estimated reading time in minutes"))
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ["-created_at"]

class ContentBlock(models.Model):
    """Base model for all content blocks"""
    BLOCK_TYPES = (
        ('text', _('Text')),
        ('heading', _('Heading')),
        ('code', _('Code')),
        ('image', _('Image/Diagram')),
        ('quote', _('Quote')),
        ('list', _('List')),
    )
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='content_blocks')
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    order = models.PositiveIntegerField(default=0, help_text=_("Order of the content block within the blog"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Content Block")
        verbose_name_plural = _("Content Blocks")
        ordering = ["blog", "order"]

class TextBlock(models.Model):
    """Model for text content"""
    block = models.OneToOneField(ContentBlock, on_delete=models.CASCADE, related_name='text_content')
    content = models.TextField()
    
    def __str__(self):
        return f"Text Block: {self.content[:50]}..."

class HeadingBlock(models.Model):
    """Model for heading content"""
    HEADING_LEVELS = (
        (1, _('H1')),
        (2, _('H2')),
        (3, _('H3')),
    )
    
    block = models.OneToOneField(ContentBlock, on_delete=models.CASCADE, related_name='heading_content')
    content = models.CharField(max_length=300)
    level = models.PositiveSmallIntegerField(choices=HEADING_LEVELS, default=2)
    
    def __str__(self):
        return f"H{self.level}: {self.content}"

class CodeBlock(models.Model):
    """Model for code snippets"""
    block = models.OneToOneField(ContentBlock, on_delete=models.CASCADE, related_name='code_content')
    code = models.TextField()
    language = models.CharField(max_length=50, default='python', help_text=_("Programming language of the code"))
    caption = models.CharField(max_length=255, blank=True, null=True)
    line_numbers = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Code Block: {self.language}"

class ImageBlock(models.Model):
    """Model for images and diagrams"""
    block = models.OneToOneField(ContentBlock, on_delete=models.CASCADE, related_name='image_content')
    image = models.ImageField(upload_to='blog/content_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alternative text for accessibility"))
    
    def __str__(self):
        return f"Image: {self.caption or 'Untitled'}"

class QuoteBlock(models.Model):
    """Model for quote content"""
    block = models.OneToOneField(ContentBlock, on_delete=models.CASCADE, related_name='quote_content')
    content = models.TextField()
    source = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Quote: {self.content[:50]}..."

class ListBlock(models.Model):
    """Model for list content"""
    LIST_TYPES = (
        ('ordered', _('Ordered List')),
        ('unordered', _('Unordered List')),
    )
    
    block = models.OneToOneField(ContentBlock, on_delete=models.CASCADE, related_name='list_content')
    list_type = models.CharField(max_length=20, choices=LIST_TYPES, default='unordered')
    
    def __str__(self):
        return f"{self.get_list_type_display()}"

class ListItem(models.Model):
    """Individual list items"""
    list_block = models.ForeignKey(ListBlock, on_delete=models.CASCADE, related_name='items')
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ["order"]
    
    def __str__(self):
        return f"List Item: {self.content[:50]}..."

class Comment(models.Model):
    """User comments on blogs"""
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog.title}"
    
    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-created_at"]
