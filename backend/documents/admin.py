from django.contrib import admin
from .models import DocumentType, Document


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'document_type', 'file_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'document_type']
    search_fields = ['file_name', 'employee__first_name', 'employee__fourth_name']
    raw_id_fields = ['employee', 'uploaded_by']
