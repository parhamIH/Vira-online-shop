
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from model_utils import FieldTracker


class Comment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"

    # نویسنده کامنت
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="کاربر"
    )

    # محصولی که درباره آن نظر داده شده
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="محصول"
    )

    # پاسخ به یک کامنت دیگر
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="پاسخ به"
    )

    # محتوای کامنت
    text = models.TextField(
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(2000),
        ],
        verbose_name="متن نظر"
    )

    # امتیاز فقط برای نظر اصلی محصول
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name="امتیاز"
    )

    # وضعیت بررسی کامنت
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="وضعیت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ثبت"
    )

    tracker = FieldTracker()

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["product", "status", "created_at"],
                name="reviews_prod_status_idx"
            ),
            models.Index(
                fields=["user", "created_at"],
                name="reviews_user_created_idx"
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        # محتوای خالی یا فقط شامل فاصله مجاز نیست
        if not self.text or not self.text.strip():
            errors["text"] = "متن نظر نمی‌تواند خالی باشد."

        if self.parent_id:

            # جلوگیری از پاسخ دادن به خودش
            if self.pk and self.parent_id == self.pk:
                errors["parent"] = "یک کامنت نمی‌تواند والد خودش باشد."

            # پاسخ باید متعلق به همان محصول باشد
            if (
                self.product_id
                and self.parent.product_id != self.product_id
            ):
                errors["parent"] = (
                    "پاسخ و کامنت اصلی باید متعلق به یک محصول باشند."
                )

            # پاسخ نباید امتیاز داشته باشد
            if self.rating is not None:
                errors["rating"] = (
                    "پاسخ به کامنت نمی‌تواند امتیاز داشته باشد."
                )

        else:
            # نظر اصلی محصول باید امتیاز داشته باشد
            if self.rating is None:
                errors["rating"] = (
                    "برای ثبت نظر محصول، امتیاز الزامی است."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.user.get_username()} - "
            f"{self.product.name} - "
            f"{self.rating or '-'} ★"
        )
