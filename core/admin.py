from store.models import Product
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from store.admin import ProductAdmin
from store.admin import ProductImageInline
from tags.models import TaggedItem
from core.models import User

class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline, ProductImageInline]

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets=(
        (None, {
        'classes':('wide',),
        'fields':('username','password1','password2','email','first_name','last_name'),
    }),
)

admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
