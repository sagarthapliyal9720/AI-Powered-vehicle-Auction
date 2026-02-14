from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Car(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    )
    VEHICLE_TYPE = (
    ('2_wheeler', '2 Wheeler'),
    ('4_wheeler', '4 Wheeler'),
)


    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cars"
    )

    title = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)

    year = models.PositiveIntegerField()

    description = models.TextField()

    base_price = models.PositiveBigIntegerField()

    auction_start = models.DateTimeField()
    auction_end = models.DateTimeField()

    image = models.ImageField(upload_to='cars/', null=True, blank=True)
    type = models.CharField(
    max_length=20,
    choices=VEHICLE_TYPE,
    default='4_wheeler'
)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    winner = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="won_cars"
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.brand} {self.model_name})"


class Bid(models.Model):

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    bidder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    amount = models.PositiveBigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']

    def __str__(self):
        return f"{self.bidder.username} - ₹{self.amount}"


class Watchlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watchlist"
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="watchlisted_by"
    )

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.car.title}"
