from rest_framework import serializers
from base.models import Visitor, Client


class CreateVisitorSerializer(serializers.ModelSerializer):
    """Serializer for creating new visitor records"""
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'ip_address', 'device_name', 'device_type',
            'longitude', 'latitude', 'country', 'city'
        ]
        read_only_fields = ['first_visit', 'last_visit', 'visit_count', 'total_time_spent']

    def create(self, validated_data):
        """Create a new visitor record"""
        return super().create(validated_data)


class VisitorSerializer(serializers.ModelSerializer):
    """Serializer for retrieving visitor details"""
    class Meta:
        model = Visitor
        fields = [
            'id', 'ip_address', 'first_visit', 'last_visit', 
            'device_name', 'device_type',
            'longitude', 'latitude', 'country', 'city',
            'visit_count', 'total_time_spent'
        ]


class CreateClientSerializer(serializers.ModelSerializer):
    """Serializers to create new clients"""

    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'whatsapp',
            'project_description', 'budget', 'project_type', 'timeline', 'design_required'      
        ]
        extra_kwargs = {
            'phone' : {'required': False},
            'whatsapp' : {'required': False},
            'budget' : {'required': False},
            'timeline' : {'required': False},
        }

    def create(self, validated_data):
        visitor_id = self.context.get('visitor_id')
        if visitor_id:
            try:
                visitor = Visitor.objects.get(id=visitor_id)
                validated_data['visitor'] = visitor

            except Visitor.DoesNotExist:
                raise serializers.ValidationError("Visitor doesnot exist!")
        
        else:
            raise serializers.ValidationError("Visitor id required!")
        
        return super().create(validated_data)


class ClientSerializer(serializers.ModelSerializer):
    """Serializers to client list"""
    visitor_id = serializers.SerializerMethodField()
    visitor_country = serializers.SerializerMethodField()
    visitor_city = serializers.SerializerMethodField()
    visitor_longitude = serializers.SerializerMethodField()
    visitor_latitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone", "whatsapp", "created_at", 
                  "project_description", "project_type", "budget", "timeline",
                  "visitor_id", "visitor_country", "visitor_city", 
                  "visitor_longitude", "visitor_latitude"]
        
    def get_visitor_id(self, obj):
        return obj.visitor.id if obj.visitor else None
    
    def get_visitor_country(self, obj):
        return obj.visitor.country if obj.visitor else None
    
    def get_visitor_city(self, obj):
        return obj.visitor.city if obj.visitor else None
    
    def get_visitor_longitude(self, obj):
        return obj.visitor.longitude if obj.visitor else None
    
    def get_visitor_latitude(self, obj):
        return obj.visitor.latitude if obj.visitor else None