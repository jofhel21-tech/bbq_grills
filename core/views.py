from __future__ import annotations
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import QuerySet, Q
from .models import Product, Reservation, ReservationItem, JournalEntry, Article, Feedback, Order, OrderItem, Cart, CartItem, OrderTracking, UserHistory, Payment, Invoice
from .forms import RegisterForm, ReservationForm, ReservationItemForm, JournalEntryForm, ArticleForm, FeedbackForm, OrderForm, AddOrderItemForm, PaymentForm, CheckoutForm, ProductSearchForm, ProductStockForm
from .forms_invoice import InvoiceForm
from django.utils import timezone
from datetime import timedelta


def log_user_activity(user, action, description='', request=None):
    """Log user activity to UserHistory."""
    if not user.is_authenticated:
        return
    
    ip_address = None
    user_agent = ''
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    UserHistory.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def home(request: HttpRequest) -> HttpResponse:
    """Home page view."""
    recent_orders = Order.objects.all()[:3]
    products = Product.objects.filter(is_active=True)[:6]
    context = {
        'recent_orders': recent_orders,
        'products': products,
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """User dashboard view."""
    user_reservations = Reservation.objects.filter(customer=request.user)[:5]
    context = {
        'reservations': user_reservations,
    }
    return render(request, 'core/dashboard.html', context)


def register(request: HttpRequest) -> HttpResponse:
    """User registration view."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def product_list(request: HttpRequest) -> HttpResponse:
    """Product list view with search and filtering."""
    products = Product.objects.filter(is_active=True)
    form = ProductSearchForm(request.GET or None)
    
    # Handle direct search from navbar (when form might not be valid but search param exists)
    navbar_search = request.GET.get('search', '').strip()
    
    # Apply search filters
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by') or 'name'
        
        # Text search in name and description
        if search_query:
            # First try exact match
            exact_match = products.filter(
                Q(name__iexact=search_query) | 
                Q(description__icontains=search_query)
            )
            
            if exact_match.exists():
                products = exact_match
            else:
                # Try phrase match (contains the full search query)
                phrase_match = products.filter(
                    Q(name__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
                
                if phrase_match.exists():
                    products = phrase_match
                else:
                    # Fall back to word-by-word search but use AND logic for more precision
                    search_words = search_query.strip().split()
                    
                    # Start with all products and filter by each word (AND logic)
                    for word in search_words:
                        products = products.filter(
                            Q(name__icontains=word) | 
                            Q(description__icontains=word)
                        )
            
            # Log search activity
            if request.user.is_authenticated:
                log_user_activity(request.user, 'view_page', f'Searched products: "{search_query}"', request)
        
        # Price range filtering
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        # Sorting
        products = products.order_by(sort_by)
    elif navbar_search:
        # Handle navbar search when form is not valid (only search parameter)
        # First try exact match
        exact_match = products.filter(
            Q(name__iexact=navbar_search) | 
            Q(description__icontains=navbar_search)
        )
        
        if exact_match.exists():
            products = exact_match
        else:
            # Try phrase match (contains the full search query)
            phrase_match = products.filter(
                Q(name__icontains=navbar_search) | 
                Q(description__icontains=navbar_search)
            )
            
            if phrase_match.exists():
                products = phrase_match
            else:
                # Fall back to word-by-word search but use AND logic for more precision
                search_words = navbar_search.split()
                
                # Start with all products and filter by each word (AND logic)
                for word in search_words:
                    products = products.filter(
                        Q(name__icontains=word) | 
                        Q(description__icontains=word)
                    )
        
        products = products.order_by('name')
        
        # Log search activity
        if request.user.is_authenticated:
            log_user_activity(request.user, 'view_page', f'Searched products: "{navbar_search}"', request)
    else:
        # Default sorting
        products = products.order_by('name')
    
    context = {
        'products': products,
        'form': form,
        'total_results': products.count(),
        'search_performed': bool(request.GET),
    }
    return render(request, 'core/product_list.html', context)


def product_search_suggestions(request: HttpRequest) -> JsonResponse:
    """AJAX endpoint for live search suggestions."""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Only search if at least 2 characters
        return JsonResponse({'suggestions': []})
    
    products = Product.objects.filter(is_active=True)
    
    # First try exact match
    exact_match = products.filter(Q(name__iexact=query))
    
    if exact_match.exists():
        matching_products = exact_match[:8]
    else:
        # Try phrase match (contains the full search query)
        phrase_match = products.filter(Q(name__icontains=query))
        
        if phrase_match.exists():
            matching_products = phrase_match[:8]
        else:
            # Fall back to word-by-word search but use AND logic for more precision
            search_words = query.split()
            
            # Start with all products and filter by each word (AND logic)
            for word in search_words:
                products = products.filter(Q(name__icontains=word))
            
            matching_products = products[:8]
    
    # Format suggestions - just product names
    suggestions = []
    for product in matching_products:
        suggestions.append(product.name)
    
    return JsonResponse({'suggestions': suggestions})


@login_required
def reservation_list(request: HttpRequest) -> HttpResponse:
    """List user's reservations."""
    reservations = Reservation.objects.filter(customer=request.user)
    return render(request, 'core/reservation_list.html', {'reservations': reservations})


@login_required
def reservation_create(request: HttpRequest) -> HttpResponse:
    """Create new reservation."""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer = request.user
            reservation.save()
            log_user_activity(request.user, 'create_reservation', f'Created reservation #{reservation.id}', request)
            messages.success(request, 'Reservation created successfully!')
            return redirect('reservation_list')
    else:
        form = ReservationForm()
    return render(request, 'core/reservation_form.html', {'form': form, 'title': 'Create Reservation'})


@login_required
def reservation_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update reservation."""
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'update_reservation', f'Updated reservation #{reservation.id}', request)
            messages.success(request, 'Reservation updated successfully!')
            return redirect('reservation_list')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'core/reservation_form.html', {'form': form, 'title': 'Update Reservation'})


@login_required
def reservation_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete reservation."""
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    if request.method == 'POST':
        reservation.delete()
        log_user_activity(request.user, 'cancel_reservation', f'Cancelled reservation #{reservation.id}', request)
        messages.success(request, 'Reservation cancelled successfully!')
        return redirect('reservation_list')
    return render(request, 'core/reservation_confirm_delete.html', {'reservation': reservation})


@login_required
def journal_list(request: HttpRequest) -> HttpResponse:
    """List user's journal entries."""
    entries = JournalEntry.objects.filter(author=request.user)
    return render(request, 'core/journal_list.html', {'entries': entries})


@login_required
def journal_create(request: HttpRequest) -> HttpResponse:
    """Create new journal entry."""
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            entry.save()
            messages.success(request, 'Journal entry created successfully!')
            return redirect('journal_list')
    else:
        form = JournalEntryForm()
    return render(request, 'core/journal_form.html', {'form': form, 'title': 'Create Journal Entry'})


@login_required
def journal_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update journal entry."""
    entry = get_object_or_404(JournalEntry, pk=pk, author=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Journal entry updated successfully!')
            return redirect('journal_list')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'core/journal_form.html', {'form': form, 'title': 'Update Journal Entry'})


@login_required
def journal_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete journal entry."""
    entry = get_object_or_404(JournalEntry, pk=pk, author=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Journal entry deleted successfully!')
        return redirect('journal_list')
    return render(request, 'core/journal_confirm_delete.html', {'entry': entry})


def article_list(request: HttpRequest) -> HttpResponse:
    """List published articles."""
    articles = Article.objects.filter(published=True)
    return render(request, 'core/article_list.html', {'articles': articles})


@user_passes_test(lambda u: u.is_staff)
def article_create(request: HttpRequest) -> HttpResponse:
    """Create new article (staff only)."""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            if article.published:
                article.publish()
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'core/article_form.html', {'form': form, 'title': 'Create Article'})


@user_passes_test(lambda u: u.is_staff)
def article_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update article (staff only)."""
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if article.published and not article.published_at:
                article.publish()
            article.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'core/article_form.html', {'form': form, 'title': 'Update Article'})


@user_passes_test(lambda u: u.is_staff)
def article_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete article (staff only)."""
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully!')
        return redirect('article_list')
    return render(request, 'core/article_confirm_delete.html', {'article': article})


def feedback_list_create(request: HttpRequest) -> HttpResponse:
    """List feedback and create new feedback."""
    if request.method == 'POST' and request.user.is_authenticated:
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('feedback')
    else:
        form = FeedbackForm() if request.user.is_authenticated else None
    
    feedback_list = Feedback.objects.all()[:20]  # Show latest 20 feedback entries
    context = {
        'feedback_list': feedback_list,
        'form': form,
    }
    return render(request, 'core/feedback.html', context)


def order_list(request: HttpRequest) -> HttpResponse:
    """List orders - all orders for staff, user's orders for customers."""
    if request.user.is_staff:
        orders = Order.objects.all().select_related('customer').prefetch_related('payments')
    elif request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user).prefetch_related('payments')
    else:
        orders = Order.objects.none()
    return render(request, 'core/order_list.html', {'orders': orders})


@user_passes_test(lambda u: u.is_staff)
def admin_reservation_list(request: HttpRequest) -> HttpResponse:
    """List all reservations for admin."""
    reservations = Reservation.objects.all()
    return render(request, 'core/reservation_list.html', {'reservations': reservations})


# Cart Views
def get_or_create_cart(user):
    """Get or create cart for user."""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """Add product to cart."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    log_user_activity(request.user, 'add_to_cart', f'Added {product.name} to cart (Qty: {cart_item.quantity})', request)
    messages.success(request, f'{product.name} added to cart!')
    return redirect('product_list')


@login_required
def cart_view(request: HttpRequest) -> HttpResponse:
    """View shopping cart."""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'core/cart.html', context)


@login_required
def update_cart_item(request: HttpRequest, item_id: int) -> HttpResponse:
    """Update cart item quantity."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    
    return redirect('cart_view')


@login_required
def remove_from_cart(request: HttpRequest, item_id: int) -> HttpResponse:
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    log_user_activity(request.user, 'remove_from_cart', f'Removed {product_name} from cart', request)
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('cart_view')


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """Checkout process with payment method selection."""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_view')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order with selected payment method and delivery info
            order = Order.objects.create(
                customer=request.user,
                total_amount=cart.total_price,
                notes=form.cleaned_data.get('order_notes', f'Order created from cart with {cart.total_items} items'),
                delivery_address=form.cleaned_data['delivery_address'],
                delivery_barangay=form.cleaned_data['delivery_barangay'],
                delivery_latitude=form.cleaned_data.get('delivery_latitude'),
                delivery_longitude=form.cleaned_data.get('delivery_longitude')
            )
            
            # Create order items from cart items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                customer=request.user,
                amount=order.total_amount,
                payment_method=form.cleaned_data['payment_method'],
                status='pending'
            )
            
            # Log activities
            log_user_activity(request.user, 'create_order', f'Created Order #{order.id} with {cart.total_items} items - Total: ₱{order.total_amount}', request)
            log_user_activity(request.user, 'payment_initiated', f'Payment #{payment.id} initiated for Order #{order.id} - ₱{payment.amount} via {payment.get_payment_method_display()}', request)
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Order #{order.id} placed successfully! Payment method: {payment.get_payment_method_display()}')
            return redirect('order_list')
    else:
        form = CheckoutForm()
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'total_amount': cart.total_price,
        'total_items': cart.total_items,
    }
    return render(request, 'core/checkout.html', context)


@login_required
def order_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update order - customers can only edit their own orders (no status changes)."""
    # Check if order exists first
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        messages.error(request, f'Order #{pk} does not exist.')
        return redirect('order_list')
    
    # Check if user owns this order or is staff
    if order.customer != request.user and not request.user.is_staff:
        messages.error(request, f'You do not have permission to edit Order #{pk}.')
        return redirect('order_list')
    
    # Check if customer can edit this order
    if not request.user.is_staff and not order.can_be_edited():
        messages.error(request, f'Order #{pk} cannot be edited. Orders that are out for delivery or completed with successful payment cannot be modified.')
        return redirect('order_list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'update_order', f'Updated Order #{order.id}', request)
            messages.success(request, f'Order #{order.id} updated successfully!')
            return redirect('order_list')
    else:
        form = OrderForm(instance=order, user=request.user)
    
    context = {
        'form': form, 
        'order': order, 
        'title': 'Edit Order',
        'is_admin': request.user.is_staff,
        'can_edit': order.can_be_edited()
    }
    return render(request, 'core/order_form.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_order_list(request: HttpRequest) -> HttpResponse:
    """Admin view to list all orders with management capabilities."""
    orders = Order.objects.all().select_related('customer').prefetch_related('items__product')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search by customer name or order ID
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(customer__username__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(id__icontains=search)
        )
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search,
    }
    return render(request, 'core/admin_order_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_order_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Admin update order with full access including status changes."""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            old_status = order.status
            form.save()
            
            # Update tracking status if order status changed
            if old_status != order.status:
                tracking, created = OrderTracking.objects.get_or_create(order=order)
                if order.status == 'processing':
                    tracking.status = 'confirmed'
                elif order.status == 'completed':
                    tracking.status = 'delivered'
                elif order.status == 'cancelled':
                    tracking.status = 'cancelled'
                tracking.save()
            
            log_user_activity(request.user, 'update_order', f'Admin updated Order #{order.id} - Status: {order.status}', request)
            messages.success(request, f'Order #{order.id} updated successfully!')
            return redirect('admin_order_list')
    else:
        form = OrderForm(instance=order, user=request.user)
    
    context = {
        'form': form, 
        'order': order, 
        'title': f'Admin Edit Order #{order.id}',
        'is_admin': True
    }
    return render(request, 'core/order_form.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_order_tracking_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Admin update order tracking information."""
    order = get_object_or_404(Order, pk=pk)
    tracking, created = OrderTracking.objects.get_or_create(order=order)
    
    if request.method == 'POST':
        # Update tracking status
        new_status = request.POST.get('tracking_status')
        if new_status and new_status in dict(OrderTracking.TRACKING_STATUS_CHOICES):
            tracking.status = new_status
        
        # Update location if provided
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location_name = request.POST.get('location_name')
        
        if latitude and longitude:
            tracking.latitude = float(latitude)
            tracking.longitude = float(longitude)
            tracking.location_name = location_name or ''
        
        # Update estimated delivery
        estimated_delivery = request.POST.get('estimated_delivery')
        if estimated_delivery:
            from django.utils.dateparse import parse_datetime
            tracking.estimated_delivery = parse_datetime(estimated_delivery)
        
        tracking.save()
        
        log_user_activity(request.user, 'update_order', f'Admin updated tracking for Order #{order.id} - Status: {tracking.status}', request)
        messages.success(request, f'Tracking updated for Order #{order.id}!')
        return redirect('admin_order_list')
    
    context = {
        'order': order,
        'tracking': tracking,
        'tracking_status_choices': OrderTracking.TRACKING_STATUS_CHOICES,
        'title': f'Update Tracking - Order #{order.id}'
    }
    return render(request, 'core/admin_order_tracking.html', context)


@login_required
def order_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete order - staff can delete all orders, customers can delete their own orders."""
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    # Check if customer can delete this order
    if not request.user.is_staff and not order.can_be_deleted():
        messages.error(request, f'Order #{pk} cannot be deleted. Orders that are out for delivery or completed with successful payment cannot be cancelled.')
        return redirect('order_list')
    
    if request.method == 'POST':
        order_id = order.id
        log_user_activity(request.user, 'cancel_order', f'Cancelled Order #{order_id}', request)
        order.delete()
        messages.success(request, f'Order #{order_id} deleted successfully!')
        return redirect('order_list')
    return render(request, 'core/order_confirm_delete.html', {'order': order, 'can_delete': order.can_be_deleted()})


@login_required
def add_order_item(request: HttpRequest, pk: int) -> HttpResponse:
    """Add item to existing order."""
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    if request.method == 'POST':
        form = AddOrderItemForm(request.POST)
        if form.is_valid():
            order_item = form.save(commit=False)
            order_item.order = order
            order_item.price = order_item.product.price
            order_item.save()
            
            # Update order total
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            
            messages.success(request, f'{order_item.product.name} added to order #{order.id}!')
            return redirect('order_update', pk=order.pk)
    else:
        form = AddOrderItemForm()
    
    context = {
        'form': form,
        'order': order,
        'title': f'Add Item to Order #{order.id}'
    }
    return render(request, 'core/add_order_item.html', context)


@login_required
def remove_order_item(request: HttpRequest, pk: int, item_id: int) -> HttpResponse:
    """Remove item from order."""
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    order_item = get_object_or_404(OrderItem, id=item_id, order=order)
    product_name = order_item.product.name
    order_item.delete()
    
    # Update order total
    order.total_amount = sum(item.total_price for item in order.items.all())
    order.save()
    
    messages.success(request, f'{product_name} removed from order #{order.id}!')
    return redirect('order_update', pk=order.pk)


@login_required
def order_tracking(request: HttpRequest, pk: int) -> HttpResponse:
    """View order tracking details."""
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    # Get or create tracking record
    tracking, created = OrderTracking.objects.get_or_create(order=order)
    
    # Prefetch payment information
    order = Order.objects.select_related('customer').prefetch_related('payments', 'items__product').get(pk=pk)
    
    context = {
        'order': order,
        'tracking': tracking,
        'has_location': tracking.latitude and tracking.longitude,
    }
    return render(request, 'core/order_tracking.html', context)


def tracking_guide(request: HttpRequest) -> HttpResponse:
    """View tracking guide for staff."""
    return render(request, 'core/tracking_guide.html')


@login_required
def user_history(request: HttpRequest) -> HttpResponse:
    """View user's activity history."""
    history = UserHistory.objects.filter(user=request.user).order_by('-timestamp')[:100]
    context = {
        'history': history,
    }
    return render(request, 'core/user_history.html', context)


@login_required
def delete_user_history(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a specific user history entry."""
    history_entry = get_object_or_404(UserHistory, pk=pk, user=request.user)
    
    if request.method == 'POST':
        action_description = history_entry.get_action_display()
        history_entry.delete()
        messages.success(request, f'Activity "{action_description}" deleted successfully!')
        return redirect('user_history')
    
    context = {
        'history_entry': history_entry,
    }
    return render(request, 'core/delete_user_history.html', context)


@login_required
def clear_user_history(request: HttpRequest) -> HttpResponse:
    """Clear all user history entries."""
    if request.method == 'POST':
        count = UserHistory.objects.filter(user=request.user).count()
        UserHistory.objects.filter(user=request.user).delete()
        messages.success(request, f'Successfully cleared {count} activity entries from your history!')
        return redirect('user_history')
    
    history_count = UserHistory.objects.filter(user=request.user).count()
    context = {
        'history_count': history_count,
    }
    return render(request, 'core/clear_user_history.html', context)


def map_view(request: HttpRequest) -> HttpResponse:
    """Display map of Naval, Biliran, Philippines."""
    return render(request, 'core/map.html')


# Payment Management Views
@user_passes_test(lambda u: u.is_staff)
def admin_payment_list(request: HttpRequest) -> HttpResponse:
    """Admin view to list all payment transactions."""
    payments = Payment.objects.all().select_related('order', 'customer', 'processed_by')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Filter by payment method
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Search by customer name, order ID, or transaction ID
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(customer__username__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(order__id__icontains=search) |
            Q(transaction_id__icontains=search) |
            Q(reference_number__icontains=search)
        )
    
    context = {
        'payments': payments,
        'status_choices': Payment.PAYMENT_STATUS_CHOICES,
        'method_choices': Payment.PAYMENT_METHOD_CHOICES,
        'current_status': status_filter,
        'current_method': method_filter,
        'search_query': search,
    }
    return render(request, 'core/admin_payment_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_payment_create(request: HttpRequest, order_id: int) -> HttpResponse:
    """Admin create payment for an order."""
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.customer = order.customer
            payment.processed_by = request.user
            payment.save()
            
            # Log payment activity
            log_user_activity(
                order.customer, 
                'payment_initiated', 
                f'Payment #{payment.id} created for Order #{order.id} - ₱{payment.amount} via {payment.get_payment_method_display()}',
                request
            )
            
            messages.success(request, f'Payment #{payment.id} created successfully!')
            return redirect('admin_payment_list')
    else:
        # Pre-fill amount with order total
        form = PaymentForm(initial={'amount': order.total_amount})
    
    context = {
        'form': form,
        'order': order,
        'title': f'Create Payment for Order #{order.id}'
    }
    return render(request, 'core/payment_form.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_payment_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Admin update payment transaction."""
    payment = get_object_or_404(Payment, pk=pk)
    old_status = payment.status
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.processed_by = request.user
            payment.save()
            
            # Log payment status change
            if old_status != payment.status:
                action_map = {
                    'completed': 'payment_completed',
                    'failed': 'payment_failed',
                    'refunded': 'payment_refunded',
                    'cancelled': 'payment_cancelled'
                }
                action = action_map.get(payment.status, 'payment_updated')
                
                log_user_activity(
                    payment.customer,
                    action,
                    f'Payment #{payment.id} status changed from {old_status} to {payment.status} - ₱{payment.amount}',
                    request
                )
            
            messages.success(request, f'Payment #{payment.id} updated successfully!')
            return redirect('admin_payment_list')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'title': f'Update Payment #{payment.id}'
    }
    return render(request, 'core/payment_form.html', context)


@login_required
def user_profile(request: HttpRequest) -> HttpResponse:
    """User profile view showing account information."""
    user = request.user
    orders_count = Order.objects.filter(customer=user).count()
    reservations_count = Reservation.objects.filter(customer=user).count()
    total_spent = sum(order.total_amount for order in Order.objects.filter(customer=user))
    
    context = {
        'user': user,
        'orders_count': orders_count,
        'reservations_count': reservations_count,
        'total_spent': total_spent,
    }
    return render(request, 'core/user_profile.html', context)


@login_required
def create_additional_account(request: HttpRequest) -> HttpResponse:
    """Create an additional account while logged in."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            log_user_activity(request.user, 'create_account', f'Created additional account: {new_user.username}', request)
            messages.success(request, f'Additional account "{new_user.username}" created successfully! You can now login with this account.')
            return redirect('user_profile')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
        'title': 'Create Additional Account',
        'is_additional': True
    }
    return render(request, 'core/create_additional_account.html', context)




@user_passes_test(lambda u: u.is_staff)
def admin_invoice_list(request: HttpRequest) -> HttpResponse:
    """Admin view to list all invoices."""
    invoices = Invoice.objects.all().select_related('customer', 'order')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Search by invoice number or customer
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(customer__username__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )
    
    context = {
        'invoices': invoices,
        'status_choices': Invoice.INVOICE_STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search,
    }
    return render(request, 'core/admin_invoice_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_generate_invoice(request: HttpRequest, order_id: int) -> HttpResponse:
    """Admin view to generate invoice for an order."""
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if invoice already exists
    if hasattr(order, 'invoice'):
        messages.info(request, 'Invoice already exists for this order.')
        return redirect('admin_invoice_detail', pk=order.invoice.pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # Generate unique invoice number
            invoice_count = Invoice.objects.count() + 1
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{invoice_count:04d}"
            
            # Calculate amounts
            subtotal = sum(item.total_price for item in order.items.all())
            tax_amount = form.cleaned_data.get('tax_amount', 0)
            discount_amount = form.cleaned_data.get('discount_amount', 0)
            total_amount = subtotal + tax_amount - discount_amount
            
            # Create invoice
            invoice = form.save(commit=False)
            invoice.order = order
            invoice.customer = order.customer
            invoice.invoice_number = invoice_number
            invoice.subtotal = subtotal
            invoice.total_amount = total_amount
            invoice.customer_name = f"{order.customer.first_name} {order.customer.last_name}".strip() or order.customer.username
            invoice.customer_email = order.customer.email
            invoice.customer_address = order.delivery_address
            invoice.status = 'issued'
            invoice.save()
            
            log_user_activity(request.user, 'generate_invoice', f'Generated Invoice {invoice_number} for Order #{order.id} (Customer: {order.customer.username})', request)
            messages.success(request, f'Invoice {invoice_number} generated successfully!')
            return redirect('admin_invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    
    context = {
        'form': form,
        'order': order,
        'title': f'Generate Invoice for Order #{order.id}'
    }
    return render(request, 'core/admin_generate_invoice.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_invoice_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Admin view to see invoice details."""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'update_invoice', f'Updated Invoice {invoice.invoice_number}', request)
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
            return redirect('admin_invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
        'order': invoice.order,
        'title': f'Invoice {invoice.invoice_number}'
    }
    return render(request, 'core/admin_invoice_detail.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_stock_management(request: HttpRequest) -> HttpResponse:
    """Admin view for managing product stock and availability."""
    products = Product.objects.all().order_by('name')
    
    # Filter by stock status if requested
    stock_filter = request.GET.get('stock_filter', 'all')
    if stock_filter == 'out_of_stock':
        products = products.filter(stock_quantity=0)
    elif stock_filter == 'low_stock':
        products = products.filter(stock_quantity__lte=5, stock_quantity__gt=0)
    elif stock_filter == 'in_stock':
        products = products.filter(stock_quantity__gt=5)
    elif stock_filter == 'inactive':
        products = products.filter(is_active=False)
    
    context = {
        'products': products,
        'stock_filter': stock_filter,
        'total_products': Product.objects.count(),
        'out_of_stock_count': Product.objects.filter(stock_quantity=0).count(),
        'low_stock_count': Product.objects.filter(stock_quantity__lte=5, stock_quantity__gt=0).count(),
        'inactive_count': Product.objects.filter(is_active=False).count(),
    }
    return render(request, 'core/admin_stock_management.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_update_stock(request: HttpRequest, product_id: int) -> HttpResponse:
    """Admin view for updating individual product stock."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductStockForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Stock updated for {product.name}')
            
            # Log the stock update
            if request.user.is_authenticated:
                log_user_activity(
                    request.user, 
                    'admin_action', 
                    f'Updated stock for {product.name}: {product.stock_quantity} units, Active: {product.is_active}',
                    request
                )
            
            return redirect('admin_stock_management')
    else:
        form = ProductStockForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Update Stock - {product.name}'
    }
    return render(request, 'core/admin_update_stock.html', context)
