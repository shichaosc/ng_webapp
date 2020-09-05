from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer


class UserSerializer(UserDetailsSerializer):

    user_id = serializers.CharField(source="id")
    avatar = serializers.ImageField(source="userprofile.avatar")

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('user_id', 'avatar', )