"""
Backend Project Structure for Restaurant OS

backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings
│   │   ├── security.py        # JWT & password hashing
│   │   ├── database.py        # Database connection
│   │   └── constants.py       # App constants
│   ├── middleware/            # Custom middleware
│   │   ├── tenant.py         # Multi-tenant middleware
│   │   ├── logging.py        # Logging middleware
│   │   └── error_handler.py  # Error handling
│   ├── models/               # SQLAlchemy models
│   │   ├── base.py          # Base model
│   │   ├── tenancy.py       # Restaurant, Branch, User models
│   │   ├── menu.py          # Category, Product models
│   │   ├── inventory.py     # Inventory models
│   │   ├── orders.py        # Order models
│   │   ├── payments.py      # Payment models
│   │   └── analytics.py     # Analytics models
│   ├── schemas/             # Pydantic schemas
│   │   ├── base.py         # Base schemas
│   │   ├── auth.py         # Auth schemas
│   │   ├── menu.py         # Menu schemas
│   │   ├── orders.py       # Order schemas
│   │   └── ...
│   ├── services/           # Business logic
│   │   ├── auth.py        # Authentication service
│   │   ├── restaurant.py  # Restaurant service
│   │   ├── menu.py        # Menu service
│   │   ├── orders.py      # Order service
│   │   ├── inventory.py   # Inventory service
│   │   ├── payments.py    # Payment service
│   │   └── analytics.py   # Analytics service
│   ├── api/                # API routes
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── restaurants.py
│   │           ├── menu.py
│   │           ├── orders.py
│   │           ├── inventory.py
│   │           ├── payments.py
│   │           └── analytics.py
│   ├── ws/                 # WebSocket handlers
│   │   ├── kitchen.py     # Kitchen display system
│   │   └── notifications.py
│   ├── utils/             # Utility functions
│   │   ├── validators.py
│   │   ├── pagination.py
│   │   ├── cache.py
│   │   └── exceptions.py
│   └── __init__.py
├── tests/                 # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_orders.py
│   └── ...
├── migrations/            # Alembic migrations
├── .env                   # Environment variables
├── main.py               # ASGI entry point
└── docker/               # Docker files
    ├── Dockerfile
    └── docker-compose.yml

"""

