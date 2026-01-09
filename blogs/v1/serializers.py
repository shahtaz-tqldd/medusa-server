import json
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from blogs.models import (
    Blog, Category, Tag, ContentBlock, TextBlock, HeadingBlock, 
    CodeBlock, ImageBlock, QuoteBlock, ListBlock, ListItem
)
from base.managers.cloudinary import CloudinaryImageManager


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
    image = serializers.ImageField(required=True, write_only=True)
    image_url = serializers.URLField(source='image', read_only=True)
    
    class Meta:
        model = ImageBlock
        fields = ['image', 'image_url', 'caption', 'alt_text', 'cloudinary_public_id']
        read_only_fields = ['cloudinary_public_id', 'image_url']
    
    def create(self, validated_data):
        image_file = validated_data.pop('image')
        block = validated_data.pop('block', None)
        
        # Upload to Cloudinary
        cloudinary_manager = CloudinaryImageManager()
        try:
            upload_result = cloudinary_manager.upload(
                image_file, 
                folder="tourtoise/blog/content"
            )
            
            # Create ImageBlock with Cloudinary data
            image_block = ImageBlock.objects.create(
                block=block,
                image=upload_result['url'],
                cloudinary_public_id=upload_result['public_id'],
                **validated_data
            )
            
            return image_block
            
        except Exception as e:
            raise serializers.ValidationError({
                'image': f'Failed to upload image: {str(e)}'
            })

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
            # Use the ImageBlockSerializer to handle Cloudinary upload
            image_serializer = ImageBlockSerializer()
            image_data['block'] = content_block
            image_serializer.create(image_data)
        elif block_type == 'quote' and quote_data:
            QuoteBlock.objects.create(block=content_block, **quote_data)
        elif block_type == 'list' and list_data:
            items_data = list_data.pop('items', [])
            list_block = ListBlock.objects.create(block=content_block, **list_data)
            for item_data in items_data:
                ListItem.objects.create(list_block=list_block, **item_data)
                
        return content_block


class BlogCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        required=True,
        allow_null=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    content_blocks = serializers.JSONField(required=False)
    featured_image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    featured_image_url = serializers.URLField(source='featured_image', read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'subtitle', 'excerpt', 
            'featured_image', 'featured_image_url', 'status', 'category',
            'tags', 'content_blocks'
        ]
        read_only_fields = ['id', 'slug', 'featured_image_url']

    def validate_content_blocks(self, value):
        """Parse content_blocks if it comes as string"""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for content_blocks")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Extract nested data
        tags_data = validated_data.pop('tags', [])
        content_blocks_data = validated_data.pop('content_blocks', [])
        featured_image_file = validated_data.pop('featured_image', None)
        
        # Handle featured image upload to Cloudinary
        if featured_image_file:
            cloudinary_manager = CloudinaryImageManager()
            try:
                upload_result = cloudinary_manager.upload(
                    featured_image_file,
                    folder="tourtoise/blog/featured"
                )
                validated_data['featured_image'] = upload_result['url']
                validated_data['featured_image_public_id'] = upload_result['public_id']
            except Exception as e:
                raise serializers.ValidationError({
                    'featured_image': f'Failed to upload featured image: {str(e)}'
                })
        
        # Create the blog
        blog = Blog.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        # Create or get tags and add them
        if tags_data:
            tag_objects = []
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag_objects.append(tag)
            blog.tags.set(tag_objects)

        # Create content blocks from parsed data
        for idx, block_data in enumerate(content_blocks_data):
            self._create_content_block(blog, block_data, idx)

        return blog
    
    def _create_content_block(self, blog, block_data, order):
        """Helper method to create content blocks"""
        block_type = block_data.get('block_type')
        
        # Create ContentBlock
        content_block = ContentBlock.objects.create(
            blog=blog,
            block_type=block_type,
            order=block_data.get('order', order)
        )
        
        # Create specific content based on type
        if block_type == 'text':
            text_content = block_data.get('text_content', {})
            TextBlock.objects.create(
                block=content_block,
                content=text_content.get('content', '')
            )
            
        elif block_type == 'heading':
            heading_content = block_data.get('heading_content', {})
            HeadingBlock.objects.create(
                block=content_block,
                content=heading_content.get('content', ''),
                level=heading_content.get('level', 2)
            )
            
        elif block_type == 'code':
            code_content = block_data.get('code_content', {})
            CodeBlock.objects.create(
                block=content_block,
                code=code_content.get('code', ''),
                language=code_content.get('language', 'python'),
                caption=code_content.get('caption', ''),
                line_numbers=code_content.get('line_numbers', True)
            )
            
        elif block_type == 'image':
            # Get image file from request.FILES
            image_key = f'content_blocks[{order}]image_content.image'
            image_file = self.context['request'].FILES.get(image_key)
            
            if image_file:
                cloudinary_manager = CloudinaryImageManager()
                try:
                    upload_result = cloudinary_manager.upload(
                        image_file,
                        folder="tourtoise/blog/content"
                    )
                    
                    image_content = block_data.get('image_content', {})
                    ImageBlock.objects.create(
                        block=content_block,
                        image=upload_result['url'],
                        cloudinary_public_id=upload_result['public_id'],
                        caption=image_content.get('caption', ''),
                        alt_text=image_content.get('alt_text', '')
                    )
                except Exception as e:
                    # Log error but don't fail the entire blog creation
                    print(f"Failed to upload image for block {order}: {str(e)}")
                    
        elif block_type == 'quote':
            quote_content = block_data.get('quote_content', {})
            QuoteBlock.objects.create(
                block=content_block,
                content=quote_content.get('content', ''),
                source=quote_content.get('source', '')
            )
            
        elif block_type == 'list':
            list_content = block_data.get('list_content', {})
            list_block = ListBlock.objects.create(
                block=content_block,
                list_type=list_content.get('list_type', 'unordered')
            )
            items = list_content.get('items', [])
            for item_idx, item in enumerate(items):
                ListItem.objects.create(
                    list_block=list_block,
                    content=item.get('content', ''),
                    order=item.get('order', item_idx)
                )


# Blog detail serializers remain the same...
class ContentBlockDetailSerializer(serializers.ModelSerializer):
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