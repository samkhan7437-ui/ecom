from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'subcategory', 'price', 'pub_date', 'image')
    list_filter = ('category', 'subcategory', 'pub_date')
    search_fields = ('product_name', 'desc', 'category', 'subcategory')
    list_editable = ('price', 'category', 'subcategory')
    list_per_page = 20
    ordering = ('-pub_date',)
    fieldsets = (
        ('Product Information', {
            'fields': ('product_name', 'desc', 'price', 'image')
        }),
        ('Classification', {
            'fields': ('category', 'subcategory')
        }),
        ('Metadata', {
            'fields': ('pub_date',)
        }),
    )


# Customize admin site branding
admin.site.site_header = "NEXUS LUXE — Inventory Control Panel"
admin.site.site_title = "NEXUS LUXE Admin"
admin.site.index_title = "Manage Your Storefront"