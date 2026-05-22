from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from users.models import UserProfile
from cart.models import Cart, CartItem
from notifications.models import Notification
from products.models import Category, Brand, Product
from reviews.models import Review
from orders.models import Order, OrderItem
from payments.models import Payment
from ai_features.models import AIRecommendation
from discounts.models import Coupon
from users.wishlist_models import Wishlist
import random
from django.db.models import Avg


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # === CATEGORIES ===
        categories_data = [
            {'name': 'Mobile Cases', 'description': 'Premium protective cases for all smartphone models — transparent, silicone, armor, leather, and rugged cases'},
            {'name': 'Chargers', 'description': 'Fast chargers, wireless charging pads, GaN adapters, car chargers and multi-port charging stations'},
            {'name': 'Cables', 'description': 'Type-C cables, Lightning cables, braided nylon cords, multi-charging cables and data sync cables'},
            {'name': 'Power Banks', 'description': 'Portable power banks from 5000mAh to 20000mAh with fast charging, wireless and solar options'},
            {'name': 'Smart Watches', 'description': 'Fitness smart watches, AMOLED displays, Bluetooth calling, sports bands and premium wearables'},
            {'name': 'Phone Holders', 'description': 'Car mobile holders, desk stands, magnetic mounts, bike holders, and adjustable phone stands'},
        ]

        categories = []
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
            categories.append(cat)

        # === BRANDS ===
        brands_data = [
            {'name': 'Apple', 'description': 'Premium technology company'},
            {'name': 'Samsung', 'description': 'Leading electronics manufacturer'},
            {'name': 'OnePlus', 'description': 'Premium smartphone brand'},
            {'name': 'Xiaomi', 'description': 'Innovative technology brand'},
            {'name': 'Realme', 'description': 'Youth-focused tech brand'},
            {'name': 'boAt', 'description': 'Indian audio and wearables brand'},
            {'name': 'JBL', 'description': 'Professional audio equipment'},
            {'name': 'Sony', 'description': 'Global electronics corporation'},
            {'name': 'Noise', 'description': 'Smart wearables brand'},
            {'name': 'Anker', 'description': 'Charging technology leader'},
        ]

        brands = []
        for brand_data in brands_data:
            b, _ = Brand.objects.get_or_create(name=brand_data['name'], defaults=brand_data)
            brands.append(b)

        cat = {c.name: c for c in categories}
        b = {br.name: br for br in brands}

        # === PRODUCTS ===
        products_data = [

            # --- MOBILE CASES (8) ---
            {'name': 'Transparent Shockproof Case', 'description': 'Ultra-clear transparent case with shock-absorbing corners. Anti-yellowing technology keeps it crystal clear for months. Precise cutouts for all ports and buttons.', 'price': 14.99, 'compare_price': 19.99, 'stock': 300, 'rating': 4.5, 'is_featured': True, 'category': cat['Mobile Cases'], 'brand': b['Samsung']},
            {'name': 'Silicone Back Cover', 'description': 'Premium liquid silicone back cover with micro-dot pattern to prevent stickiness. Soft-touch finish with raised camera and screen protection.', 'price': 12.99, 'stock': 400, 'rating': 4.4, 'category': cat['Mobile Cases'], 'brand': b['Apple']},
            {'name': 'Armor Military Grade Case', 'description': 'Military-grade drop protection with reinforced TPU bumper and polycarbonate back. Tested for 10-foot drops with air cushion technology.', 'price': 24.99, 'compare_price': 34.99, 'stock': 200, 'rating': 4.7, 'is_featured': True, 'category': cat['Mobile Cases'], 'brand': b['Samsung']},
            {'name': 'Leather Wallet Case', 'description': 'Genuine leather flip case with RFID blocking card slots. Holds up to 3 cards with magnetic closure. Slim profile with full edge protection.', 'price': 29.99, 'compare_price': 39.99, 'stock': 120, 'rating': 4.5, 'category': cat['Mobile Cases'], 'brand': b['Apple']},
            {'name': 'Liquid Silicone Case', 'description': 'Apple-style liquid silicone case with microfiber interior lining. Smooth silky finish with precise button covers. Wireless charging compatible.', 'price': 19.99, 'stock': 250, 'rating': 4.6, 'is_featured': True, 'category': cat['Mobile Cases'], 'brand': b['Apple']},
            {'name': 'Camera Lens Protective Case', 'description': 'Case with raised camera bezel and individual lens protection. Slim profile with textured anti-slip side grips for secure handling.', 'price': 17.99, 'stock': 180, 'rating': 4.3, 'category': cat['Mobile Cases'], 'brand': b['OnePlus']},
            {'name': 'Magnetic Phone Case', 'description': 'Built-in magnetic ring for MagSafe accessories and car mounts. 360° rotation ring holder with kickstand function. Slim and lightweight design.', 'price': 22.99, 'stock': 220, 'rating': 4.4, 'category': cat['Mobile Cases'], 'brand': b['Realme']},
            {'name': 'Carbon Fiber Ultra Thin Case', 'description': 'Premium carbon fiber weave case at just 0.8mm thickness. Kevlar-grade aramid fiber provides extreme protection without bulk. Racing-inspired design.', 'price': 39.99, 'stock': 60, 'rating': 4.8, 'category': cat['Mobile Cases'], 'brand': b['OnePlus']},

            # --- CHARGERS (8) ---
            {'name': 'Fast Charger 25W', 'description': 'Compact 25W USB-C PD fast charger with GaN technology. Charges compatible devices from 0 to 50% in just 30 minutes. Intelligent chip for optimized charging.', 'price': 18.99, 'compare_price': 24.99, 'stock': 250, 'rating': 4.6, 'is_featured': True, 'category': cat['Chargers'], 'brand': b['Anker']},
            {'name': 'USB-C Power Adapter 20W', 'description': 'Compact 20W USB-C power adapter with foldable prongs. Universal compatibility with all USB-C devices. Built-in surge protection for safe charging.', 'price': 14.99, 'stock': 350, 'rating': 4.4, 'category': cat['Chargers'], 'brand': b['Anker']},
            {'name': 'Wireless Charging Pad', 'description': '15W fast wireless charging pad with intelligent LED indicator. Anti-slip silicone ring keeps phone in place. Compatible with all Qi-enabled devices including AirPods.', 'price': 29.99, 'compare_price': 39.99, 'stock': 180, 'rating': 4.7, 'is_featured': True, 'category': cat['Chargers'], 'brand': b['Anker']},
            {'name': 'GaN 65W Fast Charger', 'description': 'Next-generation GaN technology 65W 3-port charger. Ultra-compact size charges laptop, tablet and phone simultaneously. Universal PD and QC compatibility.', 'price': 49.99, 'compare_price': 69.99, 'stock': 80, 'rating': 4.9, 'is_featured': True, 'category': cat['Chargers'], 'brand': b['Anker']},
            {'name': 'Car Mobile Charger Adapter', 'description': 'Dual USB car charger with 30W PD fast charging. Compact design fits all standard 12V/24V cigarette lighter outlets. LED ring indicator for night visibility.', 'price': 12.99, 'stock': 400, 'rating': 4.4, 'category': cat['Chargers'], 'brand': b['Xiaomi']},
            {'name': 'Dual Port Wall Charger', 'description': 'Dual USB-A port wall charger with intelligent power分配. Simultaneously charge two devices at maximum supported speed. Compact travel-friendly design.', 'price': 16.99, 'compare_price': 21.99, 'stock': 280, 'rating': 4.5, 'is_featured': True, 'category': cat['Chargers'], 'brand': b['Xiaomi']},
            {'name': 'Magnetic Wireless Charger', 'description': 'Magnetic wireless charger with 15W fast charging. Strong N52 magnets snap perfectly to MagSafe phones. Compact design with braided 1.5m cable.', 'price': 34.99, 'stock': 140, 'rating': 4.8, 'category': cat['Chargers'], 'brand': b['Anker']},
            {'name': '3-in-1 Charging Station', 'description': 'Foldable 3-in-1 wireless charging station for phone, smartwatch and wireless earbuds. Premium desktop design with fast charging for all three devices simultaneously.', 'price': 39.99, 'stock': 70, 'rating': 4.6, 'category': cat['Chargers'], 'brand': b['Samsung']},
            {'name': 'USB Charging Hub', 'description': '6-port USB charging hub with smart IC detection. Charges all your devices at optimal speed. Compact desktop design with LED status indicators.', 'price': 24.99, 'stock': 120, 'rating': 4.5, 'category': cat['Chargers'], 'brand': b['Anker']},
            {'name': 'Travel Charger Adapter', 'description': 'Universal travel adapter with 4 USB ports including 2 USB-C PD. Works in 200+ countries with smart voltage detection. All-in-one international charging solution.', 'price': 34.99, 'compare_price': 44.99, 'stock': 80, 'rating': 4.6, 'category': cat['Chargers'], 'brand': b['Anker']},

            # --- CABLES (9) ---
            {'name': 'Type-C Fast Charging Cable', 'description': 'High-speed USB-C to USB-C cable with 60W PD fast charging support. Durable braided nylon construction with aluminum alloy connectors. 2-meter length.', 'price': 12.99, 'stock': 500, 'rating': 4.6, 'is_featured': True, 'category': cat['Cables'], 'brand': b['Anker']},
            {'name': 'Lightning Cable 2M', 'description': 'MFi certified Lightning to USB-A cable. Apple certified chip ensures full compatibility with all iOS devices. Reinforced stress points prevent fraying at connections.', 'price': 19.99, 'stock': 350, 'rating': 4.5, 'is_featured': True, 'category': cat['Cables'], 'brand': b['Apple']},
            {'name': 'Braided USB-C Cable 100W', 'description': 'Premium braided USB-C to USB-C cable supporting 100W PD charging. 480Mbps data transfer speed. Tangle-free outdoor-grade braided design with 2 meter length.', 'price': 15.99, 'compare_price': 19.99, 'stock': 400, 'rating': 4.7, 'category': cat['Cables'], 'brand': b['Anker']},
            {'name': '3-in-1 Multi Charging Cable', 'description': '3-in-1 cable with Lightning, USB-C and Micro USB connectors. Braided nylon design with tangle-free storage pouch. Supports fast charging on all three ports simultaneously.', 'price': 14.99, 'compare_price': 19.99, 'stock': 300, 'rating': 4.4, 'is_featured': True, 'category': cat['Cables'], 'brand': b['Realme']},
            {'name': 'Magnetic USB Charging Cable', 'description': 'Magnetic detachable USB cable with interchangeable tips. One cable works with all devices. LED indicator shows charging status. 1.5 meter braided length.', 'price': 16.99, 'stock': 250, 'rating': 4.3, 'category': cat['Cables'], 'brand': b['Xiaomi']},
            {'name': 'Nylon Braided Data Cable', 'description': 'Heavy-duty nylon braided cable rated for 10000+ bends. Supports fast charging and data sync. Reinforced zinc alloy connectors with laser-welded strain relief.', 'price': 11.99, 'stock': 600, 'rating': 4.4, 'category': cat['Cables'], 'brand': b['Anker']},
            {'name': 'RGB LED Glow Cable', 'description': 'Glow-in-the-dark LED charging cable with ambient light effects. Braided fabric exterior for durability. Supports fast charging with data transfer capability.', 'price': 13.99, 'stock': 200, 'rating': 4.2, 'category': cat['Cables'], 'brand': b['boAt']},
            {'name': 'Retractable USB Cable', 'description': 'Compact retractable USB cable that self-coils for tangle-free storage. Supports fast charging and data sync. Perfect for travel and on-the-go use.', 'price': 10.99, 'stock': 350, 'rating': 4.3, 'category': cat['Cables'], 'brand': b['Xiaomi']},

            # --- POWER BANKS (10) ---
            {'name': '10000mAh Power Bank', 'description': 'Ultra-slim 10000mAh power bank with 20W PD fast charging. Just 9mm thin — easily fits in any pocket. Dual input/output ports charge two devices simultaneously.', 'price': 29.99, 'compare_price': 39.99, 'stock': 220, 'rating': 4.6, 'is_featured': True, 'category': cat['Power Banks'], 'brand': b['Anker']},
            {'name': '20000mAh Fast Charging Power Bank', 'description': 'High-capacity 20000mAh power bank with dual USB and Type-C ports. 30W PD fast charging powers laptops and tablets. LED digital display shows remaining battery.', 'price': 45.99, 'compare_price': 59.99, 'stock': 100, 'rating': 4.7, 'is_featured': True, 'category': cat['Power Banks'], 'brand': b['Anker']},
            {'name': 'Magnetic Wireless Power Bank', 'description': '10000mAh magnetic wireless power bank that snaps to MagSafe phones. 15W wireless fast charging with pass-through charging support. Compact passport-sized design.', 'price': 39.99, 'stock': 90, 'rating': 4.6, 'category': cat['Power Banks'], 'brand': b['Anker']},
            {'name': 'Pocket Mini Power Bank', 'description': 'Credit card sized 5000mAh mini power bank. Built-in folding AC plug — no cable needed. Perfect emergency charger for pocket or purse. FAA approved for flights.', 'price': 19.99, 'stock': 300, 'rating': 4.3, 'category': cat['Power Banks'], 'brand': b['Xiaomi']},
            {'name': 'Slim 10000mAh Power Bank', 'description': 'Ultra-slim aluminum power bank at just 8mm thickness. 10000mAh capacity with 18W QC fast charging. Premium metallic finish with LED battery indicator.', 'price': 32.99, 'compare_price': 42.99, 'stock': 150, 'rating': 4.5, 'category': cat['Power Banks'], 'brand': b['OnePlus']},
            {'name': 'RGB Gaming Power Bank', 'description': '20000mAh gaming power bank with customizable RGB lighting effects. Dual 20W fast charging outputs with game mode. LED matrix display for battery percentage.', 'price': 49.99, 'stock': 60, 'rating': 4.7, 'category': cat['Power Banks'], 'brand': b['boAt']},
            {'name': 'LED Display Power Bank', 'description': 'Smart 20000mAh power bank with LED percentage display. Dual input micro USB and Type-C. 3 output ports charge phone and watch simultaneously.', 'price': 35.99, 'stock': 180, 'rating': 4.4, 'category': cat['Power Banks'], 'brand': b['Realme']},
            {'name': 'Solar Power Bank', 'description': '10000mAh solar power bank for outdoor adventures. Dual solar panels for emergency charging. IPX5 water resistant with built-in LED flashlight.', 'price': 42.99, 'stock': 60, 'rating': 4.3, 'category': cat['Power Banks'], 'brand': b['boAt']},
            {'name': 'Ultra Slim 5000mAh Power Bank', 'description': 'Credit card sized 5000mAh power bank at just 6mm thickness. Built-in USB-C cable for charging. Perfect pocket companion for daily use.', 'price': 22.99, 'stock': 250, 'rating': 4.4, 'category': cat['Power Banks'], 'brand': b['Xiaomi']},

            # --- SMART WATCHES (10) ---
            {'name': 'Fitness Smart Watch', 'description': 'Advanced fitness smart watch with 1.43 inch AMOLED display. 24/7 heart rate, SpO2 and sleep monitoring. 100+ sports modes with built-in GPS tracking.', 'price': 89.99, 'compare_price': 129.99, 'stock': 120, 'rating': 4.7, 'is_featured': True, 'category': cat['Smart Watches'], 'brand': b['Noise']},
            {'name': 'Bluetooth Calling Smart Watch', 'description': 'Smart watch with built-in speaker and mic for Bluetooth calls. 1.85 inch HD display with 500 nits brightness. 7-day battery life with always-on display mode.', 'price': 59.99, 'compare_price': 79.99, 'stock': 150, 'rating': 4.6, 'is_featured': True, 'category': cat['Smart Watches'], 'brand': b['boAt']},
            {'name': 'Sports Fitness Band', 'description': 'Lightweight fitness band with 1.47 inch AMOLED display. 24/7 activity tracking with heart rate and blood oxygen monitoring. 14-day battery for worry-free wear.', 'price': 49.99, 'stock': 200, 'rating': 4.5, 'category': cat['Smart Watches'], 'brand': b['Noise']},
            {'name': 'Premium Metal Smartwatch', 'description': 'Premium stainless steel smartwatch with sapphire glass display. Luxury design meets advanced fitness tracking. 5 ATM water resistance with built-in altimeter.', 'price': 129.99, 'compare_price': 179.99, 'stock': 45, 'rating': 4.8, 'category': cat['Smart Watches'], 'brand': b['OnePlus']},
            {'name': 'Round Dial Smart Watch', 'description': 'Classic round dial smartwatch with vibrant AMOLED display. Traditional analog look with smart notifications and health tracking. Interchangeable strap system.', 'price': 74.99, 'stock': 110, 'rating': 4.5, 'category': cat['Smart Watches'], 'brand': b['Noise']},
            {'name': 'GPS Sports Smartwatch', 'description': 'Rugged sports smartwatch with dual-band GPS tracking. 50m water resistance with military-grade durability. Barometer, compass and altimeter for outdoor adventures.', 'price': 79.99, 'stock': 90, 'rating': 4.5, 'category': cat['Smart Watches'], 'brand': b['Samsung']},
            {'name': 'Ultra Smart Watch', 'description': 'Ultimate adventure smartwatch with titanium case and 100m water resistance. 36-hour battery in GPS mode. Advanced health sensors including ECG and skin temperature.', 'price': 199.99, 'stock': 30, 'rating': 4.9, 'is_featured': True, 'category': cat['Smart Watches'], 'brand': b['Samsung']},
            {'name': 'Kids Smart Watch', 'description': 'Fun smart watch for kids with GPS tracking and SOS calling. 1.4 inch touch display with kid-friendly interface. Water resistant with 3-day battery life.', 'price': 44.99, 'stock': 80, 'rating': 4.3, 'category': cat['Smart Watches'], 'brand': b['Noise']},
            {'name': 'Business Smart Watch', 'description': 'Elegant business smart watch with stainless steel casing. Classic analog style with smart notifications. 14-day battery with always-on display mode.', 'price': 99.99, 'compare_price': 139.99, 'stock': 60, 'rating': 4.6, 'category': cat['Smart Watches'], 'brand': b['Noise']},

            # --- PHONE HOLDERS (7) ---
            {'name': 'Car Mobile Holder', 'description': 'Universal car dashboard phone holder with one-touch clamp mechanism. 360° ball joint for portrait and landscape viewing. Strong suction mount stays secure on all surfaces.', 'price': 19.99, 'compare_price': 24.99, 'stock': 250, 'rating': 4.5, 'is_featured': True, 'category': cat['Phone Holders'], 'brand': b['Anker']},
            {'name': 'Adjustable Desk Phone Stand', 'description': 'Premium aluminum adjustable phone stand with anti-slip silicone pads. Compatible with all phones and tablets up to 12.9 inches. Cable management slot for tidy charging.', 'price': 24.99, 'compare_price': 34.99, 'stock': 180, 'rating': 4.6, 'is_featured': True, 'category': cat['Phone Holders'], 'brand': b['Anker']},
            {'name': 'Magnetic Car Mount', 'description': 'Ultra-strong N52 magnetic phone mount for car vents. Thin magnetic plate adheres to phone or case. 360° rotation with quick one-hand release.', 'price': 17.99, 'stock': 220, 'rating': 4.5, 'category': cat['Phone Holders'], 'brand': b['Anker']},
            {'name': 'Foldable Travel Phone Stand', 'description': 'Portable foldable phone stand for desk, bedside and travel. Compact design folds flat for storage. Weighted base prevents tipping with heavy phones.', 'price': 14.99, 'stock': 300, 'rating': 4.3, 'category': cat['Phone Holders'], 'brand': b['Realme']},
            {'name': 'Ring Holder Kickstand', 'description': 'Adhesive metal ring holder that doubles as a kickstand. 360° rotating ring for secure grip and hands-free viewing. Slim design works with most cases.', 'price': 9.99, 'stock': 500, 'rating': 4.2, 'category': cat['Phone Holders'], 'brand': b['Xiaomi']},
            {'name': 'Bike Phone Mount', 'description': 'Weatherproof bicycle phone mount with vibration dampening technology. Quick-release mechanism for easy phone access. Secure locking system keeps phone safe on rough terrain.', 'price': 21.99, 'stock': 100, 'rating': 4.4, 'category': cat['Phone Holders'], 'brand': b['Anker']},
            {'name': 'Ergonomic Desktop Stand', 'description': 'Height-adjustable ergonomic phone stand for video calls and streaming. Premium aluminum build with weighted base. Cable routing keeps desk organized.', 'price': 22.99, 'stock': 140, 'rating': 4.5, 'category': cat['Phone Holders'], 'brand': b['Anker']},
            {'name': 'Wireless Charger Stand', 'description': 'Phone stand with built-in 15W wireless charger. Adjustable viewing angle with anti-slip base. Charges phone while you watch videos or video call.', 'price': 32.99, 'stock': 90, 'rating': 4.5, 'category': cat['Phone Holders'], 'brand': b['Anker']},
        ]

        products = []
        for prod_data in products_data:
            defaults = {k: v for k, v in prod_data.items() if k not in ('category', 'brand')}
            prod, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={**defaults, 'category': prod_data['category'], 'brand': prod_data['brand']}
            )
            products.append(prod)

        self.stdout.write('Product images use Unsplash URLs via get_display_image()')

        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@gadgetglow.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user (admin/admin123)'))

        # Demo user
        demo_user, _ = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@gadgetglow.com', 'password': make_password('demo123')}
        )
        profile, _ = UserProfile.objects.get_or_create(
            user=demo_user,
            defaults={'phone': '+1234567890', 'address': '123 Tech Street, Silicon Valley, CA 94025'}
        )
        cart, _ = Cart.objects.get_or_create(user=demo_user)

        # Wishlist
        for i in range(4):
            Wishlist.objects.get_or_create(user=demo_user, product=random.choice(products))

        # Welcome notification
        Notification.objects.get_or_create(
            user=demo_user,
            title='Welcome to Gadget Glow!',
            defaults={'message': 'Thanks for joining us! Start exploring our premium mobile accessories collection.', 'notification_type': 'system'}
        )

        # Cart items for demo
        for i in range(2):
            try:
                CartItem.objects.get_or_create(cart=cart, product=random.choice(products), defaults={'quantity': 1})
            except:
                pass

        # Reviews
        for i in range(8):
            review, _ = Review.objects.get_or_create(
                product=random.choice(products),
                user=demo_user,
                defaults={'rating': random.randint(4, 5), 'comment': 'Amazing product! Great quality and fast delivery. Highly recommend!'}
            )

        # Update ratings only for reviewed products
        for prod in Product.objects.filter(reviews__isnull=False).distinct():
            prod.update_rating()

        # AI Recommendations
        for i in range(4):
            AIRecommendation.objects.get_or_create(
                user=demo_user,
                product=random.choice(products),
                defaults={'score': round(random.uniform(0.8, 0.99), 2), 'reason': 'Based on your browsing history'}
            )

        # Coupons
        coupons_data = [
            {'code': 'WELCOME10', 'description': '10% off for new users', 'discount_type': 'percentage', 'discount_value': 10, 'max_discount_amount': 50, 'valid_from': timezone.now(), 'valid_to': timezone.now() + timedelta(days=90), 'usage_limit': 100},
            {'code': 'SAVE50', 'description': '₹50 off on orders above ₹200', 'discount_type': 'fixed', 'discount_value': 50, 'min_order_amount': 200, 'valid_from': timezone.now(), 'valid_to': timezone.now() + timedelta(days=60), 'usage_limit': 50},
            {'code': 'FLASH20', 'description': 'Flash sale 20% off', 'discount_type': 'percentage', 'discount_value': 20, 'max_discount_amount': 100, 'valid_from': timezone.now(), 'valid_to': timezone.now() + timedelta(days=30), 'usage_limit': 200},
            {'code': 'FREESHIP', 'description': 'Free shipping on all orders', 'discount_type': 'fixed', 'discount_value': 10, 'min_order_amount': 50, 'valid_from': timezone.now(), 'valid_to': timezone.now() + timedelta(days=45), 'usage_limit': 500},
        ]

        for coupon_data in coupons_data:
            Coupon.objects.get_or_create(code=coupon_data['code'], defaults=coupon_data)

        # Demo orders with different statuses
        if Order.objects.filter(user=demo_user).count() == 0:
            for status in ['delivered', 'shipped', 'pending']:
                order = Order.objects.create(
                    user=demo_user,
                    total_price=random.choice([49.99, 89.99, 129.99]),
                    shipping_address='123 Tech Street, Silicon Valley, CA 94025',
                    status=status,
                    tracking_number=f'TRACK{random.randint(100000,999999)}' if status in ('shipped', 'delivered') else '',
                )
                for _ in range(random.randint(1, 3)):
                    p = random.choice(products)
                    OrderItem.objects.create(order=order, product=p, quantity=1, price=p.price)

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
        self.stdout.write(self.style.WARNING('Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING('Demo: demo / demo123'))
        self.stdout.write(self.style.SUCCESS('Coupons: WELCOME10, SAVE50, FLASH20, FREESHIP'))
