# Multi-Tenant Django Demo

A working multi-tenant document management API built with Django, django-tenants,
and Django REST Framework. Built to learn the patterns, not as production code.

## What This Demonstrates

**The exact thing micro1 will ask you about.**

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  PostgreSQL                          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ acme_corp │  │ globex   │  │ initech  │          │
│  │  schema   │  │  schema  │  │  schema  │          │
│  │           │  │          │  │          │          │
│  │ documents │  │ documents│  │ documents│          │
│  │ auth_user │  │ auth_user│  │ auth_user│          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  ┌──────────────────────────────────────────┐       │
│  │              public schema                │       │
│  │  tenants_client, tenants_domain,          │       │
│  │  django_site, etc.                        │       │
│  └──────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

Each tenant gets their own PostgreSQL schema. Documents in `acme_corp` schema
are physically invisible to queries in the `globex` schema — no WHERE tenant_id
clause needed, no risk of filtering mistakes.

### Request Flow

```
Request: GET api.acme.localhost/api/documents/
    │
    ▼
Django-Tenants Middleware
    │  Detects tenant from subdomain
    │  Sets PostgreSQL search_path = "acme_corp"
    ▼
DocumentViewSet.get_queryset()
    │  Document.objects.all()
    │  (PostgreSQL only sees acme_corp.documents table)
    ▼
Returns: Acme Corp's documents only
```

### Key Files

| File | What It Does |
|------|-------------|
| `core/settings.py` | SHARED_APPS vs TENANT_APPS split, database routing |
| `tenants/models.py` | Client (TenantMixin) with auto-create/auto-drop schemas |
| `documents/models.py` | Document model — lives in tenant schemas |
| `documents/views.py` | DRF ViewSet — isolation is automatic, no tenant_id in queries |
| `verify_isolation.py` | Creates a doc in acme, proves initech can't see it |

## Running It

```bash
cd ~/code/multi-tenant-demo
source venv/bin/activate

# Start PostgreSQL (Docker)
docker start multitenant-pg

# Run the verification
python verify_isolation.py

# Start the dev server
python manage.py runserver
```

## Interview Talking Points

When micro1 asks about multi-tenancy, you can say:

> "I built a multi-tenant system using Django and django-tenants with
> PostgreSQL schemas.  Each tenant gets their own schema — so their data
> is physically isolated at the database level, not just filtered at the
> application level.  The middleware detects the tenant from the
> subdomain, sets the PostgreSQL search_path, and all subsequent queries
> automatically hit the right schema.  I wrote a verification script
> that proved cross-tenant data leaks are impossible — a document
> created in one schema is invisible to queries in another."

Then pivot to your HuQAS experience:

> "I use the same pattern at HuQAS for our clinical laboratory system.
> Each lab is a tenant with its own schema, but user accounts are shared
> at the public level so staff can switch between labs without
> re-authenticating."

## The Three Approaches (for the interview)

| Approach | How | Pro | Con |
|----------|-----|-----|-----|
| Shared DB + tenant_id | Every table has FK to tenant | Simplest | One bad query = data leak |
| Separate databases | Per-tenant database | Strongest isolation | N x migrations, N x backups |
| **PostgreSQL schemas** | Per-tenant schema in one DB | Strong isolation + single DB | Requires PostgreSQL |

**Rule of thumb:** shared DB for internal tools, schemas for most SaaS, separate
databases for regulated industries (HIPAA, SOC2).
