from rest_framework import serializers
from base.models import Visitor


class CreateVisitorSerializer(serializers.ModelSerializer):
    """Serializer for creating new visitor records"""
    class Meta:
        model = Visitor
        fields = [
            'id', 'ip_address', 'device_name', 'device_type',
            'longitude', 'latitude', 'country', 'city',
            'cookie_id'
        ]
        read_only_fields = ['first_visit', 'last_visit', 'visit_count', 'total_time_spent']
    
    def create(self, validated_data):
        """Override create to handle existing visitors based on IP or cookie"""
        ip_address = validated_data.get('ip_address')
        cookie_id = validated_data.get('cookie_id')
        
        # Try to find existing visitor by IP or cookie_id
        existing_visitor = None
        if ip_address:
            existing_visitor = Visitor.objects.filter(ip_address=ip_address).first()
        
        if not existing_visitor and cookie_id:
            existing_visitor = Visitor.objects.filter(cookie_id=cookie_id).first()
            
        if existing_visitor:
            # Update existing visitor with any new information
            for key, value in validated_data.items():
                setattr(existing_visitor, key, value)
            
            # Update visit stats
            existing_visitor.update_visit()
            return existing_visitor
        
        # Create new visitor if none exists
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