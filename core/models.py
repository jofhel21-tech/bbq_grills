from __future__ import annotations
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Product(models.Model):
    """BBQ products model."""
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Available stock quantity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    @property
    def stock_status(self):
        """Get stock status display."""
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity <= 5:
            return "Low Stock"
        else:
            return "In Stock"
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False
    
    def add_stock(self, quantity):
        """Add stock quantity."""
        self.stock_quantity += quantity
        self.save()


class Article(models.Model):
    """Blog articles model."""
    title = models.CharField(max_length=200)
    body = models.TextField()
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-id']

    def __str__(self):
        return self.title

    def publish(self):
        """Publish the article."""
        self.published = True
        self.published_at = timezone.now()
        self.save()


class Feedback(models.Model):
    """Customer feedback model."""
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"


class JournalEntry(models.Model):
    """Personal journal entries model."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Reservation(models.Model):
    """Reservation booking model for BBQ orders."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    RESERVATION_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
        ('dine_in', 'Dine In'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='ReservationItem')
    reservation_type = models.CharField(max_length=20, choices=RESERVATION_TYPE_CHOICES, default='pickup')
    scheduled_for = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Contact information
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Delivery/Pickup address
    address = models.TextField(blank=True, help_text="Delivery address or pickup location notes")
    
    notes = models.TextField(blank=True, help_text="Special instructions or requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_for']

    def __str__(self):
        return f"Reservation {self.id} - {self.customer.username} - {self.get_reservation_type_display()}"

    def get_status_display(self):
        """Return human-readable status."""
        return dict(self.STATUS_CHOICES)[self.status]

    def get_reservation_type_display(self):
        """Return human-readable reservation type."""
        return dict(self.RESERVATION_TYPE_CHOICES)[self.reservation_type]


class ReservationItem(models.Model):
    """Individual items within a reservation."""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True, help_text="Special cooking instructions for this item")

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.quantity * self.price


class Order(models.Model):
    """Order model for BBQ products."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Delivery location fields
    delivery_address = models.TextField(blank=True, help_text="Full delivery address")
    delivery_latitude = models.FloatField(null=True, blank=True, help_text="Delivery location latitude")
    delivery_longitude = models.FloatField(null=True, blank=True, help_text="Delivery location longitude")
    delivery_barangay = models.CharField(max_length=100, blank=True, help_text="Barangay/District in Naval")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"

    def get_status_display(self):
        """Return human-readable status."""
        return dict(self.STATUS_CHOICES)[self.status]
    
    def can_be_edited(self):
        """Check if order can be edited by customer."""
        # Cannot edit if order is completed or out for delivery
        if self.status in ['completed', 'out_for_delivery']:
            # Check if payment is successful
            successful_payment = self.payments.filter(status='completed').exists()
            if successful_payment:
                return False
        return True
    
    def can_be_deleted(self):
        """Check if order can be deleted by customer."""
        # Cannot delete if order is completed or out for delivery
        if self.status in ['completed', 'out_for_delivery']:
            # Check if payment is successful
            successful_payment = self.payments.filter(status='completed').exists()
            if successful_payment:
                return False
        return True


class OrderTracking(models.Model):
    """Order tracking information."""
    TRACKING_STATUS_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('confirmed', 'Order Confirmed'),
        ('preparing', 'Preparing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES, default='order_placed')
    
    # Current delivery location (driver/rider location)
    latitude = models.FloatField(null=True, blank=True, help_text="Current delivery person latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="Current delivery person longitude")
    location_name = models.CharField(max_length=255, blank=True, help_text="Current location name")
    
    # Customer location reference
    customer_latitude = models.FloatField(null=True, blank=True, help_text="Customer location latitude")
    customer_longitude = models.FloatField(null=True, blank=True, help_text="Customer location longitude")
    customer_location_name = models.CharField(max_length=255, blank=True, help_text="Customer location name")
    
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Tracking for Order {self.order.id}"

    def get_status_display(self):
        """Return human-readable status."""
        return dict(self.TRACKING_STATUS_CHOICES)[self.status]


class OrderItem(models.Model):
    """Individual items within an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.quantity * self.price


class Cart(models.Model):
    """Shopping cart for users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Individual items within a shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.quantity * self.product.price


class Payment(models.Model):
    """Payment transaction model."""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment details
    transaction_id = models.CharField(max_length=100, blank=True, help_text="External payment transaction ID")
    reference_number = models.CharField(max_length=50, blank=True, help_text="Payment reference number")
    payment_date = models.DateTimeField(null=True, blank=True, help_text="When payment was completed")
    
    # Additional info
    notes = models.TextField(blank=True, help_text="Payment notes or instructions")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='processed_payments', help_text="Staff member who processed payment")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.id} - ₱{self.amount} ({self.get_status_display()})"

    def get_status_display(self):
        """Return human-readable status."""
        return dict(self.PAYMENT_STATUS_CHOICES)[self.status]

    def get_payment_method_display(self):
        """Return human-readable payment method."""
        return dict(self.PAYMENT_METHOD_CHOICES)[self.payment_method]


class UserHistory(models.Model):
    """Track user activities and history."""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view_product', 'Viewed Product'),
        ('add_to_cart', 'Added to Cart'),
        ('remove_from_cart', 'Removed from Cart'),
        ('create_order', 'Created Order'),
        ('update_order', 'Updated Order'),
        ('cancel_order', 'Cancelled Order'),
        ('payment_initiated', 'Payment Initiated'),
        ('payment_completed', 'Payment Completed'),
        ('payment_failed', 'Payment Failed'),
        ('payment_cancelled', 'Payment Cancelled'),
        ('payment_refunded', 'Payment Refunded'),
        ('create_reservation', 'Created Reservation'),
        ('update_reservation', 'Updated Reservation'),
        ('cancel_reservation', 'Cancelled Reservation'),
        ('create_journal', 'Created Journal Entry'),
        ('update_journal', 'Updated Journal Entry'),
        ('delete_journal', 'Deleted Journal Entry'),
        ('submit_feedback', 'Submitted Feedback'),
        ('view_page', 'Viewed Page'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User Histories'

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_action_display(self):
        """Return human-readable action."""
        return dict(self.ACTION_CHOICES)[self.action]


class Invoice(models.Model):
    """Invoice model for orders."""
    INVOICE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True, help_text="Unique invoice number")
    
    # Invoice details
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='draft')
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Tax or VAT amount")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount amount if any")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Customer information
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_address = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True, help_text="Additional notes or terms")
    payment_terms = models.CharField(max_length=100, blank=True, help_text="e.g., Due upon receipt")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.username}"
    
    def get_status_display(self):
        """Return human-readable status."""
        return dict(self.INVOICE_STATUS_CHOICES)[self.status]
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.due_date and self.status != 'paid':
            from datetime import date
            return date.today() > self.due_date
        return False
