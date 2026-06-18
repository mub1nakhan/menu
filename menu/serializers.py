"""
menu/serializers.py
"""
from rest_framework import serializers

from menu.models import MenuCategory, Product


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ["id", "branch", "name_i18n", "sort_order", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name_i18n(self, value):
        if not isinstance(value, dict) or not value:
            raise serializers.ValidationError("name_i18n must be a non-empty object, e.g. {'en': 'Soups'}")
        return value


class ProductSerializer(serializers.ModelSerializer):
    margin = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "branch", "category", "name_i18n", "description_i18n", "image_url",
            "price", "cost_price", "is_available", "prep_time_minutes", "sort_order",
            "margin", "created_at",
        ]
        read_only_fields = ["id", "cost_price", "margin", "created_at"]

    def validate_name_i18n(self, value):
        if not isinstance(value, dict) or not value:
            raise serializers.ValidationError("name_i18n must be a non-empty object, e.g. {'en': 'Burger'}")
        return value

    def validate_category(self, category: MenuCategory):
        """Ensure the category belongs to the same restaurant as the request's user."""
        request = self.context["request"]
        if category.restaurant_id != request.user.restaurant_id:
            raise serializers.ValidationError("Category does not belong to your restaurant.")
        return category


class PublicProductSerializer(serializers.ModelSerializer):
    """
    Customer-facing serializer (QR menu app): resolves name_i18n/description_i18n
    down to a single string in the requested language, instead of exposing the
    raw JSON blob, and never exposes cost_price/margin.
    """
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "category", "name", "description", "image_url", "price", "prep_time_minutes"]

    def _localized(self, i18n: dict, fallback: str = "") -> str:
        lang = self.context.get("lang", "en")
        return i18n.get(lang) or i18n.get("en") or i18n.get("uz") or fallback

    def get_name(self, obj: Product) -> str:
        return self._localized(obj.name_i18n)

    def get_description(self, obj: Product) -> str:
        return self._localized(obj.description_i18n)