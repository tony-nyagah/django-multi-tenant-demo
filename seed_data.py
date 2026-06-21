"""Seed test data — creates users and documents in each tenant schema.
Demonstrates data isolation: Acme users can't see Globex documents."""

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/home/tony/code/multi-tenant-demo')

django.setup()

from tenants.models import Client
from django.contrib.auth import get_user_model
from django.db import connection
from documents.models import Document

User = get_user_model()

def seed_tenant(tenant):
    """Seed a single tenant schema with users and documents."""
    connection.set_schema(tenant.schema_name)

    # Create users for this tenant
    alice, _ = User.objects.get_or_create(
        username=f"alice_{tenant.schema_name}",
        defaults={"email": f"alice@{tenant.schema_name}.com", "is_staff": True}
    )
    alice.set_password("pass123")
    alice.save()

    bob, _ = User.objects.get_or_create(
        username=f"bob_{tenant.schema_name}",
        defaults={"email": f"bob@{tenant.schema_name}.com"}
    )
    bob.set_password("pass123")
    bob.save()

    # Create documents
    docs = [
        ("Q4 Financial Report", "Confidential revenue data...", "draft", alice),
        ("Employee Handbook", "Company policies and procedures.", "published", alice),
        ("Product Roadmap", "Features planned for H1 2026.", "review", bob),
        ("Meeting Notes - Board", "Discussed expansion plans.", "archived", alice),
    ]
    for title, content, status, creator in docs:
        Document.objects.get_or_create(
            title=title, created_by=creator,
            defaults={"content": content, "status": status}
        )

    count = Document.objects.count()
    print(f"  [{tenant.schema_name}] {tenant.name}: {User.objects.count()} users, {count} documents")

# Seed each tenant (skip public)
for tenant in Client.objects.exclude(schema_name='public'):
    seed_tenant(tenant)

# Reset connection to public schema
connection.set_schema_to_public()

print("\nDone.  Credentials: username=alice_<schema>, password=pass123")
print("Each tenant's data is in its own PostgreSQL schema — completely isolated.")
