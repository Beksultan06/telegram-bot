from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'year', 'shop', 'shop_price',
            'car_model', 'car_brand', 'car_category',
            'part', 'manufacturer_country', 'created_at', 'updated_at'
        ]