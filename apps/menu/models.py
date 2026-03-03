from django.db import models

# Create your models here.
class MenuCategory(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Kategori menu untuk customer, misal: Food, Drinks, Snacks."
    )

    def __str__(self):
        return self.name

class MenuGroup(models.Model):
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.PROTECT,
        related_name='groups'
    )
    name = models.CharField(
        max_length=50,
        help_text="Grup dalam kategori, misal: Ayam, Jeroan, Pasta, Tea, Juice."
    )

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} / {self.name}"

class MenuItem(models.Model):
    PREP_STATION = [
        ('kitchen', 'Kitchen'),    # chef
        ('bar', 'Bar'),            # bartender
    ]

    group = models.ForeignKey(
        MenuGroup,
        on_delete=models.PROTECT,
        related_name='items'
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    prep_station = models.CharField(
        max_length=20,
        choices=PREP_STATION,
        help_text="Kemana item ini dikirim: kitchen (chef) atau bar (bartender)."
    )

    def __str__(self):
        return self.name

    @property
    def category(self):
        return self.group.category