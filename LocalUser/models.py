#Developer : SURENDRA 
#date : 2-Oct-2022
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, profile_id, date_of_birth, password=None):
        print("IN CRATE USER")
        if not email:
            raise ValueError('Users must have an email address')
        print("EMAIL IS "+str(email))
        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            profile_id=profile_id
        )

        print(user)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password=None):
        print("INC SUPERUSER")
        # print("")
        company = Company.objects.create(
            company_name="admin",
            allotted=100.00,
            employees=1,
            gst="Planner"
        )
        company.save()
        profile = UserProfile.objects.create(
            first_name="admin",
            last_name="admin",
            email=self.normalize_email(email),
            regular=True,
            company_name=company,
        )
        profile.save()
        # profile_id=1
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            date_of_birth=date_of_birth,
            profile_id=profile
        )
        user.is_admin = True
        user.is_superuser = True
        # user.is_staff = True

        user.save(using=self._db)
        return user



class LocalUser(AbstractBaseUser):
    username = None
    profile_id = models.ForeignKey(
        'UserProfile', on_delete=models.DO_NOTHING, null=True, unique=True
    )
    email = models.EmailField(
        verbose_name='email address',
        unique=True,
        max_length=255
        # unique=True,
    )
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth',]

    def get_full_name(self):
        
        return self.email

    def get_short_name(self):
        
        return self.email

    def get_username(self):
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
       
        return True

    def has_module_perms(self, app_label):
       
        return True

    @property
    def is_staff(self):
        
        return self.is_admin


class Company(models.Model):
    company_name = models.CharField(max_length=300)
    company_razorpay = models.CharField(max_length=300, default="RAZORPAY")
    address = models.TextField(max_length=1000)
    gst = models.CharField(max_length=15)
  
    employees = models.IntegerField()
    disabled = models.BooleanField(default=False)
    allotted = models.FloatField()
    hourly_rate = models.FloatField(default=0)

    def __str__(self):
        return self.company_name


class UserProfile(models.Model):
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    regular = models.BooleanField(default=False)
    company_name = models.ForeignKey('Company', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.first_name+" "+self.last_name


class GmailAccount(models.Model):
    user_profile_id = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    gmail_id = models.CharField(max_length=500)

    def __str__(self):
        return self.gmail_id


class ForgotPasswordTokens(models.Model):
    localuser = models.ForeignKey('LocalUser', on_delete=models.CASCADE)
    token = models.BigIntegerField()


