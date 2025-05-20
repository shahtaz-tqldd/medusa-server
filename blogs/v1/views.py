from django.utils import timezone
from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend

# restframework utils
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny

# models
from blogs.models import Blog, ContentBlock, Category

# serializers
from blogs.v1.serializers import (
    BlogCreateSerializer, 
    BlogDetailSerializer, 
    BlogListSerializer,
    BlogUpdateSerializer,
    CategorySerializer,
    TagSerializer

)

# helpers
from blogs.v1 import res_msg
from blogs.helpers.blog_filter import BlogFilter
from base.helpers.pagination import CustomPagination
from base.helpers.response import APIResponse


class CreateNewBlog(generics.CreateAPIView):
    """
    API View to create new blog
    """
    serializer_class = BlogCreateSerializer
    permission_classes = [IsAuthenticated]
    RES_LANG = "en"
    
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
            message=res_msg.BLOG_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )



class BlogList(generics.ListAPIView):
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
    RES_LANG = "en"
    
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
            message=res_msg.BLOG_LIST[self.RES_LANG]
        )


class BlogDetails(generics.RetrieveAPIView):
    """
    API View to get blog details with id
    """
    serializer_class = BlogDetailSerializer
    RES_LANG = "en"
    
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
            return APIResponse.error(message=res_msg.BLOG_NOT_FOUND[self.RES_LANG])
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message=res_msg.BLOG_DETAILS[self.RES_LANG]
        )


class UpdateBlogDetails(generics.UpdateAPIView):
    """
    API View to update blog with id
    """
    serializer_class = BlogUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    RES_LANG = "en"
    
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
            return APIResponse.error(message=res_msg.BLOG_NOT_FOUND[self.RES_LANG])
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_blog = serializer.save()
        
        # Return the updated blog with all details
        return APIResponse.success(
            data=BlogDetailSerializer(updated_blog, context={'request': request}).data, 
            message=res_msg.BLOG_UPDATED[self.RES_LANG],
            status=status.HTTP_205_RESET_CONTENT
        )
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)



class DeleteBlog(generics.DestroyAPIView):
    """
    API View to delete blog with id
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    RES_LANG = "en"
    
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
            return APIResponse.error(message=res_msg.BLOG_NOT_FOUND[self.RES_LANG])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete content blocks first (to handle cascade properly)
        ContentBlock.objects.filter(blog=instance).delete()
        
        # Delete the blog
        instance.delete()
        
        return APIResponse.success(
            message=res_msg.BLOG_DELETED[self.RES_LANG], 
            status=status.HTTP_204_NO_CONTENT
        )
    

# -------------
# Category
# -------------
class CreateNewCategory(generics.CreateAPIView):
    """
    API View to create new category
    """
    RES_LANG = 'en'
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success(
            data=serializer.data, 
            message=res_msg.CATEGORY_CREATED[self.RES_LANG],
            status=status.HTTP_201_CREATED
        )
    

class CategoryList(generics.ListAPIView):
    """
    API View to get category list
    """
    RES_LANG = 'en'
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return APIResponse.success(
            data=serializer.data, 
            message=res_msg.CATEGORY_LIST[self.RES_LANG]
        )
    
    
class UpdateCategory(generics.UpdateAPIView):
    """
    API View to update category with id
    """
    RES_LANG = 'en'
    ermission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'id'
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return APIResponse.success(
            data=serializer.data, 
            message=res_msg.CATEGORY_UPDATED[self.RES_LANG],
            status=status.HTTP_205_RESET_CONTENT
        )
    
    
class DeleteCategory(generics.DestroyAPIView):
    """
    API View to delete category with id
    """
    RES_LANG = 'en'
    ermission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return APIResponse.success(
            message=res_msg.CATEGORY_DELETED[self.RES_LANG],
            status=status.HTTP_204_NO_CONTENT
        )
    