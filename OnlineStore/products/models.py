from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Products(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    description=models.TextField(max_length=100)
    price=models.IntegerField()
    stock=models.IntegerField()
    image=models.ImageField(upload_to='products/')
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)


    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
        
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending','pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('cancelled','cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart=models.ManyToManyField(Cart)
    created_at =models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status =models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
class Payment(models.Model):
    PAYMENT_STATUS_CHOICE =[
        ('pending','pending'),
        ('Completed','Completed'),
        ('Failed','Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, choices=[('COD','cash on Delivery'), ('Online','Online Payment')])
    trancation_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICE, default='pending')

    def __str__(self):
        return f'Payment for order{self.order.id} - {self.status}'