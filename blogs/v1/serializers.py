from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from blogs.models import (
    Blog, Category, Tag, ContentBlock, TextBlock, HeadingBlock, 
    CodeBlock, ImageBlock, QuoteBlock, ListBlock, ListItem
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


# Serializers for content blocks
class TextBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBlock
        fields = ['content']

class HeadingBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeadingBlock
        fields = ['content', 'level']

class CodeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeBlock
        fields = ['code', 'language', 'caption', 'line_numbers']

class ImageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageBlock
        fields = ['image', 'caption', 'alt_text']

class QuoteBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteBlock
        fields = ['content', 'source']

class ListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListItem
        fields = ['content', 'order']

class ListBlockSerializer(serializers.ModelSerializer):
    items = ListItemSerializer(many=True)
    
    class Meta:
        model = ListBlock
        fields = ['list_type', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        list_block = ListBlock.objects.create(**validated_data)
        for item_data in items_data:
            ListItem.objects.create(list_block=list_block, **item_data)
        return list_block

# Serializer for content blocks with content type discrimination
class ContentBlockSerializer(serializers.ModelSerializer):
    text_content = TextBlockSerializer(required=False)
    heading_content = HeadingBlockSerializer(required=False)
    code_content = CodeBlockSerializer(required=False)
    image_content = ImageBlockSerializer(required=False)
    quote_content = QuoteBlockSerializer(required=False)
    list_content = ListBlockSerializer(required=False)
    
    class Meta:
        model = ContentBlock
        fields = [
            'id', 'block_type', 'order', 
            'text_content', 'heading_content', 'code_content', 
            'image_content', 'quote_content', 'list_content'
        ]
    
    def create(self, validated_data):
        # Extract nested content data based on block type
        block_type = validated_data.get('block_type')
        text_data = validated_data.pop('text_content', None)
        heading_data = validated_data.pop('heading_content', None)
        code_data = validated_data.pop('code_content', None)
        image_data = validated_data.pop('image_content', None)
        quote_data = validated_data.pop('quote_content', None)
        list_data = validated_data.pop('list_content', None)
        
        # Create the content block
        content_block = ContentBlock.objects.create(**validated_data)
        
        # Create the specific content based on block type
        if block_type == 'text' and text_data:
            TextBlock.objects.create(block=content_block, **text_data)
        elif block_type == 'heading' and heading_data:
            HeadingBlock.objects.create(block=content_block, **heading_data)
        elif block_type == 'code' and code_data:
            CodeBlock.objects.create(block=content_block, **code_data)
        elif block_type == 'image' and image_data:
            ImageBlock.objects.create(block=content_block, **image_data)
        elif block_type == 'quote' and quote_data:
            QuoteBlock.objects.create(block=content_block, **quote_data)
        elif block_type == 'list' and list_data:
            items_data = list_data.pop('items', [])
            list_block = ListBlock.objects.create(block=content_block, **list_data)
            for item_data in items_data:
                ListItem.objects.create(list_block=list_block, **item_data)
                
        return content_block

# Blog create serializer
class BlogCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        required=True,
        allow_null=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), 
        many=True, 
        required=False
    )
    content_blocks = ContentBlockSerializer(many=True, required=False)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'subtitle', 'excerpt', 
            'featured_image', 'status', 'category',
            'tags', 'content_blocks'
        ]
        read_only_fields = ['id', 'slug']

    @transaction.atomic
    def create(self, validated_data):
        # Extract nested data
        tags_data = validated_data.pop('tags', [])
        content_blocks_data = validated_data.pop('content_blocks', [])
        
        # Create the blog
        blog = Blog.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        # Add tags
        if tags_data:
            blog.tags.set(tags_data)

        # Create content blocks
        for block_data in content_blocks_data:
            block_data['blog'] = blog
            self.fields['content_blocks'].child.create(block_data)

        return blog


# Serializers for blog details view
class ContentBlockDetailSerializer(ContentBlockSerializer):
    class Meta(ContentBlockSerializer.Meta):
        fields = ContentBlockSerializer.Meta.fields
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Only include the content for the specific block type
        content_types = ['text_content', 'heading_content', 'code_content', 
                         'image_content', 'quote_content', 'list_content']
        
        for content_type in content_types:
            if content_type != f"{instance.block_type}_content" and content_type in data:
                data.pop(content_type)
        
        return data

class BlogDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    content_blocks = ContentBlockDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'subtitle', 'author',
            'status', 'excerpt', 'featured_image', 
            'category', 'tags', 'reading_time', 'view_count',
            'content_blocks', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'name': f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username
        }
    

class BlogListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'subtitle', 'slug', 'featured_image',
            'author', 'category', 'tags', 'reading_time',
            'view_count', 'published_at'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'name': f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username
        }
    

class BlogUpdateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        required=True,
        allow_null=False
    )

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), 
        many=True, 
        required=False
    )
    
    class Meta:
        model = Blog
        fields = [
            'title', 'subtitle', 'excerpt', 
            'featured_image', 'status', 'category', 
            'tags'
        ]
    
    @transaction.atomic
    def update(self, instance, validated_data):
        # Handle categories and tags
        tags_data = validated_data.pop('tags', None)
        
        # Update status and published_at
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # If changing from draft to published, set published_at
        if old_status == 'draft' and new_status == 'published':
            validated_data['published_at'] = timezone.now()
        
        # Update the blog instance
        instance = super().update(instance, validated_data)
            
        # Update tags if provided
        if tags_data is not None:
            instance.tags.set(tags_data)
            
        return instance