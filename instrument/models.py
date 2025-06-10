from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Instruments(models.Model):
    name = models.CharField(max_length=100, default="")
    group = models.CharField(max_length=30, default="")
    type = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")
    country = models.CharField(max_length=30, default="")
    archive = models.BooleanField(default=False)
    api_support = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", null=True, blank=True, default=None)

    def is_system_instrument(self):
        return self.user is None  # No user = system-maintained

    def clean(self):
        # Ha user nem None, tehát nem rendszer által fenntartott
        if self.user:
            # Ne lehessen duplikált nevű rendszer instrumentum
            system_duplicate = Instruments.objects.filter(
                name=self.name, user__isnull=True
            ).exists()
            if system_duplicate:
                raise ValidationError("This instrument already exists in the system.")

            # Ne lehessen saját név duplikáció
            user_duplicate = Instruments.objects.filter(
                name=self.name, user=self.user
            )
            if self.pk:
                user_duplicate = user_duplicate.exclude(pk=self.pk)
            if user_duplicate.exists():
                raise ValidationError("You already created an instrument with this name.")

            # Ne lehessen olyan group+type kombináció, ami a rendszer által fenntartott
            group_type_exists = Instruments.objects.filter(
                group=self.group,
                type=self.type,
                user__isnull=True
            ).exists()
            if group_type_exists:
                raise ValidationError(
                    "You cannot create an instrument with this group and type, it already exists in the system.")

        else:
            # Ha rendszer/admin instrumentum, ne legyen teljes duplikátum
            system_duplicate = Instruments.objects.filter(
                name=self.name,
                group=self.group,
                type=self.type,
                currency=self.currency,
                user__isnull=True
            )
            if self.pk:
                system_duplicate = system_duplicate.exclude(pk=self.pk)
            if system_duplicate.exists():
                raise ValidationError("A system instrument with these attributes already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Prices(models.Model):
    instrument = models.ForeignKey(Instruments, on_delete=models.CASCADE, null=True)
    price = models.FloatField(default=0.0)
    source = models.CharField(max_length=30, default="")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class Tickers(models.Model):
    inst_code = models.ForeignKey(Instruments, on_delete=models.CASCADE, db_column="inst_code", null=True, blank=True, default=None)
    source_ticker = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")
    margin = models.FloatField(default=0.0)