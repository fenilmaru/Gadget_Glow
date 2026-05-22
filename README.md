# Gadget Glow - AI-Powered E-Commerce Platform

A production-ready, full-stack Django AI-powered e-commerce web application for mobile accessories. Built with enterprise-level architecture, security, and scalability.

## Features

### Core Features
- **AI-Powered** - Chatbot, product recommendations, smart search, sentiment analysis, description generation (OpenAI)
- **RESTful API** - Full DRF API with versioning, filtering, pagination, Swagger/ReDoc docs
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **Role-Based Access** - Admin, Customer, Seller roles with granular permissions
- **Product Management** - Categories, Brands, Variants, Images, Stock tracking, Soft delete
- **Cart & Orders** - Full checkout flow, inventory locking, atomic transactions, coupon system
- **Payment System** - Idempotent payment handling, transaction logs, webhook-ready
- **Admin Analytics** - Dashboard with Chart.js, sales data, user analytics, inventory monitoring
- **Real-time** - Django Channels WebSocket-ready architecture
- **Security** - CSRF, XSS, SQL injection prevention, rate limiting, audit logging, security headers

### Tech Stack
| Category | Technology |
|---|---|
| Backend | Django 5+, Django REST Framework |
| Database | PostgreSQL (SQLite for dev) |
| Auth | JWT (SimpleJWT) |
| Cache | Redis / LocMemCache |
| Queue | Celery |
| AI | OpenAI API (GPT-4) |
| Real-time | Django Channels + Redis |
| Docs | drf-yasg (Swagger/ReDoc) |
| Frontend | Django Templates + Bootstrap-style CSS |
| Deployment | Docker, Nginx, Gunicorn, CI/CD |

## Project Structure

```
Gadget_Glow/
├── Gadget_Glow/           # Project config
│   ├── settings.py        # All production settings
│   ├── urls.py            # Main URL routing
│   ├── views.py           # Template-based views
│   ├── middleware.py       # Security headers, audit, rate limiting
│   ├── permissions.py     # RBAC permissions
│   ├── utils.py           # Pagination, helpers, exception handler
│   ├── celery.py          # Celery configuration
│   ├── wsgi.py / asgi.py  # Deployment entry points
│   └── context_processors.py
├── users/                 # Authentication & profiles
├── products/              # Products, categories, brands
├── cart/                  # Shopping cart
├── orders/                # Orders & order items
├── payments/              # Payment processing & logs
├── ai_features/           # OpenAI integration
├── analytics_app/         # Admin analytics & audit logs
├── notifications/         # User notifications
├── reviews/               # Product reviews
├── discounts/             # Coupon management
├── templates/             # All UI templates
├── static/                # Static files
├── media/                 # User uploads
├── logs/                  # Application logs
├── .github/workflows/     # CI/CD pipeline
├── Dockerfile             # Production Docker image
├── docker-compose.yml     # Multi-container setup
├── nginx.conf             # Nginx configuration
├── requirements.txt       # Dependencies
└── .env.example           # Environment variables
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite works for dev)
- Redis (optional, falls back to LocMemCache)

### 1. Setup Environment
```bash
# Clone the repository
git clone <repo-url>
cd Gadget_Glow

# Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings, or use defaults for development
```

### 3. Database Setup
```bash
# For SQLite (default dev):
python manage.py migrate

# For PostgreSQL (production):
# 1. Create database: createdb gadget_glow
# 2. Set in .env:
#    DB_ENGINE=django.db.backends.postgresql
#    DB_NAME=gadget_glow
#    DB_USER=postgres
#    DB_PASSWORD=yourpassword
# 3. Run migrate:
python manage.py migrate
```

### 4. Create Superuser & Seed Data
```bash
python manage.py createsuperuser --username admin --email admin@example.com
# Password: admin123 (or your choice)

# Seed sample data (products, coupons, demo user):
python manage.py seed_data
```

### 5. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 6. Access the Application
| URL | Description |
|---|---|
| http://localhost:8000/ | Home page |
| http://localhost:8000/admin/ | Django Admin |
| http://localhost:8000/dashboard/ | Admin Dashboard |
| http://localhost:8000/swagger/ | Swagger API Docs |
| http://localhost:8000/redoc/ | ReDoc API Docs |

## API Endpoints

### Authentication (`/api/v1/auth/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/register/` | User registration |
| POST | `/login/` | Login (returns JWT) |
| POST | `/logout/` | Logout (blacklist token) |
| GET | `/profile/` | Get user profile |
| PUT | `/profile/` | Update profile |
| POST | `/change-password/` | Change password |
| POST | `/token/refresh/` | Refresh JWT token |

### Products (`/api/v1/products/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | List products (paginated, filterable) |
| GET | `/{id}/` | Product detail |
| GET | `/featured/` | Featured products |
| GET | `/search/?q=term` | AI-powered smart search |
| GET | `/low_stock/` | Low stock alerts (admin) |
| GET | `/categories/` | List categories |
| GET | `/brands/` | List brands |

### Cart (`/api/v1/cart/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Get cart |
| POST | `/add_item/` | Add item to cart |
| POST | `/update_quantity/` | Update item quantity |
| POST | `/remove_item/` | Remove item from cart |
| POST | `/clear/` | Clear cart |

### Orders (`/api/v1/orders/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | List orders (user-specific) |
| POST | `/` | Create order (from cart) |
| GET | `/{id}/` | Order detail |
| POST | `/{id}/cancel/` | Cancel order |
| POST | `/{id}/update_status/` | Update status (admin) |

### AI Features (`/api/v1/ai/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/recommendations/` | Personalized AI recommendations |
| POST | `/chat/chat/` | AI chatbot conversation |
| GET | `/chat/history/` | Chat history |
| POST | `/search/search/` | Smart search with NLP |
| POST | `/sentiment/analyze/` | Review sentiment analysis |
| POST | `/describe/generate/` | AI product description |

### Analytics (`/api/v1/analytics/`) - Admin Only
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/` | Dashboard statistics |
| GET | `/sales_chart/?days=30` | Sales chart data |
| GET | `/top_products/` | Top selling products |
| GET | `/audit_logs/` | Audit log entries |

### Payments (`/api/v1/payments/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Create payment |
| POST | `/{id}/process/` | Process payment (admin) |
| POST | `/{id}/refund/` | Refund payment (admin) |
| POST | `/webhook/` | Payment gateway webhook |

### Notifications (`/api/v1/notifications/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | List notifications |
| POST | `/{id}/mark_read/` | Mark as read |
| POST | `/mark_all_read/` | Mark all as read |
| GET | `/unread_count/` | Unread count |

## AI Features

### Product Recommendations
AI analyzes user purchase history and browsing patterns to suggest relevant products:
```python
from ai_features.services import get_ai_recommendations
recommendations = get_ai_recommendations(user, limit=8)
```

### Smart Search
Natural language processing for product search:
```
POST /api/v1/ai/search/search/
{"query": "best wireless earphones under 2000"}
```

### Sentiment Analysis
Analyze product reviews for positive/negative sentiment:
```python
from ai_features.services import analyze_sentiment
result = analyze_sentiment("Great product, highly recommend!", review_id=1)
# Returns: {"sentiment": "positive", "confidence_score": 0.95, "key_points": [...]}
```

### AI Chatbot
GadgetBot - an intelligent shopping assistant:
- Product recommendations and comparisons
- Order tracking
- Technical specifications
- FAQs

### Product Description Generator
SEO-friendly product descriptions via AI:
```python
from ai_features.services import generate_product_description
desc = generate_product_description("Fast Charger", "Chargers", ["20W PD", "USB-C"])
```

## Security Features

- **JWT Authentication** with access/refresh token rotation and blacklisting
- **RBAC** - Admin, Customer, Seller roles
- **Security Headers** - XSS, X-Frame-Options, Content-Type, HSTS
- **Rate Limiting** - Brute-force protection on login
- **Audit Logging** - All write operations logged
- **Input Validation** - DRF serializers with comprehensive validation
- **SQL Injection Prevention** - Django ORM (no raw queries)
- **CSRF Protection** - Enabled for session auth
- **Environment Variables** - No hardcoded secrets
- **CORS** - Configurable allowed origins
- **HTTPS-ready** - Session/cookie security settings

## Deployment

### Docker
```bash
docker-compose up -d
```
This starts: Django (gunicorn), PostgreSQL, Redis, Celery Worker, Celery Beat, Nginx

### Manual (Production)
```bash
# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn Gadget_Glow.wsgi:application --workers 4 --bind 0.0.0.0:8000

# Run celery
celery -A Gadget_Glow worker -l info
celery -A Gadget_Glow beat -l info
```

### Platform Options
- **Render**: Connect GitHub repo, set build command, start command
- **Railway**: Deploy via GitHub, add PostgreSQL + Redis add-ons
- **AWS**: Use Elastic Beanstalk or ECS with RDS and ElastiCache

## Performance Optimizations
- Redis caching for queries and API responses
- Database indexing on all frequently queried fields
- Pagination for all list endpoints
- `select_related`/`prefetch_related` for eager loading
- Celery for async/background tasks
- Atomic requests for data integrity
- CDN-ready static file structure

## Testing
```bash
# Run all tests
python manage.py test users products cart orders payments reviews ai_features

# With coverage
pip install pytest pytest-django pytest-cov
pytest --cov=. --cov-report=html
```

## License
MIT

## Author
Built with Django, DRF, OpenAI, and enterprise best practices.
