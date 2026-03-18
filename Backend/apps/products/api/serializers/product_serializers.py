# apps/products/api/serializers/product_serializers.py
from rest_framework import serializers
from apps.products.models import Category, Product, CutType


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ["id", "name", "slug"]


class CutTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CutType
        fields = ["id", "name", "extra_price", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
    cut_types       = CutTypeSerializer(many=True, read_only=True)
    category_name   = serializers.CharField(source="category.name", read_only=True)
    shop_name       = serializers.CharField(source="shop.name", read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model  = Product
        fields = [
            "id", "name", "slug", "description",
            "price", "discount_price", "effective_price",
            "stock_quantity", "unit", "image", "is_available",
            "category", "category_name", "shop", "shop_name",
            "cut_types", "created_at",
        ]
        read_only_fields = ["slug", "created_at"]


class ProductCreateSerializer(serializers.ModelSerializer):
    cut_types = CutTypeSerializer(many=True, required=False)

    class Meta:
        model  = Product
        fields = [
            "name", "description", "category",
            "price", "discount_price", "stock_quantity",
            "unit", "image", "cut_types",
        ]

    def create(self, validated_data):
        cut_types_data = validated_data.pop("cut_types", [])
        shop    = self.context["request"].user.shops.first()
        product = Product.objects.create(shop=shop, **validated_data)
        for cut in cut_types_data:
            CutType.objects.create(product=product, **cut)
        return product