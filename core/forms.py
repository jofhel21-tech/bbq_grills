from __future__ import annotations
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation, ReservationItem, JournalEntry, Article, Feedback, Order, OrderItem, Product, OrderTracking, Payment, Invoice


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address")
    first_name = forms.CharField(max_length=30, required=False, help_text="Optional")
    last_name = forms.CharField(max_length=30, required=False, help_text="Optional")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Add help text for password fields
        self.fields['password1'].help_text = "At least 8 characters with uppercase, lowercase, and numbers"
        self.fields['password2'].help_text = "Re-enter your password to confirm"


class ReservationForm(forms.ModelForm):
    scheduled_for = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Pickup/Delivery Time"
    )
    
    class Meta:
        model = Reservation
        fields = ["reservation_type", "scheduled_for", "contact_phone", "address", "notes"]
        widgets = {
            'reservation_type': forms.Select(attrs={'class': 'form-select'}),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 09123456789'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Delivery address or pickup location notes'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions or requests'
            }),
        }
        labels = {
            'reservation_type': 'Service Type',
            'contact_phone': 'Contact Phone',
            'address': 'Address/Location',
            'notes': 'Special Instructions',
        }


class ReservationItemForm(forms.ModelForm):
    """Form for adding items to a reservation."""
    class Meta:
        model = ReservationItem
        fields = ["product", "quantity", "special_instructions"]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'max': 99, 
                'value': 1
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special cooking instructions for this item'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['product'].empty_label = "Select a product"
        self.fields['special_instructions'].required = False


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ["title", "content"]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "published"]


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["message"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "notes", "delivery_address", "delivery_barangay", "delivery_latitude", "delivery_longitude"]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter your full delivery address'}),
            'delivery_barangay': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Barangay Caraycaray'}),
            'delivery_latitude': forms.HiddenInput(),
            'delivery_longitude': forms.HiddenInput(),
        }
        labels = {
            'delivery_address': 'Delivery Address',
            'delivery_barangay': 'Barangay/District',
            'delivery_latitude': 'Latitude',
            'delivery_longitude': 'Longitude',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Remove status field for regular users (non-staff)
        if user and not user.is_staff:
            self.fields.pop('status', None)
            # Make delivery fields required for customers
            self.fields['delivery_address'].required = True
            self.fields['delivery_barangay'].required = True


class AddOrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 99, 'value': 1})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['product'].empty_label = "Select a product"


class OrderTrackingForm(forms.ModelForm):
    """Form for updating order tracking information."""
    estimated_delivery = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        required=False,
        help_text="Set the estimated delivery date and time"
    )
    
    class Meta:
        model = OrderTracking
        fields = ['status', 'latitude', 'longitude', 'location_name', 'estimated_delivery']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 14.5994',
                'step': '0.0001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 120.9842',
                'step': '0.0001'
            }),
            'location_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Downtown Branch, En Route to Customer'
            }),
        }
        labels = {
            'status': 'Order Status',
            'latitude': 'Latitude (GPS)',
            'longitude': 'Longitude (GPS)',
            'location_name': 'Location Name',
            'estimated_delivery': 'Estimated Delivery Time',
        }
        help_texts = {
            'latitude': 'Enter latitude coordinate (e.g., 14.5994)',
            'longitude': 'Enter longitude coordinate (e.g., 120.9842)',
            'location_name': 'Describe the current location (e.g., "Preparing at Kitchen", "Out for Delivery")',
        }


class PaymentForm(forms.ModelForm):
    """Form for managing payment transactions."""
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        required=False,
        help_text="When was the payment completed?"
    )
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'status', 'transaction_id', 'reference_number', 
                 'payment_date', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., TXN123456789'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., REF-2024-001'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Payment notes or special instructions...'
            }),
        }
        labels = {
            'amount': 'Payment Amount (₱)',
            'payment_method': 'Payment Method',
            'status': 'Payment Status',
            'transaction_id': 'Transaction ID',
            'reference_number': 'Reference Number',
            'payment_date': 'Payment Date',
            'notes': 'Notes',
        }


class CheckoutForm(forms.Form):
    """Form for checkout with payment method selection."""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Payment Method',
        initial='cash'
    )
    
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your complete delivery address'
        }),
        label='Delivery Address',
        required=True
    )
    
    delivery_barangay = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Barangay Caraycaray'
        }),
        label='Barangay/District',
        required=True
    )
    
    delivery_latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    delivery_longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    order_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any special instructions for your order...'
        }),
        label='Order Notes (Optional)',
        required=False
    )


class ProductSearchForm(forms.Form):
    """Form for searching and filtering products."""
    SORT_CHOICES = [
        ('name', 'Name (A-Z)'),
        ('-name', 'Name (Z-A)'),
        ('price', 'Price (Low to High)'),
        ('-price', 'Price (High to Low)'),
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
    ]
    
    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products by name or description...',
            'autocomplete': 'off'
        }),
        label='Search',
        required=False
    )
    
    min_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        label='Min Price (₱)',
        required=False,
        decimal_places=2,
        max_digits=8
    )
    
    max_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '9999.99',
            'step': '0.01',
            'min': '0'
        }),
        label='Max Price (₱)',
        required=False,
        decimal_places=2,
        max_digits=8
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sort By',
        required=False,
        initial='name'
    )


class ProductStockForm(forms.ModelForm):
    """Form for managing product stock and availability."""
    
    class Meta:
        model = Product
        fields = ['stock_quantity', 'is_active']
        widgets = {
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter stock quantity'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'stock_quantity': 'Stock Quantity',
            'is_active': 'Available for Sale'
        }

