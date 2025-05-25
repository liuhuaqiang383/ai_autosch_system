from rest_framework import serializers
from .models import SysUser, SysRole, SysUserRole


class SysRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRole
        fields = '__all__'


class SysUserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_code = serializers.CharField(source='role.code', read_only=True)

    class Meta:
        model = SysUserRole
        fields = '__all__'


class SysUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    user_roles = SysUserRoleSerializer(source='sysuserrole_set', many=True, read_only=True)
    role_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = SysUser
        fields = ['id', 'username', 'name', 'email', 'phone', 'status', 'password',
                  'is_active', 'is_staff', 'user_roles', 'role_ids', 'create_time', 'update_time']
        read_only_fields = ['create_time', 'update_time']

    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password', None)
        user = SysUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        # 添加角色
        for role_id in role_ids:
            try:
                role = SysRole.objects.get(id=role_id)
                SysUserRole.objects.create(user=user, role=role)
            except SysRole.DoesNotExist:
                pass

        return user

    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        password = validated_data.pop('password', None)

        # 更新用户信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 更新密码
        if password:
            instance.set_password(password)

        instance.save()

        # 更新角色
        if role_ids is not None:
            # 先删除现有的所有角色关系
            instance.sysuserrole_set.all().delete()
            # 添加新的角色关系
            for role_id in role_ids:
                try:
                    role = SysRole.objects.get(id=role_id)
                    SysUserRole.objects.create(user=instance, role=role)
                except SysRole.DoesNotExist:
                    pass

        return instance 