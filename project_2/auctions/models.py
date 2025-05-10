from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Auction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=35)
    description = models.TextField()
    current_bid = models.ForeignKey('Bid', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home', 'Home & Garden'),
        ('toys', 'Toys'),
        ('books', 'Books'),
        ('other', 'Other'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', blank=True)

    watchlist = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='watchlist')

    img = models.ImageField(default="default.png", blank=True)

    def __str__(self):
        return self.title



class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bid_amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{str(self.bid_amount)} by {self.user}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.auction}"