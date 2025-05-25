from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名必须提供')
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须有 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须有 is_superuser=True')

        return self.create_user(username, email, password, **extra_fields)


class SysRole(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='角色编码')
    name = models.CharField(max_length=100, verbose_name='角色名称')
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='角色描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_role'
        verbose_name = '系统角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SysUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='真实姓名')
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name='邮箱')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='手机号')
    status = models.BooleanField(default=True, verbose_name='状态：0-禁用，1-启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    is_staff = models.BooleanField(default=False, verbose_name='是否是管理员')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    roles = models.ManyToManyField(SysRole, through='SysUserRole', verbose_name='角色')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'sys_user'
        verbose_name = '系统用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username or self.name or ''


class SysUserRole(models.Model):
    user = models.ForeignKey(SysUser, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(SysRole, on_delete=models.CASCADE, verbose_name='角色')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sys_user_role'
        verbose_name = '用户角色关联'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user}-{self.role}"
