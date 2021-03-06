from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin)

from helpers import IntegerRangeField
from helpers import roles
from tasks import update_indexes


class ExtUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, location, first_name,
                    password, last_name, age, desired_salary, other, role):
        """
        Creates and saves a User with the given email, date_of_birth, location,
        first_name, last_name, age, desired_salary, other and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            location=location,
            first_name=first_name,
            last_name=last_name,
            age=age,
            desired_salary=desired_salary,
            other=other,
            role=role
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, date_of_birth, location, first_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            location=location,
            first_name=first_name,
            role=roles.ROLE_ADMIN
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


class ExtUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(verbose_name='First name', max_length=40)
    last_name = models.CharField(verbose_name='Last name', max_length=40)
    email = models.EmailField(verbose_name='Email address', max_length=255, unique=True)
    date_of_birth = models.DateField(verbose_name='Birthday')
    is_active = models.BooleanField(verbose_name='Is active', default=True)
    role = IntegerRangeField(verbose_name='Role', min_value=0, max_value=2, default=roles.ROLE_USER)
    age = models.IntegerField(verbose_name='Age', blank=True, null=True)
    desired_salary = models.IntegerField(verbose_name='Desired salary', blank=True, null=True)
    register_date = models.DateField(verbose_name='Register date', auto_now_add=True)
    last_change = models.DateTimeField(verbose_name='Last change', auto_now=True)
    location = models.CharField(verbose_name='Location', max_length=40)
    other = models.TextField(verbose_name='Other informations', blank=True)

    objects = ExtUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'date_of_birth', 'location']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        if self.role == roles.ROLE_ADMIN:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        super(ExtUser, self).save(*args, **kwargs)
        update_indexes.delay()
