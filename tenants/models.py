"""
Tenant model — each Client is a tenant that gets its own PostgreSQL schema.

The schema_name becomes the PostgreSQL schema name.  django-tenants
automatically creates the schema when a tenant is saved and drops it
when deleted.
"""

from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    # TenantMixin already provides:
    #   schema_name  — the PostgreSQL schema (auto-set from name)
    #   paid_until   — optional billing field
    #   on_trial     — optional trial flag
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """Domain routing — maps subdomain to tenant."""

    class Meta:
        ordering = ["domain"]

    def __str__(self):
        return self.domain
