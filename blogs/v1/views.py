from django.utils import timezone
from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend

# restframework utils
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import (
    CreateAPIView, 
    ListAPIView, 
    RetrieveAPIView, 
    UpdateAPIView, 
    DestroyAPIView
)
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
    HTTP_204_NO_CONTENT,
)

# models
from blogs.models import Blog, ContentBlock

# serializers
from blogs.v1.serializers import (
    BlogCreateSerializer, 
    BlogDetailSerializer, 
    BlogListSerializer,
    BlogUpdateSerializer,
)

# helpers
from base.helpers.pagination import CustomPagination
from base.helpers.response import APIResponse
from blogs.helpers.blog_filter import BlogFilter
from blogs.v1.res_msg import (
    BLOG_CREATED,
    BLOG_LIST,
    BLOG_DETAILS,
    BLOG_UPDATED,
    BLOG_DELETED,
    BLOG_NOT_FOUND,
)


class CreateNewBlog(CreateAPIView):
    """
    API View to create new blog
    """
    serializer_class = BlogCreateSerializer
    permission_classes = [IsAuthenticated]
    RESPONSE_LANGUAGE = "en"
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # If status is published, add published_at date
        if request.data.get('status') == 'published':
            serializer.validated_data['published_at'] = timezone.now()
        
        blog = serializer.save()
        response_data = BlogDetailSerializer(blog, context={'request': request}).data 
        
        # Return serialized data for the created blog
        return APIResponse.success(
            data= response_data,
            message=BLOG_CREATED[self.RESPONSE_LANGUAGE],
            status=HTTP_201_CREATED
        )



class BlogList(ListAPIView):
    """
    API View to get blog list with pagination, filtering and search
    """
    serializer_class = BlogListSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlogFilter
    search_fields = ['title', 'subtitle', 'excerpt', 'author__username']
    ordering_fields = ['published_at', 'view_count', 'title']
    ordering = ['-published_at']
    RESPONSE_LANGUAGE = "en"
    
    def get_queryset(self):
        # By default, only show published blogs
        queryset = Blog.objects.filter(status='published')
        
        # If user is authenticated and has requested their drafts
        if self.request.user.is_authenticated and self.request.query_params.get('include_drafts') == 'true':
            queryset = Blog.objects.filter(
                Q(status='published') | Q(author=self.request.user, status='draft')
            )
            
        # Add prefetch related to optimize queries
        queryset = queryset.select_related('author').prefetch_related('category', 'tags')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        
        return APIResponse.success(
            data=data, 
            message=BLOG_LIST[self.RESPONSE_LANGUAGE]
        )


class BlogDetails(RetrieveAPIView):
    """
    API View to get blog details with id
    """
    serializer_class = BlogDetailSerializer
    RESPONSE_LANGUAGE = "en"
    
    def get_queryset(self):
        return Blog.objects.all()
    
    def get_object(self):
        lookup_value = self.kwargs.get('id')
        try:
            blog = Blog.objects.get(id=lookup_value)
            # Increment view count
            Blog.objects.filter(id=lookup_value).update(view_count=F('view_count') + 1)
            return blog
        except Blog.DoesNotExist:
            raise NotFound(BLOG_NOT_FOUND[self.RESPONSE_LANGUAGE])
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message=BLOG_DETAILS[self.RESPONSE_LANGUAGE]
        )


class UpdateBlogDetails(UpdateAPIView):
    """
    API View to update blog with id
    """
    serializer_class = BlogUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    RESPONSE_LANGUAGE = "en"
    
    def get_queryset(self):
        return Blog.objects.all()
    
    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        try:
            blog = Blog.objects.get(id=lookup_value)
            # Check permissions
            self.check_object_permissions(self.request, blog)
            return blog
        except Blog.DoesNotExist:
            raise NotFound(BLOG_NOT_FOUND[self.RESPONSE_LANGUAGE])
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_blog = serializer.save()
        
        # Return the updated blog with all details
        return APIResponse.success(
            data=BlogDetailSerializer(updated_blog, context={'request': request}).data, 
            message=BLOG_UPDATED[self.RESPONSE_LANGUAGE],
            status=HTTP_205_RESET_CONTENT
        )
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)



class DeleteBlog(DestroyAPIView):
    """
    API View to delete blog with id
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    RESPONSE_LANGUAGE = "en"
    
    def get_queryset(self):
        return Blog.objects.all()
    
    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        try:
            blog = Blog.objects.get(id=lookup_value)
            # Check permissions
            self.check_object_permissions(self.request, blog)
            return blog
        except Blog.DoesNotExist:
            raise NotFound(BLOG_NOT_FOUND[self.RESPONSE_LANGUAGE])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete content blocks first (to handle cascade properly)
        ContentBlock.objects.filter(blog=instance).delete()
        
        # Delete the blog
        instance.delete()
        
        return APIResponse.success(
            message=BLOG_DELETED[self.RESPONSE_LANGUAGE], 
            status=HTTP_204_NO_CONTENT
        )