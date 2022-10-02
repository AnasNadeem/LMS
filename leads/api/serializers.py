from leads.models_user import Account, Member, User
from leads.models_lead import Lead, LeadAttribute
from rest_framework import serializers

######################
# ---- USER ---- #
######################


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
        fields = ('email', 'password')

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': ('User already exist with this email')})
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4)
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'password')
        read_only_fields = ('password', )


class OtpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    otp = serializers.CharField(max_length=10)

    class Meta:
        model = User
        fields = ('email', 'otp')


class UserEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('email',)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=250)

######################
# ---- ACCOUNT ---- #
######################


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'


class AccountwithMemberSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'business_desc',
            'subdomain',
            'members',
        )

    def get_members(self, obj):
        account = Account.objects.get(pk=obj.id)
        members = account.member_set.all()
        members_serializer = MemberWithUserSerializer(members, many=True)
        return members_serializer.data

######################
# ---- MEMBER ---- #
######################


class MemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = '__all__'


class MemberWithUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Member
        fields = '__all__'

######################
# ---- LEAD ---- #
######################


class LeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = '__all__'

######################
# ---- LEAD ATTRIBUTE ---- #
######################


class LeadAttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeadAttribute
        fields = '__all__'
