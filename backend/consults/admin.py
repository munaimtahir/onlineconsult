from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Department, User, Patient, ConsultRequest, ConsultComment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'email', 'department', 'role', 'is_staff']
    list_filter = ['role', 'department', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'department', 'role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'department', 'role')}),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['hospital_id', 'name', 'age', 'gender', 'created_at']
    search_fields = ['hospital_id', 'name']
    list_filter = ['gender']


@admin.register(ConsultRequest)
class ConsultRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'from_department', 'to_department', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'from_department', 'to_department']
    search_fields = ['patient__name', 'patient__hospital_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ConsultComment)
class ConsultCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'consult', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message', 'author__username']
    readonly_fields = ['created_at']
