from leads.models import (User,
                          Account,
                          LeadAttribute,
                          Lead,
                          LeadUserMap
                          )
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)

    class Meta:
        model = User
        fields = '__all__'
