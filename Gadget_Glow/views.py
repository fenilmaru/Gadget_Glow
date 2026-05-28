import random
import string
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.utils import timezone
from datetime import timedelta
from users.models import UserProfile
from cart.models import Cart, CartItem
from notifications.models import Notification
from products.models import Product, Category, Brand
from reviews.models import Review
from orders.models import Order, OrderItem
from payments.models import Payment
from discounts.models import Coupon
from users.wishlist_models import Wishlist
from ai_features.models import AIRecommendation
from Gadget_Glow.utils import get_client_ip
from analytics_app.models import AuditLog


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            error = 'Invalid username or password'
    return render(request, 'login.html', {'error': error})


def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        role = request.POST.get('role', 'user')
        if password != confirm_password:
            error = 'Passwords do not match'
        elif User.objects.filter(username=username).exists():
            error = 'Username already exists'
        elif User.objects.filter(email=email).exists():
            error = 'Email already registered'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters'
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name,
            )
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            UserProfile.objects.create(user=user, phone=phone)
            Cart.objects.create(user=user)
            auth_login(request, user)
            return redirect('home') if not user.is_staff else redirect('admin_dashboard')
    return render(request, 'register.html', {'error': error})


@login_required
def user_logout(request):
    auth_logout(request)
    return redirect('login')


def home(request):
    categories = Category.objects.filter(is_active=True)
    featured = Product.objects.filter(is_featured=True, is_active=True, is_deleted=False).select_related('category', 'brand')[:8]
    recent = Product.objects.filter(is_active=True, is_deleted=False).order_by('-created_at')[:8]
    brands = Brand.objects.filter(is_active=True)
    bestselling = Product.objects.filter(is_active=True, is_deleted=False, rating__gt=0).order_by('-rating')[:4]

    # Category-wise products
    category_products = {}
    for cat in categories[:4]:
        prods = Product.objects.filter(category=cat, is_active=True, is_deleted=False)[:4]
        if prods:
            category_products[cat] = prods

    for prod in featured:
        prod.display_image_url = prod.get_display_image()
    for prod in recent:
        prod.display_image_url = prod.get_display_image()
    for prod in bestselling:
        prod.display_image_url = prod.get_display_image()
    for cat_prods in category_products.values():
        for prod in cat_prods:
            prod.display_image_url = prod.get_display_image()

    return render(request, 'home.html', {
        'featured_products': featured,
        'categories': categories,
        'recent_products': recent,
        'brands': brands,
        'bestselling': bestselling,
        'category_products': category_products,
    })


def products_page(request):
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    in_stock = request.GET.get('in_stock', '')
    rating = request.GET.get('rating', '')

    products = Product.objects.filter(is_active=True, is_deleted=False).select_related('category', 'brand').all()

    if search:
        products = products.filter(name__icontains=search) | products.filter(description__icontains=search)
    if category:
        products = products.filter(category_id=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if in_stock:
        products = products.filter(stock__gt=0)
    if rating:
        products = products.filter(rating__gte=rating)
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    for prod in products:
        prod.display_image_url = prod.get_display_image()

    wishlist_products = set()
    if request.user.is_authenticated:
        wishlist_products = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    all_categories = Category.objects.all()

    return render(request, 'products.html', {
        'products': products,
        'categories': all_categories,
        'search_query': search,
        'sort': sort,
        'selected_category': category,
        'wishlist_products': wishlist_products,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category').prefetch_related('images'), slug=slug)
    reviews = product.reviews.select_related('user').order_by('-created_at')
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    if request.user.is_authenticated and request.method == 'POST':
        if 'add_to_cart' in request.POST:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            quantity = int(request.POST.get('quantity', 1))
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'{product.name} added to cart!')
            return redirect('cart_page')
        elif 'add_to_wishlist' in request.POST:
            Wishlist.objects.get_or_create(user=request.user, product=product)
            messages.success(request, f'{product.name} added to wishlist!')
        elif 'remove_wishlist' in request.POST:
            Wishlist.objects.filter(user=request.user, product=product).delete()
            messages.success(request, f'{product.name} removed from wishlist!')
        elif 'add_review' in request.POST:
            rating_val = int(request.POST.get('rating', 5))
            comment = request.POST.get('comment', '')
            Review.objects.create(user=request.user, product=product, rating=rating_val, comment=comment)
            messages.success(request, 'Review submitted!')

    for rel in related_products:
        rel.display_image_url = rel.get_display_image()

    return render(request, 'product_detail.html', {
        'product': product,
        'product_image': product.get_display_image(),
        'reviews': reviews,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    })


@login_required
def cart_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'add':
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            try:
                product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
                return redirect('cart_page')
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'{product.name} added to cart!')
            if request.POST.get('redirect_to') == 'checkout':
                return redirect('checkout_page')
            return redirect('cart_page')
        elif 'update_quantity' in request.POST:
            item_id = request.POST.get('item_id')
            quantity = int(request.POST.get('quantity', 1))
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return redirect('cart_page')
        elif 'remove_item' in request.POST:
            item_id = request.POST.get('item_id')
            CartItem.objects.filter(id=item_id, cart=cart).delete()
            return redirect('cart_page')
        elif 'clear_cart' in request.POST:
            cart.items.all().delete()
            messages.info(request, 'Cart cleared.')
            return redirect('cart_page')

    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items})


@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    if request.method == 'POST':
        if 'move_to_cart' in request.POST:
            wishlist_id = request.POST.get('wishlist_id')
            wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            CartItem.objects.get_or_create(cart=cart, product=wishlist_item.product)
            wishlist_item.delete()
            return redirect('wishlist_page')
        elif 'remove' in request.POST:
            wishlist_id = request.POST.get('wishlist_id')
            Wishlist.objects.filter(id=wishlist_id, user=request.user).delete()
            return redirect('wishlist_page')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def profile_page(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        profile.phone = phone
        profile.address = address
        profile.save()
        if current_password and new_password:
            if request.user.check_password(current_password):
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password updated successfully!')
            else:
                messages.error(request, 'Current password is incorrect!')
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_page')
    return render(request, 'profile.html', {'profile': profile, 'orders': orders})


@login_required
def checkout_page(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_page')
    discount = 0
    coupon_code = ''
    coupon_error = ''
    generated_coupon = None
    if request.method == 'POST':
        if 'apply_coupon' in request.POST:
            coupon_code = request.POST.get('coupon_code', '')
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid:
                    subtotal = cart.total_price
                    if subtotal >= coupon.min_order_amount:
                        if coupon.discount_type == 'percentage':
                            discount = subtotal * (coupon.discount_value / 100)
                            if coupon.max_discount_amount and discount > coupon.max_discount_amount:
                                discount = coupon.max_discount_amount
                        else:
                            discount = coupon.discount_value
                        request.session['coupon_code'] = coupon_code
                        request.session['discount'] = float(discount)
                        messages.success(request, f'Coupon applied! Discount: ₹{discount:.2f}')
                    else:
                        coupon_error = f'Minimum order amount is ₹{coupon.min_order_amount}'
                else:
                    coupon_error = 'Coupon is expired or fully used'
            except Coupon.DoesNotExist:
                coupon_error = 'Invalid coupon code'
        elif 'place_order' in request.POST:
            shipping_address = request.POST.get('shipping_address', '')
            payment_method = request.POST.get('payment_method', 'cod')
            if not shipping_address:
                messages.error(request, 'Please provide shipping address!')
                return redirect('checkout_page')
            subtotal = cart.total_price
            total = subtotal - discount
            order = Order.objects.create(
                user=request.user, total_price=total,
                shipping_address=shipping_address, status='pending'
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order, product=item.product,
                    quantity=item.quantity, price=item.product.price * item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()
            Payment.objects.create(
                order=order, amount=total, method=payment_method,
                status='completed', transaction_id=f"TXN-{Payment.objects.count() + 1:06d}"
            )
            Notification.objects.create(
                user=request.user, title='Order Placed',
                message=f'Your order #{order.id} has been placed successfully!',
                notification_type='order', link=f'/orders/{order.id}/'
            )
            # Generate a random coupon for featured products as a thank-you
            featured_products = Product.objects.filter(is_featured=True, is_active=True, is_deleted=False)[:5]
            if featured_products.exists():
                code = 'WELCOME' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                gen_coupon = Coupon.objects.create(
                    code=code,
                    description=f'Thank-you coupon for order #{order.id} — save on featured items!',
                    discount_type='percentage',
                    discount_value=Decimal('15.00'),
                    min_order_amount=Decimal('0'),
                    max_discount_amount=Decimal('500'),
                    valid_from=timezone.now(),
                    valid_to=timezone.now() + timedelta(days=30),
                    usage_limit=1,
                )
                gen_coupon.applicable_products.add(*featured_products)
                generated_coupon = code
                Notification.objects.create(
                    user=request.user, title='Coupon Reward! 🎉',
                    message=f'You earned a special coupon {code} — 15% off on featured accessories! Valid for 30 days.',
                    notification_type='promo', link='/products/?featured=true'
                )
            cart.items.all().delete()
            if 'coupon_code' in request.session: del request.session['coupon_code']
            if 'discount' in request.session: del request.session['discount']
            messages.success(request, f'Order #{order.id} placed successfully!')
            return render(request, 'checkout.html', {
                'cart': cart, 'cart_items': [], 'subtotal': 0,
                'discount': 0, 'total': 0, 'coupon_code': '', 'coupon_error': '',
                'generated_coupon': generated_coupon, 'order': order,
            })
    subtotal = cart.total_price
    total = subtotal - discount
    request.session['discount'] = float(discount)
    return render(request, 'checkout.html', {
        'cart': cart, 'cart_items': cart_items, 'subtotal': subtotal,
        'discount': discount, 'total': total, 'coupon_code': coupon_code, 'coupon_error': coupon_error,
        'generated_coupon': generated_coupon,
    })


@login_required
def orders_page(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})


@login_required
def notifications_page(request):
    notifications = Notification.objects.filter(user=request.user)
    if request.method == 'POST':
        if 'mark_read' in request.POST:
            notif_id = request.POST.get('notif_id')
            Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
        elif 'mark_all_read' in request.POST:
            notifications.update(is_read=True)
        elif 'delete' in request.POST:
            notif_id = request.POST.get('notif_id')
            Notification.objects.filter(id=notif_id, user=request.user).delete()
        return redirect('notifications_page')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications.html', {'notifications': notifications, 'unread_count': unread_count})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    from analytics_app.services import get_dashboard_stats
    stats = get_dashboard_stats()
    context = {
        'total_products': stats['total_products'],
        'total_orders': stats['total_orders'],
        'total_users': stats['total_users'],
        'total_revenue': stats['total_revenue'],
        'pending_orders': stats['pending_orders'],
        'low_stock_products': stats['low_stock_products'],
        'weekly_revenue': stats['weekly_revenue'],
        'monthly_orders': stats['monthly_orders'],
        'new_users_month': stats['new_users_month'],
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:10],
        'products': Product.objects.select_related('category').order_by('-created_at')[:10],
        'categories': Category.objects.annotate(pcount=models.Count('products')).order_by('name'),
        'all_products': Product.objects.select_related('category').order_by('-created_at'),
    }
    return render(request, 'admin_dashboard.html', context)


# --- Admin Category Management ---
@login_required
def admin_categories(request):
    if not request.user.is_staff:
        return redirect('home')
    categories = Category.objects.annotate(pcount=models.Count('products')).order_by('name')
    return render(request, 'manage_categories.html', {'categories': categories})


@login_required
def admin_category_add(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        if not name:
            messages.error(request, 'Category name is required')
        elif Category.objects.filter(name__iexact=name).exists():
            messages.error(request, 'Category already exists')
        else:
            cat = Category.objects.create(name=name, description=description, is_active=is_active)
            if 'image' in request.FILES:
                cat.image = request.FILES['image']
                cat.save(update_fields=['image'])
            messages.success(request, f'Category "{name}" created!')
            return redirect('admin_categories')
    return render(request, 'category_form.html', {'category': None, 'title': 'Add Category'})


@login_required
def admin_category_edit(request, cat_id):
    if not request.user.is_staff:
        return redirect('home')
    category = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        if not name:
            messages.error(request, 'Category name is required')
        elif Category.objects.filter(name__iexact=name).exclude(id=cat_id).exists():
            messages.error(request, 'Category name already taken')
        else:
            category.name = name
            category.description = description
            category.is_active = is_active
            if 'image' in request.FILES:
                category.image = request.FILES['image']
            category.save()
            messages.success(request, f'Category "{name}" updated!')
            return redirect('admin_categories')
    return render(request, 'category_form.html', {'category': category, 'title': 'Edit Category'})


@login_required
def admin_category_delete(request, cat_id):
    if not request.user.is_staff:
        return redirect('home')
    category = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted!')
    return redirect('admin_categories')


# --- Admin Product Management ---
@login_required
def admin_products(request):
    if not request.user.is_staff:
        return redirect('home')
    search = request.GET.get('search', '')
    cat_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    products = Product.objects.select_related('category', 'brand').order_by('-created_at')
    if status == 'deleted':
        products = products.filter(is_deleted=True)
    else:
        products = products.filter(is_deleted=False)
    if search:
        products = products.filter(name__icontains=search)
    if cat_id:
        products = products.filter(category_id=cat_id)
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    elif status == 'out_of_stock':
        products = products.filter(stock=0)
    elif status == 'low_stock':
        products = products.filter(stock__gt=0, stock__lte=5)
    categories = Category.objects.all()
    return render(request, 'manage_products.html', {
        'products': products, 'categories': categories,
        'search_query': search, 'selected_category': cat_id, 'selected_status': status,
    })


@login_required
def admin_product_add(request):
    if not request.user.is_staff:
        return redirect('home')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        price = request.POST.get('price', '0')
        compare_price = request.POST.get('compare_price', '')
        stock = request.POST.get('stock', '0')
        description = request.POST.get('description', '')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        if not name or not category_id or not price:
            messages.error(request, 'Name, category and price are required')
        else:
            product = Product.objects.create(
                name=name, description=description,
                price=price, compare_price=compare_price or None,
                category_id=category_id, brand_id=brand_id or None,
                stock=stock, is_featured=is_featured, is_active=is_active,
            )
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                product.save(update_fields=['image'])
            messages.success(request, f'Product "{name}" created!')
            return redirect('admin_products')
    return render(request, 'product_form.html', {
        'product': None, 'title': 'Add Product',
        'categories': categories, 'brands': brands,
    })


@login_required
def admin_product_edit(request, prod_id):
    if not request.user.is_staff:
        return redirect('home')
    product = get_object_or_404(Product, id=prod_id)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price', '0')
        product.compare_price = request.POST.get('compare_price') or None
        product.category_id = request.POST.get('category')
        product.brand_id = request.POST.get('brand') or None
        product.stock = request.POST.get('stock', '0')
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_active = request.POST.get('is_active') == 'on'
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        messages.success(request, f'Product "{product.name}" updated!')
        return redirect('admin_products')
    return render(request, 'product_form.html', {
        'product': product, 'title': 'Edit Product',
        'categories': categories, 'brands': brands,
    })


@login_required
def admin_product_delete(request, prod_id):
    if not request.user.is_staff:
        return redirect('home')
    product = get_object_or_404(Product, id=prod_id)
    if request.method == 'POST':
        product.is_deleted = True
        product.is_active = False
        product.save()
        messages.success(request, f'Product "{product.name}" deleted!')
    return redirect('admin_products')


@login_required
def admin_product_toggle_featured(request, prod_id):
    if not request.user.is_staff:
        return redirect('home')
    product = get_object_or_404(Product, id=prod_id)
    product.is_featured = not product.is_featured
    product.save()
    return redirect('admin_products')


@login_required
def admin_product_toggle_active(request, prod_id):
    if not request.user.is_staff:
        return redirect('home')
    product = get_object_or_404(Product, id=prod_id)
    product.is_active = not product.is_active
    product.save()
    return redirect('admin_products')


@login_required
def admin_product_bulk_delete(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        ids = request.POST.getlist('product_ids')
        count = 0
        for pid in ids:
            try:
                product = Product.objects.get(id=pid)
                product.is_deleted = True
                product.is_active = False
                product.save()
                count += 1
            except Product.DoesNotExist:
                pass
        messages.success(request, f'{count} product(s) deleted!')
    return redirect('admin_products')


@login_required
def admin_category_bulk_delete(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        ids = request.POST.getlist('category_ids')
        count = 0
        for cid in ids:
            try:
                Category.objects.get(id=cid).delete()
                count += 1
            except Category.DoesNotExist:
                pass
        messages.success(request, f'{count} categor(ies) deleted!')
    return redirect('admin_categories')


@login_required
def ai_chatbot_page(request):
    return render(request, 'ai_chatbot.html')
