"""Verify tenant data isolation — the whole point of multi-tenancy."""

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/home/tony/code/multi-tenant-demo')
import django; django.setup()

from tenants.models import Client
from django.db import connection
from documents.models import Document

print("=" * 60)
print("VERIFYING TENANT DATA ISOLATION")
print("=" * 60)

for tenant in Client.objects.exclude(schema_name='public'):
    connection.set_schema(tenant.schema_name)
    docs = list(Document.objects.values_list('title', flat=True))
    print(f"\n[{tenant.schema_name}] {tenant.name}")
    print(f"  Documents: {docs}")

# Cross-contamination check:
# Create a unique document in acme, then verify it's invisible to initech
connection.set_schema('acme_corp')
Document.objects.create(title="UNIQUE_ACME_ONLY", content="should not leak")
acme_ids = set(Document.objects.values_list('id', flat=True))

connection.set_schema('initech')
initech_has_leak = Document.objects.filter(title="UNIQUE_ACME_ONLY").exists()

connection.set_schema('acme_corp')
Document.objects.filter(title="UNIQUE_ACME_ONLY").delete()  # cleanup

print("\n" + "=" * 60)
if initech_has_leak:
    print("FAIL: Data leak detected — Initech can see Acme's document!")
else:
    print("PASS: Initech cannot see Acme's document. Tenant isolation works.")

# Show Postgres schemas
from django.db import connections
with connections['default'].cursor() as c:
    c.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema' ORDER BY schema_name")
    schemas = [row[0] for row in c.fetchall()]
    print(f"\nPostgreSQL schemas: {schemas}")
