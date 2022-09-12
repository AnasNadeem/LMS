from leads.models_user import Account, AccountUser, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'is_staff',
                  'is_active',
                  'date_joined',
                  )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': ('User already exist with this email')})
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AccountwithAccountUserSerializer(serializers.ModelSerializer):
    account_users = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'business_desc',
            'account_users',
        )

    def get_account_users(self, obj):
        account = Account.objects.get(pk=obj.id)
        account_users = account.accountuser_set.all()
        account_users_serializer = AccountUserSerializer(account_users, many=True)
        return account_users_serializer.data


class AccountUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountUser
        fields = '__all__'
