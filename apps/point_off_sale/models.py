# point_off_sale/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('bartender', 'Bartender'),
        ('chef', 'Chef'),
        ('assistant_chef', 'Assistant Chef'),
    ])

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"T{self.number}"

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

class Order(models.Model):
    STATUS = [
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]
    ORDER_TYPE = [
        ('dine_in', 'Dine In'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
    ]
    customer_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nama customer"
    )
    table = models.ForeignKey(Table, on_delete=models.PROTECT, null=True, blank=True)
    guest_count = models.PositiveIntegerField(default=1)
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE, default='dine_in')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='open')

    def __str__(self):
        return f'{self.customer_name} - {self.order_type} - {self.status}'

class OrderItem(models.Model):
    ITEM_STATUS = [
        ('to_cook', 'To Cook'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('done', 'Done'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'   # order.items.all()
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ITEM_STATUS, default='to_cook')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} [{self.status}]"

