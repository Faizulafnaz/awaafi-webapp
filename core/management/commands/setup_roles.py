from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Order, OrderItem, Product, ProductVariant, Category, Cart, CartItem
from accounts.models import User, Address


class Command(BaseCommand):
    help = 'Set up role-based access control for Awaafi Restaurant'

    def handle(self, *args, **options):
        self.stdout.write('Setting up role-based access control...')
        
        # Get content types
        user_ct = ContentType.objects.get_for_model(User)
        address_ct = ContentType.objects.get_for_model(Address)
        order_ct = ContentType.objects.get_for_model(Order)
        orderitem_ct = ContentType.objects.get_for_model(OrderItem)
        product_ct = ContentType.objects.get_for_model(Product)
        productvariant_ct = ContentType.objects.get_for_model(ProductVariant)
        category_ct = ContentType.objects.get_for_model(Category)
        cart_ct = ContentType.objects.get_for_model(Cart)
        cartitem_ct = ContentType.objects.get_for_model(CartItem)
        
        # Create or get groups
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Manager group'))
        
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Staff group'))
        
        kitchen_group, created = Group.objects.get_or_create(name='Kitchen')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Kitchen group'))
        
        # Clear existing permissions
        manager_group.permissions.clear()
        staff_group.permissions.clear()
        kitchen_group.permissions.clear()
        
        # Manager permissions (full access except user management)
        manager_permissions = Permission.objects.filter(
            content_type__in=[
                order_ct, orderitem_ct, product_ct, productvariant_ct, 
                category_ct, cart_ct, cartitem_ct, address_ct
            ]
        )
        manager_group.permissions.set(manager_permissions)
        self.stdout.write(self.style.SUCCESS('✓ Set Manager permissions'))
        
        # Staff permissions (limited access)
        staff_permissions = Permission.objects.filter(
            content_type__in=[order_ct, orderitem_ct, product_ct, category_ct],
            codename__in=['view_order', 'change_order', 'view_orderitem', 'change_orderitem',
                         'view_product', 'view_category']
        )
        staff_group.permissions.set(staff_permissions)
        self.stdout.write(self.style.SUCCESS('✓ Set Staff permissions'))
        
        # Kitchen permissions (view only)
        kitchen_permissions = Permission.objects.filter(
            content_type__in=[order_ct, orderitem_ct, product_ct, category_ct],
            codename__in=['view_order', 'view_orderitem', 'view_product', 'view_category']
        )
        kitchen_group.permissions.set(kitchen_permissions)
        self.stdout.write(self.style.SUCCESS('✓ Set Kitchen permissions'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Role-based access control setup complete!'))
        self.stdout.write('\n📋 Role Summary:')
        self.stdout.write('  • Manager: Full access to orders, products, categories, carts, addresses')
        self.stdout.write('  • Staff: View/edit orders, view products and categories')
        self.stdout.write('  • Kitchen: View orders and products only')
        self.stdout.write('\n💡 Next steps:')
        self.stdout.write('  1. Go to /admin/auth/user/ to assign users to groups')
        self.stdout.write('  2. Test different user roles')
        self.stdout.write('  3. Consider adding django-simple-history for audit logging') 