from django.db import models
from django.contrib.auth.models import User,AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from shortuuidfield import ShortUUIDField

# override User-model
class UserStatusChoices(models.IntegerChoices):
    ACTIVE = 1,'Active' #已经激活的
    INACTIVE = 2,'Inactive'  # 没有激活的
    LOCKED = 3,'Locked'   # 被锁定

class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        creates user
        """
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        # GlobalUserModel = apps.get_model(
        #     self.model._meta.app_label, self.model._meta.object_name
        # )
        # username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields) # self.model = OAUser
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """创建普通用户 Create a normal user """
        extra_fields.setdefault("is_staff", True)   # OA system is for employees only
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create superuser with all permissions 创建超级用户"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('status', UserStatusChoices.ACTIVE)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)



class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    custom user model .
    """

    # username_validator = UnicodeUsernameValidator()
    uid = ShortUUIDField(primary_key=True)   # ShortUUIDField
    username = models.CharField(
        # _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(unique=True, blank=False)  # email must be unique and cannot be empty
    telephone =models.CharField(max_length=20, blank=True )
    is_staff = models.BooleanField(default=False)
    status = models.IntegerField(choices=UserStatusChoices.choices, default=UserStatusChoices.INACTIVE) # 默认是未激活
    is_active = models.BooleanField(default=True) #其实status已经包含了active，但是Django需要这个属性，我们项目只需要关注status即可
    date_joined = models.DateTimeField(auto_now_add=True)

    department = models.ForeignKey('OADepartment', null=True, on_delete=models.SET_NULL, related_name='staffs',
                                   related_query_name='staffs')

    objects = OAUserManager()

    EMAIL_FIELD = "email"
    # USERNAME_FIELD used for authentication
    # 此处是USERNAME_FIELD 使用来做鉴权的，会把authenticate的username参数，传给USERNAME_FIELD指定的字段
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS：指定哪些字段是必须要传的，但是不能重复包含USERNAME_FIELD和EMAIL_FIELD已经设置过的值
    REQUIRED_FIELDS = ['username','password']



    def clean(self):  # Standardized email
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

class OADepartment(models.Model):
    name = models.CharField(max_length=100)
    intro = models.CharField(max_length=200)
    # leader: The leader is responsible for a department
    leader = models.OneToOneField(OAUser, null=True, on_delete=models.SET_NULL, related_name='leader_department', related_query_name='leader_department')
    # manager : belongs to the board, a manager can manage multiple departments
    manager = models.ForeignKey(OAUser, null=True, on_delete=models.SET_NULL, related_name='manager_departments', related_query_name='manager_departments')
