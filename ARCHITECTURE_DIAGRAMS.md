# 🏗️ Architecture & Data Flow Diagrams

## 1️⃣ LAYERED ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SYSTEMS                           │
│  (Zettle POS API, Google Drive API, Client Browser)         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Request/Response
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 🔌 API LAYER                                                 │
│  Routes │ Schemas │ Dependencies │ Webhook Handlers         │
│  Job: Convert HTTP ↔ Python                                  │
│  WHO DEPENDS ON ME: External clients                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Call use cases
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 📦 CORE LAYER (Business Logic)                              │
│  Use Cases │ Repositories │ Domain Models │ Exceptions      │
│  Job: Implement business rules                               │
│  WHO DEPENDS ON ME: API layer                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ Call services + repositories
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│📡 SERVICES  │ │📡 SERVICES   │ │📡 SERVICES   │
│  Zettle     │ │  Google Drive│ │  Database    │
│  API Wrapper│ │  API Wrapper │ │  Connection  │
│  Job: Talk  │ │  Job: Talk   │ │  Job: Manage │
│  to 3rd     │ │  to 3rd      │ │  data storage│
│  parties    │ │  parties     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌──────────┐    ┌──────────┐
   │ Zettle │    │  Google  │    │ SQLite   │
   │ Server │    │  Server  │    │ Database │
   └────────┘    └──────────┘    └──────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🛠️  SHARED LAYER (Bottom - Available to all)               │
│  Utils │ Validators │ Serializers │ Decorators              │
│  Job: Provide reusable utilities                             │
│  WHO DEPENDS ON ME: Everyone (but not other way around)     │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle: Outer layers depend on inner layers, never reverse!**
- API depends on Core ✅
- Core depends on Services ✅
- API depends on Services ❌

---

## 2️⃣ REQUEST FLOW EXAMPLE: Webhook Event

```
Zettle Webhook arrives
       │
       ▼
POST /store_inventory_data_webhook
       │
       ├─ 🔌 API LAYER (api/routes.py)
       │  ├─ Receives HTTP request
       │  ├─ Validates with schema (api/schemas.py)
       │  │  └─ Checks: required fields, data types
       │  ├─ Gets dependencies (api/dependencies.py)
       │  │  └─ Database session, logger
       │  └─ Calls use case
       │
       ├─ 📦 CORE LAYER (core/use_cases/process_inventory_update.py)
       │  ├─ Receives validated data
       │  ├─ Validates business rules
       │  │  └─ Check: quantity > 0? product exists?
       │  ├─ Calls repository
       │  │  └─ Saves to database
       │  ├─ Calls service
       │  │  └─ Updates Google Sheets
       │  └─ Returns result
       │
       ├─ 📡 SERVICES LAYER
       │  ├─ Repository (core/repositories/inventory_repository.py)
       │  │  ├─ Creates SQL query
       │  │  ├─ Saves to database
       │  │  └─ Returns saved record
       │  │
       │  └─ Google Sheets Service (services/google_drive/sheets_client.py)
       │     ├─ Prepares data for Google API
       │     ├─ Makes API call
       │     └─ Handles errors
       │
       └─ 🔌 API LAYER (Response)
          ├─ Formats result with schema
          ├─ Sets HTTP status code (200, 400, 500)
          └─ Returns JSON response

Client receives HTTP response
```

---

## 3️⃣ FILE LOCATION DECISION TREE

```
I need to add code for...

    │
    ├─ Handling HTTP request? → api/routes.py
    │  └─ Validating request data? → api/schemas.py
    │
    ├─ Business logic? → core/use_cases/
    │  ├─ Working with inventory? → core/domain/inventory.py
    │  ├─ Working with products? → core/domain/product.py
    │
    ├─ Storing/retrieving data? → core/repositories/
    │  ├─ Inventory queries? → core/repositories/inventory_repository.py
    │  ├─ Product queries? → core/repositories/product_repository.py
    │
    ├─ Talking to Zettle API? → services/zettle/
    │  ├─ Making requests? → services/zettle/client.py
    │  ├─ Handling auth? → services/zettle/auth.py
    │
    ├─ Talking to Google? → services/google_drive/
    │  ├─ Drive operations? → services/google_drive/client.py
    │  ├─ Sheets operations? → services/google_drive/sheets_client.py
    │
    ├─ Error type? → core/exceptions.py (or service-specific)
    │
    ├─ Utility function? → shared/utils.py
    │
    ├─ Validation rule? → shared/validators.py
    │
    └─ Test? → tests/unit/ or tests/integration/
```

---

## 4️⃣ DOMAIN MODEL RELATIONSHIPS

```
┌─────────────────────────────────────────────────────────────┐
│  Zettle Webhook Event                                        │
│  └─ type: "InventoryBalanceChanged"                         │
│  └─ data:                                                    │
│       ├─ product_id                                         │
│       ├─ before: 100                                        │
│       └─ after: 95                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │ Parsed by:
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  core/domain/zettle.py                                       │
│  └─ InventoryBalanceChanged (data model)                    │
│     ├─ product_id: str                                      │
│     ├─ before: int                                          │
│     ├─ after: int                                           │
│     └─ timestamp: datetime                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │ Used by:
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  core/use_cases/process_inventory_update.py                 │
│  └─ process_inventory_update(event: InventoryBalanceChanged)│
│     └─ Calculates: change = after - before                 │
│        Validates: product exists? stock valid?             │
│        Creates: Inventory record                            │
│        Returns: InventoryUpdateResult                       │
└──────────────────┬──────────────────────────────────────────┘
                   │ Stored as:
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  services/database/models.py (DB model)                      │
│  └─ Inventory (SQLModel table)                              │
│     ├─ id: UUID (primary key)                               │
│     ├─ product_id: str (foreign key)                        │
│     ├─ before: int                                          │
│     ├─ after: int                                           │
│     └─ timestamp: datetime                                  │
│     └─ Stored in SQLite database                            │
└─────────────────────────────────────────────────────────────┘

Note: 
- core/domain models are PURE Python (no DB dependencies)
- services/database models are SQLMODEL (with DB dependencies)
```

---

## 5️⃣ DEPENDENCY INJECTION EXAMPLE

```
HTTP Request arrives
       │
       ▼
app.post("/webhook")
async def handle_webhook(
    request: InventoryUpdateRequest,  ← From request body
    session: AsyncSession = Depends(get_database_session),  ← Injected
    logger = Depends(get_logger),  ← Injected
    sheets_client = Depends(get_sheets_client)  ← Injected
):
    # Dependencies are provided automatically!
    # This is dependency injection - pass dependencies instead of 
    # creating them inside the function
    
    # Benefits:
    # ✅ Easy to test (mock the dependencies)
    # ✅ Centralized configuration
    # ✅ Single responsibility (function focuses on logic, not setup)
    
    result = await process_inventory_update(
        event=request.data,
        repo=InventoryRepository(session),
        sheets_client=sheets_client
    )
    return result

# In api/dependencies.py, we define how to create dependencies:
async def get_database_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def get_sheets_client() -> SheetsClient:
    return SheetsClient(credentials=read_credentials())
```

---

## 6️⃣ ERROR HANDLING FLOW

```
Use case executes:

    try:
        inventory = await repo.get_by_id(product_id)
        if not inventory:
            raise NotFoundError(f"Product {product_id} not found")  ← Custom error
        
        if new_stock < 0:
            raise ValidationError("Stock cannot be negative")  ← Custom error
        
        result = await repo.save(inventory)
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise  ← Let API handle it
        
    except RepositoryError as e:
        logger.error(f"Database error: {e}")
        raise ExternalServiceError(f"Database unavailable")  ← Convert to generic
        
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        raise  ← Let caller handle

API receives error:

    try:
        result = await process_inventory_update(...)
        return {"status": "success", "data": result}
        
    except ValidationError as e:
        return {"status": "error", "message": str(e)}, 400  ← Bad request
        
    except NotFoundError as e:
        return {"status": "error", "message": str(e)}, 404  ← Not found
        
    except ExternalServiceError as e:
        return {"status": "error", "message": str(e)}, 503  ← Service unavailable
        
    except Exception as e:
        logger.critical(f"Unhandled error: {e}")
        return {"status": "error", "message": "Internal error"}, 500

Client receives HTTP response with appropriate status code ✅
```

---

## 7️⃣ TESTING STRATEGY

```
Test Pyramid:

                    △
                   /\
                  /  \  Integration Tests
                 /────\ (5-10 tests)
                /      \ 
               /        \ Real or heavily mocked services
              /──────────\
             /            \ Unit Tests (20-50 tests)
            /              \ Fast, isolated, heavily mocked
           /────────────────\
          /                  \
         /   End-to-End Tests \ (1-3 tests)
        /──────────────────────\
       /                        \
      /                          \

Unit Tests Example:
├─ Test repositories (mock database)
│  └─ test_inventory_repo.get_by_id() returns correct record
├─ Test use cases (mock repositories + services)
│  └─ test_process_inventory_update() calls repo.save() correctly
└─ Test validators (pure functions)
   └─ test_validate_quantity() rejects negative numbers

Integration Tests Example:
├─ Test with real database
│  └─ test_save_and_retrieve_inventory() uses SQLite
└─ Test with mocked external APIs
   └─ test_sync_with_google_sheets() mocks Google API

End-to-End Tests Example:
└─ test_webhook_full_flow()
   ├─ Sends HTTP request to POST /webhook
   ├─ Checks database was updated
   └─ Checks Google Sheets was updated
```

---

## 8️⃣ ADDING NEW FEATURE CHECKLIST

Adding a new feature? Follow this flow:

```
1. Define the domain model
   └─ File: core/domain/new_entity.py
   └─ What it is: Python dataclass with fields

2. Create the use case
   └─ File: core/use_cases/handle_new_feature.py
   └─ What it does: Business logic for the feature

3. Add repository method if needed
   └─ File: core/repositories/new_repository.py (if new entity)
   └─ What it does: Data access for the new entity

4. Create API endpoint
   └─ File: api/routes.py (add new route)
   └─ File: api/schemas.py (add request/response models)
   └─ What it does: HTTP interface

5. Add any external service calls
   └─ File: services/new_service/
   └─ What it does: Wrapper for third-party API

6. Add exception types if needed
   └─ File: core/exceptions.py or services/new_service/errors.py
   └─ What they are: Custom error types

7. Write tests
   └─ File: tests/unit/test_new_feature.py
   └─ File: tests/integration/test_new_feature_integration.py
   └─ What they do: Verify the feature works

8. Update .env.example if needed
   └─ Add new environment variables needed

Done! ✅
```

---

## 9️⃣ WHY NOT JUST PUT EVERYTHING IN ONE FILE?

```
❌ Single file approach (Bad):
main.py (10,000+ lines)
  ├─ HTTP routes
  ├─ Business logic
  ├─ Database code
  ├─ External API calls
  ├─ Validation
  ├─ Error handling
  ├─ Tests (somehow)
  └─ Everything else!

Problems:
- Hard to find anything (where is the inventory update logic?)
- Hard to change anything (change one thing, break 3 others)
- Hard to test (can't test business logic without real database)
- Hard to reuse code (business logic tied to HTTP layer)
- Hard to understand (what is the core business logic?)
- New developers get lost ❌

✅ Layered approach (Good):
├─ api/routes.py (just HTTP)
├─ core/use_cases/process_inventory.py (just business logic)
├─ core/repositories/inventory_repo.py (just data access)
├─ services/google_drive/sheets_client.py (just Google API)
└─ tests/unit/ (fast, isolated tests)

Benefits:
- Easy to find code (where inventory updates? → core/use_cases/)
- Easy to change (change DB? Just update repository)
- Easy to test (mock the database, test business logic)
- Easy to reuse (business logic is separate from HTTP)
- Easy to understand (clear purpose for each file)
- New developers get productive quickly ✅
```

---

## 🔟 SUMMARY: THE 4 LAYERS

| Layer | Purpose | Depends On | Examples |
|-------|---------|-----------|----------|
| **API** | HTTP interface | Core, Shared | routes.py, schemas.py, webhooks/ |
| **CORE** | Business logic | Services, Shared | use_cases/, repositories/, domain/ |
| **SERVICES** | External APIs | Shared | zettle/, google_drive/, database/ |
| **SHARED** | Reusable utils | Nothing | utils.py, validators.py |

**Golden Rule**: Inner layers never know about outer layers!
- Core doesn't import from API ✅
- Services don't import from Core ✅
- Shared doesn't import from anyone ✅
