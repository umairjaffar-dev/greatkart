from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Create model to manage users.
class MyAccountManager(BaseUserManager):
    # Define a function to manage simple user
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address.')
        
        if not username:
            raise ValueError('User must have a username.')
        
        user = self.model(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = self.normalize_email(email)
        )
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    # Define a function to manage superuser.
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            first_name=first_name, 
            last_name=last_name,
            username=username,
            email=self.normalize_email(email), 
            password=password
        )
        
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        
        user.save(using=self._db)
        
        return user




# Create Custom User models here.
class Account(AbstractBaseUser):
    # Modles Fields: fname, lname, email, phone
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=100, unique=True)
    email           = models.EmailField(max_length=100, unique=True)
    phone_number    = models.CharField(max_length=50)
    
    # Required fields when user is created.
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    is_superadmin   = models.BooleanField(default=False)
    
    # 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Tell this account to use MyAccountManager.
    objects = MyAccountManager()
    
    # string representing model
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
        
    def has_module_perms(self, add_label):
        return True
    
