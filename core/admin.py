from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, Reservation, ReservationItem, JournalEntry, Article, Feedback, Order, OrderItem, Cart, CartItem, OrderTracking, UserHistory, Invoice


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price_display", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'is_active')
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        return f"${obj.price:.2f}"
    price_display.short_description = 'Price'

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 200px; max-height: 200px;" />')
        return "No image"
    image_preview.short_description = 'Preview'


class ReservationItemInline(admin.TabularInline):
    model = ReservationItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'special_instructions')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "reservation_type", "scheduled_for", "status", "total_amount")
    list_filter = ("status", "reservation_type", "scheduled_for")
    search_fields = ("customer__username", "contact_phone")
    inlines = [ReservationItemInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'reservation_type', 'scheduled_for', 'status')
        }),
        ('Contact & Location', {
            'fields': ('contact_phone', 'address')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    search_fields = ("title", "author__username")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "published_at")
    list_filter = ("published",)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_price')
    fields = ('product', 'quantity', 'price', 'total_price')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'status', 'location_name', 'estimated_delivery', 'updated_at')
    list_filter = ('status', 'updated_at', 'created_at')
    search_fields = ('order__id', 'location_name', 'order__customer__username', 'order__customer__email')
    readonly_fields = ('created_at', 'updated_at', 'map_preview')
    list_editable = ('status',)
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_out_for_delivery', 'mark_delivered']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'customer_name')
        }),
        ('Status & Timeline', {
            'fields': ('status', 'estimated_delivery')
        }),
        ('GPS Location Tracking', {
            'fields': ('latitude', 'longitude', 'location_name', 'map_preview'),
            'description': 'Enter GPS coordinates to show live location on customer tracking map. Format: Latitude (e.g., 14.5994), Longitude (e.g., 120.9842)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_id(self, obj):
        return f"Order #{obj.order.id:06d}"
    order_id.short_description = 'Order #'
    order_id.admin_order_field = 'order__id'

    def customer_name(self, obj):
        customer = obj.order.customer
        return f"{customer.get_full_name() or customer.username}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'order__customer__username'

    def status_badge(self, obj):
        status_colors = {
            'order_placed': 'gray',
            'confirmed': 'blue',
            'preparing': 'orange',
            'ready_for_pickup': 'purple',
            'out_for_delivery': 'cyan',
            'delivered': 'green',
            'cancelled': 'red'
        }
        return mark_safe(
            f'<span style="background: {status_colors.get(obj.status, "gray")}; '
            f'color: white; padding: 5px 10px; border-radius: 10px; font-size: 12px; font-weight: bold;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def quick_actions(self, obj):
        return mark_safe(
            f'<a class="button" href="{obj.id}/change/" style="background-color: #417690; padding: 5px 10px; border-radius: 4px; color: white; text-decoration: none;">Edit</a>'
        )
    quick_actions.short_description = 'Actions'

    def map_preview(self, obj):
        if obj.latitude and obj.longitude:
            map_html = f'''
            <div style="width: 100%; height: 300px; border: 2px solid #ddd; border-radius: 8px; margin-top: 10px;">
                <iframe width="100%" height="100%" frameborder="0" style="border-radius: 8px;"
                    src="https://www.openstreetmap.org/export/embed.html?bbox={obj.longitude-0.01},{obj.latitude-0.01},{obj.longitude+0.01},{obj.latitude+0.01}&layer=mapnik&marker={obj.latitude},{obj.longitude}">
                </iframe>
            </div>
            <p style="margin-top: 10px; font-size: 12px; color: #666;">
                <strong>Coordinates:</strong> {obj.latitude}, {obj.longitude}<br>
                <strong>Location:</strong> {obj.location_name or 'Not specified'}
            </p>
            '''
            return mark_safe(map_html)
        else:
            return mark_safe('<p style="color: #999; font-style: italic;">No GPS coordinates set yet. Enter latitude and longitude above to display map.</p>')
    map_preview.short_description = 'Map Preview'

    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"✓ {updated} order(s) marked as Confirmed")
    mark_confirmed.short_description = "✓ Mark as Confirmed"

    def mark_preparing(self, request, queryset):
        updated = queryset.update(status='preparing')
        self.message_user(request, f"✓ {updated} order(s) marked as Preparing")
    mark_preparing.short_description = "✓ Mark as Preparing"

    def mark_ready(self, request, queryset):
        updated = queryset.update(status='ready_for_pickup')
        self.message_user(request, f"✓ {updated} order(s) marked as Ready for Pickup")
    mark_ready.short_description = "✓ Mark as Ready for Pickup"

    def mark_out_for_delivery(self, request, queryset):
        updated = queryset.update(status='out_for_delivery')
        self.message_user(request, f"✓ {updated} order(s) marked as Out for Delivery")
    mark_out_for_delivery.short_description = "✓ Mark as Out for Delivery"

    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f"✓ {updated} order(s) marked as Delivered")
    mark_delivered.short_description = "✓ Mark as Delivered"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_link', 'total_amount_display', 'status_badge', 'created_at', 'order_actions')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'customer__username', 'customer__email', 'customer__first_name', 'customer__last_name')
    list_select_related = ('customer',)
    readonly_fields = ('created_at', 'updated_at', 'order_number')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_completed', 'mark_as_cancelled']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'total_amount', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_number(self, obj):
        return f"#{obj.id:06d}"
    order_number.short_description = 'Order #'

    def total_amount_display(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total'

    def customer_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.get_full_name() or obj.customer.username}</a>')
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer__username'

    def status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'cancelled': 'red'
        }
        return mark_safe(
            f'<span style="background: {status_colors.get(obj.status, "gray")}; '
            f'color: white; padding: 5px 10px; border-radius: 10px; font-size: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def order_actions(self, obj):
        return mark_safe(
            f'<a class="button" href="{obj.id}/change/">View</a> &nbsp;'
            f'<a class="button" href="{obj.id}/history/">History</a>'
        )
    order_actions.short_description = 'Actions'
    order_actions.allow_tags = True

    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        self.message_user(request, f"{updated} order(s) marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_completed(self, request, queryset):
        updated = queryset.exclude(status='cancelled').update(status='completed')
        self.message_user(request, f"{updated} order(s) marked as completed.")
    mark_as_completed.short_description = "Mark selected orders as Completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.exclude(status='completed').update(status='cancelled')
        self.message_user(request, f"{updated} order(s) marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"


# Custom User Admin with order information
class OrderInline(admin.StackedInline):
    model = Order
    extra = 0
    show_change_link = True
    readonly_fields = ('order_number', 'created_at', 'total_amount_display')
    fields = ('order_number', 'created_at', 'total_amount_display', 'status')

    def order_number(self, obj):
        return f"#{obj.id:06d}"
    order_number.short_description = 'Order #'

    def total_amount_display(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total'

    def has_add_permission(self, request, obj=None):
        return False


class CartInline(admin.StackedInline):
    model = Cart
    extra = 0
    show_change_link = True
    readonly_fields = ('total_items', 'total_price_display')
    fields = ('total_items', 'total_price_display', 'created_at')

    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total Value'

    def has_add_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'order_count', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [OrderInline, CartInline]

    def order_count(self, obj):
        return obj.order_set.count()
    order_count.short_description = 'Orders'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_display', 'description_short', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'user_agent', 'timestamp')
    date_hierarchy = 'timestamp'

    def action_display(self, obj):
        return obj.get_action_display()
    action_display.short_description = 'Action'

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Invoice Admin
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_link', 'order_id', 'total_amount_display', 'status_badge', 'issued_date')
    list_filter = ('status', 'issued_date')
    search_fields = ('invoice_number', 'customer__username', 'customer__email')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'customer', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address')
        }),
        ('Terms & Notes', {
            'fields': ('due_date', 'payment_terms', 'notes')
        }),
        ('Timestamps', {
            'fields': ('issued_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.customer.id])
        return mark_safe(f'<a href="{url}">{obj.customer.get_full_name() or obj.customer.username}</a>')
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer__username'
    
    def order_id(self, obj):
        return f"#{obj.order.id:06d}"
    order_id.short_description = 'Order #'
    
    def total_amount_display(self, obj):
        return f"₱{obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total'
    
    def status_badge(self, obj):
        status_colors = {
            'draft': 'gray',
            'issued': 'blue',
            'paid': 'green',
            'cancelled': 'red'
        }
        return mark_safe(
            f'<span style="background: {status_colors.get(obj.status, "gray")}; '
            f'color: white; padding: 5px 10px; border-radius: 10px; font-size: 12px;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


# Register all models with their admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)

# Admin site settings
admin.site.site_header = 'BBQ Grill Admin'
admin.site.site_title = 'BBQ Grill Administration'
admin.site.index_title = 'Site Administration'


