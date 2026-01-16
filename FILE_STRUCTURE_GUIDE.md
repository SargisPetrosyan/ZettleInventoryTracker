# 🏗️ Zettle Inventory Tracker - Complete File Structure Guide

## 📊 Architecture Overview with Explanations

```
zettle_inventory_tracker/
│
├─────────────────────────────────────────────────────────
│ 🎯 ROOT LEVEL - Configuration & Entry Points
├─────────────────────────────────────────────────────────
│
├── main.py
│   WHY: FastAPI application entry point
│   WHAT: 
│     - Initializes FastAPI app instance
│     - Registers all API routes
│     - Sets up middleware (CORS, error handlers, etc.)
│     - Starts the uvicorn server
│   WHEN TO EDIT: Adding new routes or middleware
│   EXAMPLE:
│     app = FastAPI()
│     app.include_router(webhooks.router)
│
├── config.py
│   WHY: Centralized configuration management
│   WHAT:
│     - Loads environment variables
│     - Defines Settings class with all config
│     - Contains database URLs, API keys, file paths
│     - Provides single source of truth for settings
│   WHEN TO EDIT: Adding new configuration parameters
│   EXAMPLE:
│     class Settings:
│         DATABASE_URL = os.getenv("DATABASE_URL")
│         ZETTLE_API_KEY = os.getenv("ZETTLE_API_KEY")
│
├── constants.py
│   WHY: Store global constants and enums
│   WHAT:
│     - Google Drive folder/template IDs
│     - Event type enums (TestMessage, InventoryUpdated, etc.)
│     - Fixed strings and magic numbers
│     - Status codes and event names
│   WHEN TO EDIT: Adding new event types or IDs
│   REASON: Avoids hardcoding values throughout codebase
│
├── logging_config.py
│   WHY: Centralized logging setup
│   WHAT:
│     - Configures logger instance
│     - Sets log level (DEBUG, INFO, WARNING, ERROR)
│     - Defines log format and output
│     - File and console handlers
│   WHEN TO EDIT: Changing log format or levels
│
├── .env
│   WHY: Environment variables (secrets)
│   WHAT:
│     - API keys (Zettle, Google)
│     - Database URLs
│     - Service endpoints
│     - Feature flags
│   SECURITY: Never commit to Git - add to .gitignore
│   EXAMPLE:
│     ZETTLE_API_KEY=your-secret-key
│     DATABASE_URL=sqlite:///./database.db
│
├── .env.example
│   WHY: Template for environment setup
│   WHAT:
│     - Shows what .env variables are needed
│     - No actual secrets (safe to commit)
│     - Helps new developers set up quickly
│   WHEN TO EDIT: Adding new environment variables
│
├── pyproject.toml
│   WHY: Project metadata and dependencies
│   WHAT:
│     - Project name, version, description
│     - All package dependencies
│     - Tool configurations (mypy, ruff, pytest)
│     - Python version requirement
│   WHEN TO EDIT: Adding/removing packages
│
├── README.md
│   WHY: Project documentation
│   WHAT:
│     - What the project does
│     - How to set it up
│     - How to run it
│     - Contributing guidelines
│
└── .gitignore
    WHY: Prevent committing sensitive files
    WHAT:
      - .env, __pycache__, .venv
      - creds/ (credentials)
      - database.db (local database)
      - .mypy_cache, .ruff_cache
    REASON: Security (don't leak secrets)
    REASON: Keep repo clean (ignore generated files)

│
├─────────────────────────────────────────────────────────
│ 📦 CORE LAYER - Business Logic (Heart of app)
├─────────────────────────────────────────────────────────
│
├── core/
│   
│   ├── __init__.py
│   │   WHY: Makes core/ a Python package
│   │
│   ├── domain/
│   │   WHY: Separate layer for data models
│   │   WHAT: Pure data classes representing entities
│   │   PRINCIPLE: No business logic, just structure
│   │   BENEFIT: Easy to test, reusable models
│   │
│   │   ├── __init__.py
│   │   │
│   │   ├── zettle.py
│   │   │   WHY: Models for Zettle-specific data
│   │   │   CONTAINS:
│   │   │     - InventoryBalanceChanged (webhook data)
│   │   │     - ProductData (product information)
│   │   │     - ZettleEvent (generic event structure)
│   │   │   EXAMPLE:
│   │   │     class InventoryBalanceChanged(BaseModel):
│   │   │         product_id: str
│   │   │         before: int
│   │   │         after: int
│   │   │         timestamp: datetime
│   │   │
│   │   ├── inventory.py
│   │   │   WHY: Models for inventory domain
│   │   │   CONTAINS:
│   │   │     - Inventory (stock levels)
│   │   │     - InventoryHistory (tracking changes)
│   │   │     - StockLevel (point-in-time data)
│   │   │
│   │   └── product.py
│   │       WHY: Models for product domain
│   │       CONTAINS:
│   │         - Product (basic info)
│   │         - ProductVariant (SKU, price)
│   │         - ProductCategory (classification)
│   │
│   ├── use_cases/
│   │   WHY: Orchestrate business logic
│   │   WHAT: "How do we do business?" - implements rules
│   │   PRINCIPLE: Calls repositories and services
│   │   BENEFIT: One place to test all business logic
│   │
│   │   ├── __init__.py
│   │   │
│   │   ├── process_inventory_update.py
│   │   │   WHY: Main business flow for inventory updates
│   │   │   DOES:
│   │   │     1. Validate webhook data (check business rules)
│   │   │     2. Calculate stock changes (before/after)
│   │   │     3. Prepare data for storage
│   │   │     4. Save to database (via repository)
│   │   │     5. Sync with Google Sheets (via service)
│   │   │     6. Return result
│   │   │   EXAMPLE:
│   │   │     def process_inventory_update(event):
│   │   │         # Validate
│   │   │         if not validate(event):
│   │   │             raise ValidationError()
│   │   │         # Update DB
│   │   │         inventory_repo.save(data)
│   │   │         # Update Sheets
│   │   │         sheets_client.update()
│   │   │
│   │   ├── sync_products.py
│   │   │   WHY: Synchronize products across systems
│   │   │   DOES:
│   │   │     1. Fetch products from Zettle API
│   │   │     2. Update local database
│   │   │     3. Sync with Google Drive
│   │   │
│   │   └── generate_reports.py
│   │       WHY: Generate inventory reports
│   │       DOES:
│   │         1. Query inventory data
│   │         2. Aggregate/calculate
│   │         3. Format for output
│   │
│   ├── repositories/
│   │   WHY: Data Access Layer (Repository Pattern)
│   │   WHAT: "How do we store/retrieve data?"
│   │   PRINCIPLE: Abstract database operations
│   │   BENEFIT: Can swap database without changing logic
│   │
│   │   ├── __init__.py
│   │   │
│   │   ├── base_repository.py
│   │   │   WHY: Abstract base class for all repositories
│   │   │   DEFINES: Common CRUD operations
│   │   │   METHODS:
│   │   │     - get_by_id(id)
│   │   │     - get_all()
│   │   │     - create(entity)
│   │   │     - update(id, entity)
│   │   │     - delete(id)
│   │   │   EXAMPLE:
│   │   │     class BaseRepository(ABC):
│   │   │         @abstractmethod
│   │   │         async def create(self, entity):
│   │   │             pass
│   │   │
│   │   ├── inventory_repository.py
│   │   │   WHY: Inventory data access
│   │   │   INHERITS FROM: BaseRepository
│   │   │   EXTRA METHODS:
│   │   │     - get_by_product_id(product_id)
│   │   │     - get_recent_updates(days=7)
│   │   │     - get_stock_level(product_id, date)
│   │   │   EXAMPLE:
│   │   │     class InventoryRepository(BaseRepository):
│   │   │         async def get_by_product_id(self, id):
│   │   │             return await db.query(Inventory).filter(...)
│   │   │
│   │   └── product_repository.py
│   │       WHY: Product data access
│   │       INHERITS FROM: BaseRepository
│   │       EXTRA METHODS:
│   │         - get_by_sku(sku)
│   │         - get_by_category(category)
│   │         - search(query)
│   │
│   └── exceptions.py
│       WHY: Custom exception classes
│       WHAT: Define error types for the app
│       CONTAINS:
│         - ZettleTrackerException (base class)
│         - ValidationError (invalid data)
│         - RepositoryError (DB failure)
│         - ExternalServiceError (API failure)
│         - AuthenticationError (auth failed)
│         - NotFoundError (resource missing)
│       BENEFIT: Easy error handling and logging
│       EXAMPLE:
│         try:
│             process_inventory()
│         except ValidationError as e:
│             log.error(f"Invalid data: {e}")
│
├─────────────────────────────────────────────────────────
│ 🔌 API LAYER - HTTP Interface
├─────────────────────────────────────────────────────────
│
├── api/
│   WHY: FastAPI routes and request/response handling
│   RESPONSIBILITY: Convert HTTP to Python, Python to HTTP
│
│   ├── __init__.py
│   │
│   ├── routes.py
│   │   WHY: Define all API endpoints
│   │   CONTAINS:
│   │     - POST /store_inventory_data_webhook
│   │     - GET /health
│   │     - POST /sync_products
│   │   DOES:
│   │     1. Receive HTTP request
│   │     2. Validate with schemas (Pydantic)
│   │     3. Call use case (business logic)
│   │     4. Return HTTP response
│   │   EXAMPLE:
│   │     @app.post("/webhook")
│   │     async def webhook(request: InventoryUpdateRequest):
│   │         result = await process_inventory_update(request)
│   │         return {"status": "success", "data": result}
│   │
│   ├── schemas.py
│   │   WHY: Request/Response data validation
│   │   WHAT: Pydantic models for validation
│   │   BENEFIT: Automatic validation, OpenAPI docs
│   │   CONTAINS:
│   │     - InventoryUpdateRequest (validate input)
│   │     - InventoryUpdateResponse (format output)
│   │     - SyncProductsRequest
│   │   EXAMPLE:
│   │     class InventoryUpdateRequest(BaseModel):
│   │         product_id: str
│   │         new_stock: int
│   │         timestamp: datetime
│   │         
│   │         @field_validator('product_id')
│   │         def validate_product_id(cls, v):
│   │             if not v:
│   │                 raise ValueError('Required')
│   │             return v
│   │
│   ├── dependencies.py
│   │   WHY: FastAPI dependency injection
│   │   WHAT: Reusable dependencies for endpoints
│   │   CONTAINS:
│   │     - get_database_session()
│   │     - get_current_user()
│   │     - get_zettle_client()
│   │   BENEFIT: Avoid code duplication, easy testing
│   │   EXAMPLE:
│   │     async def get_database_session() -> AsyncGenerator:
│   │         session = SessionLocal()
│   │         try:
│   │             yield session
│   │         finally:
│   │             await session.close()
│   │
│   └── webhooks/
│       WHY: Webhook-specific handlers
│       
│       ├── __init__.py
│       │
│       ├── zettle_webhook.py
│       │   WHY: Handle Zettle webhook events
│       │   DOES:
│       │     1. Receive webhook from Zettle
│       │     2. Verify signature (security)
│       │     3. Parse event type
│       │     4. Route to correct handler
│       │     5. Call appropriate use case
│       │   EXAMPLE:
│       │     async def handle_inventory_changed(event):
│       │         await process_inventory_update(event)
│       │
│       └── webhook_validator.py
│           WHY: Validate webhook authenticity
│           DOES:
│             1. Verify webhook signature
│             2. Check for duplicates
│             3. Validate event structure
│           BENEFIT: Prevent malicious/fake webhooks
│           EXAMPLE:
│             def verify_webhook_signature(payload, signature):
│                 expected = hmac.new(KEY, payload, sha256)
│                 return hmac.compare_digest(...)
│
├─────────────────────────────────────────────────────────
│ 📡 SERVICES LAYER - External Integrations
├─────────────────────────────────────────────────────────
│
├── services/
│   WHY: Wrap external APIs (Zettle, Google, Database)
│   PRINCIPLE: Isolate third-party dependencies
│   BENEFIT: Easy to mock/replace external services
│
│   ├── zettle/
│   │   WHY: Zettle API integration
│   │   
│   │   ├── __init__.py
│   │   │
│   │   ├── client.py
│   │   │   WHY: Wrapper for Zettle API calls
│   │   │   METHODS:
│   │   │     - get_products()
│   │   │     - get_product_by_id(id)
│   │   │     - get_inventory(product_id)
│   │   │     - update_inventory(product_id, quantity)
│   │   │   DOES:
│   │   │     1. Make HTTP requests to Zettle
│   │   │     2. Add authentication headers
│   │   │     3. Handle errors (convert to custom errors)
│   │   │     4. Return parsed data
│   │   │
│   │   ├── auth.py
│   │   │   WHY: Manage Zettle authentication
│   │   │   DOES:
│   │   │     1. Store API key
│   │   │     2. Refresh tokens if needed
│   │   │     3. Provide credentials to client
│   │   │
│   │   └── errors.py
│   │       WHY: Zettle-specific exception classes
│   │       CONTAINS:
│   │         - ZettleServiceError (base)
│   │         - ZettleAuthError (auth failed)
│   │         - ZettleAPIError (API failed)
│   │
│   ├── google_drive/
│   │   WHY: Google Drive & Sheets integration
│   │   
│   │   ├── __init__.py
│   │   │
│   │   ├── client.py
│   │   │   WHY: Google Drive API operations
│   │   │   METHODS:
│   │   │     - copy_file(source_id, new_title, folder_id)
│   │   │     - create_folder(name, parent_id)
│   │   │     - delete_file(file_id)
│   │   │     - list_files(folder_id)
│   │   │
│   │   ├── sheets_client.py
│   │   │   WHY: Google Sheets specific operations
│   │   │   METHODS:
│   │   │     - update_cell(spreadsheet_id, range, value)
│   │   │     - update_range(spreadsheet_id, range, values)
│   │   │     - get_values(spreadsheet_id, range)
│   │   │     - append_row(spreadsheet_id, values)
│   │   │
│   │   ├── auth.py
│   │   │   WHY: Google authentication
│   │   │   DOES:
│   │   │     1. Read credentials.json
│   │   │     2. Manage OAuth tokens
│   │   │     3. Refresh token if expired
│   │   │
│   │   └── errors.py
│   │       WHY: Google-specific exceptions
│   │       CONTAINS:
│   │         - GoogleServiceError (base)
│   │         - GoogleAuthError (auth failed)
│   │         - GoogleAPIError (API failed)
│   │
│   └── database/
│       WHY: Database connection & models
│       
│       ├── __init__.py
│       │
│       ├── connection.py
│       │   WHY: Manage database connections
│       │   DOES:
│       │     1. Create engine
│       │     2. Create session factory
│       │     3. Provide session management
│       │   EXAMPLE:
│       │     engine = create_engine(DATABASE_URL)
│       │     SessionLocal = sessionmaker(engine)
│       │
│       ├── models.py
│       │   WHY: SQLModel database table definitions
│       │   CONTAINS:
│       │     - Inventory (table)
│       │     - Product (table)
│       │     - InventoryHistory (table)
│       │   NOTE: These are database models, not domain models
│       │   DIFFERENCE:
│       │     - Domain models: Pure Python classes
│       │     - DB models: SQLModel with database columns
│       │
│       └── migrations.py
│           WHY: Database schema versioning
│           DOES:
│             1. Track schema changes
│             2. Apply upgrades/downgrades
│             3. Version control for database
│
├─────────────────────────────────────────────────────────
│ 🛠️ SHARED LAYER - Reusable Utilities
├─────────────────────────────────────────────────────────
│
├── shared/
│   WHY: Utilities used across multiple layers
│   PRINCIPLE: No dependencies on core or api
│
│   ├── __init__.py
│   │
│   ├── utils.py
│   │   WHY: General utility functions
│   │   CONTAINS:
│   │     - format_date(date)
│   │     - parse_json(string)
│   │     - convert_currency(amount)
│   │     - hash_data(data)
│   │   BENEFIT: Avoid code duplication
│   │
│   ├── validators.py
│   │   WHY: Data validation logic
│   │   CONTAINS:
│   │     - validate_sku(sku)
│   │     - validate_quantity(qty)
│   │     - validate_email(email)
│   │   BENEFIT: Centralized validation rules
│   │
│   ├── serializers.py
│   │   WHY: Convert objects to/from formats
│   │   DOES:
│   │     1. Convert Python objects to JSON
│   │     2. Convert JSON to Python objects
│   │     3. Format data for external APIs
│   │
│   └── decorators.py
│       WHY: Reusable decorators
│       CONTAINS:
│         - @retry_on_failure (retry failed calls)
│         - @log_execution (log function calls)
│         - @cache_result (cache function result)
│       BENEFIT: Add cross-cutting concerns
│
├─────────────────────────────────────────────────────────
│ 🧪 TESTS - Unit & Integration Tests
├─────────────────────────────────────────────────────────
│
├── tests/
│   WHY: Verify everything works correctly
│   PRINCIPLE: Test all layers independently
│
│   ├── conftest.py
│   │   WHY: Pytest configuration & fixtures
│   │   CONTAINS:
│   │     - Database fixtures
│   │     - Mock API fixtures
│   │     - Sample data
│   │   BENEFIT: Reusable test setup
│   │
│   ├── unit/
│   │   WHY: Test individual components
│   │   ISOLATION: Mock all dependencies
│   │
│   │   ├── test_repositories.py
│   │   │   WHY: Test repository layer
│   │   │   TESTS:
│   │   │     - get_by_id() works
│   │   │     - save() works
│   │   │     - custom queries work
│   │   │   EXAMPLE:
│   │   │     def test_get_inventory_by_id():
│   │   │         repo = InventoryRepository(mock_db)
│   │   │         result = repo.get_by_id("123")
│   │   │         assert result.id == "123"
│   │   │
│   │   ├── test_use_cases.py
│   │   │   WHY: Test business logic
│   │   │   TESTS:
│   │   │     - process_inventory_update() works
│   │   │     - validates correctly
│   │   │     - calls dependencies correctly
│   │   │
│   │   └── test_validators.py
│   │       WHY: Test validation rules
│   │       TESTS:
│   │         - Valid data passes
│   │         - Invalid data fails
│   │
│   └── integration/
│       WHY: Test components together
│       INTEGRATION: Real database or mocked APIs
│
│       ├── test_zettle_integration.py
│       │   WHY: Test Zettle API integration
│       │   TESTS:
│       │     - Can authenticate
│       │     - Can fetch products
│       │     - Can get inventory
│       │
│       ├── test_google_drive_integration.py
│       │   WHY: Test Google Drive integration
│       │   TESTS:
│       │     - Can authenticate
│       │     - Can read files
│       │     - Can update sheets
│       │
│       └── test_api_endpoints.py
│           WHY: Test full API flow
│           TESTS:
│             - POST /webhook works end-to-end
│             - GET /health works
│             - Error handling works
│
├─────────────────────────────────────────────────────────
│ 📊 DATA & CREDENTIALS
├─────────────────────────────────────────────────────────
│
├── data/
│   WHY: Store application data files
│   
│   ├── templates/
│   │   WHY: Google Sheets templates
│   │   CONTAINS:
│   │     - Daily inventory template
│   │     - Monthly report template
│   │
│   └── samples/
│       WHY: Sample data for testing
│       CONTAINS:
│         - Example JSON responses
│         - Test inventory data
│
└── creds/
    WHY: Store credentials (NEVER COMMIT)
    
    ├── credentials.json
    │   WHY: Google API credentials
    │   SECURITY: Add to .gitignore
    │
    └── token.json
        WHY: Google API access token
        SECURITY: Add to .gitignore
```

---

## 🎯 Why This Structure?

### 1. **Separation of Concerns**
Each folder has ONE responsibility:
- `api/` handles HTTP
- `core/` handles business logic
- `services/` handles external APIs
- `shared/` handles utilities

✅ **Benefit**: Easy to find code, easy to change one thing without breaking others

---

### 2. **Testability**
Each layer can be tested independently:
- Mock repositories for use case tests
- Mock services for integration tests
- Real database for integration tests

✅ **Benefit**: Fast, isolated tests that don't depend on each other

---

### 3. **Maintainability**
Clear file organization makes it easy to:
- Find where to add new code
- Understand existing code
- Make changes safely

✅ **Benefit**: New developers onboard faster

---

### 4. **Scalability**
Easy to add new features:
- New domain entity? Add to `core/domain/`
- New business process? Add to `core/use_cases/`
- New external API? Add to `services/`

✅ **Benefit**: Project grows without becoming chaotic

---

### 5. **Dependency Management**
Clear import rules prevent circular dependencies:
- API can import from Core
- Core can import from Repositories
- Services can't import from API/Core

✅ **Benefit**: No circular dependencies, easier to understand

---

## 📋 Quick Decision Guide

| Need | Location |
|------|----------|
| New entity type? | `core/domain/` |
| New business process? | `core/use_cases/` |
| New data queries? | `core/repositories/` |
| New API endpoint? | `api/routes.py` + `api/schemas.py` |
| New external service? | `services/<name>/` |
| Shared utility? | `shared/` |
| New test? | `tests/unit/` or `tests/integration/` |
| New error type? | `core/exceptions.py` or `services/<name>/errors.py` |

---

## 🚀 Import Examples

**Correct ✅:**
```python
# api/routes.py imports from core
from core.use_cases.process_inventory_update import process_inventory_update

# core/use_cases imports from repositories and services
from core.repositories.inventory_repository import InventoryRepository
from services.google_drive.sheets_client import SheetsClient

# services imports from shared
from shared.validators import validate_sku
```

**Wrong ❌:**
```python
# ❌ Core should NOT import from API
from api.routes import some_function

# ❌ API should NOT directly use database
from services.database.connection import get_session
```

---

## 📈 Growth Path

Start simple, grow gradually:

**Phase 1: MVP**
- Just implement core business logic
- Simple API routes
- Direct database access

**Phase 2: Scale**
- Add repository pattern
- Add validation layer
- Add error handling

**Phase 3: Enterprise**
- Add microservices
- Add message queues
- Add caching layer

This structure supports all phases!
