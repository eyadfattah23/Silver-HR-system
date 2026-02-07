from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    list_display = ('id', 'first_name', 'rest_of_name', 'email', 'phone_number1', 'date_joined')
    search_fields = ('first_name', 'phone_number1')
    list_filter = ('date_joined',)
    ordering = ('first_name', 'created_at')
    
    