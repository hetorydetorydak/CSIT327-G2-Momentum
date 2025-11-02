from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError

class Role(models.Model):
    role_id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.role_name

class Employee(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    department = models.CharField(max_length=150, blank=True, null=True)
    position = models.CharField(max_length=150, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    email_address = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def email_exists(cls, email):
        return cls.objects.filter(email_address__iexact=email).exists()

class UserAccount(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='accounts')
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    last_login = models.DateTimeField(null=True, blank=True, default=None)
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @classmethod
    def username_exists(cls, username):
        return cls.objects.filter(username__iexact=username).exists()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.objects.filter(username__iexact=username).first()
    
    @classmethod
    def create_employee_user(cls, employee_data, username, password, role_id=303):
        from django.db import transaction
        
        role = Role.objects.filter(pk=role_id).first()
        if not role:
            role, _ = Role.objects.get_or_create(
                role_id=303, 
                defaults={
                    "role_name": "Employee", 
                    "description": "Standard employee"
                }
            )
        
        with transaction.atomic():
            employee = Employee.objects.create(**employee_data)
            user = cls(
                employee=employee,
                username=username,
                role=role
            )
            user.set_password(password)
            user.save()
        
        return user

    # make models work with Django's auth
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_username(self):
        return self.username