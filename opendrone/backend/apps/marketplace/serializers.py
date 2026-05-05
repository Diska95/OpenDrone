from rest_framework import serializers
from .models import DroneProject, ProjectFile, BOMItem, DroneCategory, ProjectReview, Brand
from apps.users.serializers import UserSerializer


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'website', 'default_supplier_url',
                  'categories', 'is_partner', 'description']


class DroneCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneCategory
        fields = ['id', 'name', 'slug', 'icon', 'description']
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'icon': {'required': False, 'allow_blank': True},
        }

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Nome troppo corto.')
        if len(value) > 100:
            raise serializers.ValidationError('Nome troppo lungo (max 100).')
        return value

    def create(self, validated_data):
        from django.utils.text import slugify
        name = validated_data['name']
        base_slug = slugify(name) or 'cat'
        slug = base_slug
        n = 1
        while DroneCategory.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{n}'
            n += 1
        validated_data['slug'] = slug
        return super().create(validated_data)


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = '__all__'
        read_only_fields = ['project']
        extra_kwargs = {
            'filename': {'required': False, 'allow_blank': True},
            'file_type': {'required': False},
        }


class BOMItemSerializer(serializers.ModelSerializer):
    brand_data = BrandSerializer(source='brand', read_only=True)

    class Meta:
        model = BOMItem
        fields = '__all__'
        read_only_fields = ['project']


class ProjectReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectReview
        fields = '__all__'
        read_only_fields = ['reviewer', 'project']

    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name}".strip() or obj.reviewer.email


class DroneProjectListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    designer_name = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    bom_total_cost = serializers.SerializerMethodField()

    class Meta:
        model = DroneProject
        fields = [
            'id', 'slug', 'title', 'short_description', 'category', 'category_name',
            'designer_name', 'difficulty', 'license_type', 'royalty_percentage',
            'status', 'estimated_total_cost_min', 'estimated_total_cost_max',
            'rating', 'total_reviews', 'order_count', 'is_featured',
            'is_university_project', 'cover_image', 'bom_total_cost',
            'use_cases', 'created_at',
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_designer_name(self, obj):
        return f"{obj.designer.first_name} {obj.designer.last_name}".strip() or obj.designer.email

    def get_cover_image(self, obj):
        img = obj.files.filter(file_type='image', is_public=True).first()
        if img and img.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(img.file.url)
        return None

    def get_bom_total_cost(self, obj):
        total = sum(item.unit_price_eur * item.quantity for item in obj.bom_items.all())
        return float(total)


class DroneProjectDetailSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, read_only=True)
    bom_items = BOMItemSerializer(many=True, read_only=True)
    reviews = ProjectReviewSerializer(many=True, read_only=True)
    designer = UserSerializer(read_only=True)
    category_data = DroneCategorySerializer(source='category', read_only=True)
    bom_total_cost = serializers.SerializerMethodField()

    class Meta:
        model = DroneProject
        fields = '__all__'
        read_only_fields = [
            'designer', 'slug', 'status', 'view_count', 'download_count',
            'order_count', 'fork_count', 'rating', 'total_reviews',
            'published_at', 'created_at', 'updated_at',
        ]

    def get_bom_total_cost(self, obj):
        total = sum(item.unit_price_eur * item.quantity for item in obj.bom_items.all())
        return float(total)


class DroneProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneProject
        fields = [
            'id', 'slug', 'status',
            'title', 'description', 'short_description', 'category',
            'license_type', 'royalty_percentage', 'difficulty',
            'estimated_weight_grams', 'estimated_flight_time_minutes',
            'max_payload_grams', 'operating_range_km', 'use_cases',
            'easa_category', 'compliance_notes', 'is_university_project', 'version',
        ]
        read_only_fields = ['id', 'slug', 'status']
