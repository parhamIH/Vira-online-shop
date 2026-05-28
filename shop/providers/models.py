import uuid
from django.db import models
from django.contrib.auth.models import User

#__________________________________________ ------Provider------ _______________________________________
class Provider(models.Model):
    class ProviderType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        COMPANY = "company", "Company"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name="provider_profile", help_text="Main account owner of the provider")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    provider_type = models.CharField(max_length=20, choices=ProviderType.choices, default=ProviderType.COMPANY,)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING,)

    company_name = models.CharField(unique=True, max_length=255, help_text="Display name of the provider")

    legal_name = models.CharField(max_length=255, blank=True, null=True, help_text="Registered/legal company name")

    national_id = models.CharField(max_length=20, blank=True, null=True, unique=True, help_text="National ID for individual/company")

    registration_number = models.CharField(max_length=50 ,blank=True, null=True, unique=True, help_text="Company registration number")

    economic_code = models.CharField(max_length=20, blank=True, null=True, unique=True, help_text="Economic code")

    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="phone_number")
    is_phone_verified = models.BooleanField(default=False, verbose_name="is_phone_verified")
    verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name="verification_code")
    verification_code_created_at = models.DateTimeField(null=True, blank=True, verbose_name="verification_code_created_at")

    email = models.EmailField(unique=True)

    website = models.URLField(blank=True, null=True)
    #craet new mode for address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    sheba = models.CharField(max_length=34, blank=True, null=True, unique=True, help_text="IBAN / Sheba number")

    bank_account_number = models.CharField(max_length=50, blank=True, null=True)

    logo = models.ImageField(upload_to="providers/logos/", blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Commission percentage" )

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"
        ordering = ["-created_at"]
        permissions = [
            ("verify_provider", "Can verify provider"),
        ]
    def __str__(self):
        return self.company_name


class ProviderMember(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="members")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="provider_memberships")

    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "user"],
                name="unique_provider_user_membership"
            )
        ]

    def __str__(self):
        return f"{self.user} in {self.provider}"
