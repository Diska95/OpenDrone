from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, DesignerProfile, PrintNodeProfile, AssemblyCenterProfile


class DesignerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignerProfile
        fields = '__all__'
        read_only_fields = ['user', 'total_royalties_earned', 'rating', 'total_reviews']


class PrintNodeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintNodeProfile
        fields = '__all__'
        read_only_fields = ['user', 'rating', 'rating_by_material', 'is_certified',
                            'current_load', 'total_orders_completed', 'total_revenue']


class AssemblyCenterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssemblyCenterProfile
        fields = '__all__'
        read_only_fields = ['user', 'rating', 'is_certified', 'total_orders_completed']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=['designer', 'print_node', 'assembly_center', 'customer'],
        write_only=True, default='customer'
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Le password non coincidono.'})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', 'customer')
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.roles = [role]
        if 'customer' not in user.roles:
            user.roles.append('customer')
        user.save()
        if role == 'designer':
            DesignerProfile.objects.create(user=user)
        elif role == 'print_node':
            PrintNodeProfile.objects.create(
                user=user, business_name='', address='', city='', province='IT'
            )
        elif role == 'assembly_center':
            AssemblyCenterProfile.objects.create(
                user=user, business_name='', address='', city='', province='IT'
            )
        return user


class UserSerializer(serializers.ModelSerializer):
    designer_profile = serializers.SerializerMethodField()
    print_node_profile = serializers.SerializerMethodField()
    assembly_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'bio', 'avatar',
            'roles', 'is_verified', 'is_staff', 'is_superuser', 'is_active',
            'stripe_account_id',
            'designer_profile', 'print_node_profile', 'assembly_profile',
            'created_at',
        ]
        read_only_fields = ['id', 'email', 'roles', 'is_verified', 'is_staff', 'is_superuser', 'is_active', 'stripe_account_id', 'created_at']

    def get_designer_profile(self, obj):
        if hasattr(obj, 'designer_profile'):
            return DesignerProfileSerializer(obj.designer_profile).data
        return None

    def get_print_node_profile(self, obj):
        if hasattr(obj, 'print_node_profile'):
            return PrintNodeProfileSerializer(obj.print_node_profile).data
        return None

    def get_assembly_profile(self, obj):
        if hasattr(obj, 'assembly_profile'):
            return AssemblyCenterProfileSerializer(obj.assembly_profile).data
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class DeleteAccountSerializer(serializers.Serializer):
    """Conferma cancellazione account (art. 17 GDPR).

    `confirmation` deve essere esattamente "ELIMINA" per evitare click
    accidentali. Localizzato all'italiano coerentemente con la UI.
    """
    password = serializers.CharField(required=True, write_only=True)
    confirmation = serializers.CharField(required=True)

    def validate_confirmation(self, value):
        if value.strip().upper() != 'ELIMINA':
            raise serializers.ValidationError(
                'Per confermare digita esattamente "ELIMINA".'
            )
        return value
