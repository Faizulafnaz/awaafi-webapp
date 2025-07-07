from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta
from .models import Product, ProductVariant, Category, Cart, CartItem, Order, OrderItem



@admin.register(Category)
class CategoryAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Number of Products'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff', 'Kitchen']).exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

@admin.register(Product)
class ProductAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'category', 'variant_count', 'image_preview')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'category__name')
    ordering = ('name',)
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'description', 'category')}),
        ('Image', {'fields': ('image', 'image_preview')}),
    )
    
    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Variants'
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff', 'Kitchen']).exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

@admin.register(ProductVariant)
class ProductVariantAdmin(SimpleHistoryAdmin):
    list_display = ('product', 'name', 'price', 'is_available')
    list_filter = ('is_available', 'product__category')
    search_fields = ('product__name', 'name')
    ordering = ('product__name', 'name')
    
    fieldsets = (
        ('Product Information', {'fields': ('product', 'name')}),
        ('Pricing & Availability', {'fields': ('price', 'is_available')}),
    )
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('variant', 'quantity')
    can_delete = False

@admin.register(Cart)
class CartAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'item_count', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'total_amount')
    ordering = ('-created_at',)
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Cart Information', {'fields': ('user', 'created_at')}),
        ('Summary', {'fields': ('total_amount',)}),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def total_amount(self, obj):
        total = sum(item.variant.price * item.quantity for item in obj.items.all())
        return f"£{total:.2f}"
    total_amount.short_description = 'Total'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

@admin.register(CartItem)
class CartItemAdmin(SimpleHistoryAdmin):
    list_display = ('cart', 'variant', 'quantity', 'total_price')
    list_filter = ('variant__product__category',)
    search_fields = ('cart__user__email', 'variant__product__name', 'variant__name')
    readonly_fields = ('cart', 'variant', 'quantity')
    
    def total_price(self, obj):
        return f"£{obj.variant.price * obj.quantity:.2f}"
    total_price.short_description = 'Total Price'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price')
    can_delete = False

@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'user', 'status', 'total', 'item_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id', 'stripe_payment_intent')
    readonly_fields = ('created_at', 'stripe_payment_intent', 'total')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {'fields': ('user', 'address', 'status')}),
        ('Payment', {'fields': ('total', 'stripe_payment_intent')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff', 'Kitchen']).exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff']).exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff']).exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

@admin.register(OrderItem)
class OrderItemAdmin(SimpleHistoryAdmin):
    list_display = ('order', 'product', 'variant', 'quantity', 'price', 'total_price')
    list_filter = ('product__category',)
    search_fields = (
        'order__user__email', 
        'product__name', 
        'product__description',
        'variant__name', 
        'order__id',
        'order__status',
        'order__created_at'
    )
    readonly_fields = ('order', 'product', 'variant', 'quantity', 'price')
    
    def total_price(self, obj):
        return f"£{obj.price * obj.quantity:.2f}"
    total_price.short_description = 'Total Price'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff', 'Kitchen']).exists()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff']).exists()
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Staff']).exists()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()