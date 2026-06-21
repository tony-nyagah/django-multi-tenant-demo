"""Create tenants via Django ORM (non-interactive)."""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/home/tony/code/multi-tenant-demo')

django.setup()

from tenants.models import Client, Domain

# Public tenant
public, _ = Client.objects.get_or_create(
    schema_name='public',
    defaults={'name': 'Public Tenant', 'description': 'Main public schema'}
)
Domain.objects.get_or_create(tenant=public, domain='localhost')

# Test tenants
tenants = [
    ('Acme Corp', 'acme.localhost'),
    ('Globex Inc', 'globex.localhost'),
    ('Initech', 'initech.localhost'),
]

for org_name, domain in tenants:
    tenant, created = Client.objects.get_or_create(
        schema_name=org_name.lower().replace(' ', '_').replace('.', ''),
        defaults={'name': org_name, 'description': f'{org_name} document space'}
    )
    Domain.objects.get_or_create(tenant=tenant, domain=domain)
    status = 'CREATED' if created else 'EXISTED'
    print(f"{status}: {tenant.name} (schema: {tenant.schema_name})")

print("\nAll tenants:")
for t in Client.objects.all():
    domains = ', '.join(d.domain for d in t.domains.all())
    print(f"  [{t.schema_name}] {t.name} -> {domains}")
