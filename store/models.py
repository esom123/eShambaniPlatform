from django.db import models

# Create your models here.
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from userauth.models import User

import shortuuid 

STATUS=(
    ("published","published"),
    ("Draft","Draft"),
    ("Disabled","Disabled"),
)

PAYMENT_STATUS=(
    ("paid","paid"),
    ("processing","processing"),
    ("Failed","Failed"),
)

PAYMENT_METHOD=(
    ("paypal","paypal"),
    ("stripe","stripe"),
    ("flutterwave","flutterwave"),
    ("paystack","paystack"),
    ("Razopay","Razorpay"),
)

ORDER_STATUS=(
    ("pending","pending"),
    ("processing","processing"),
    ("shipped","shipped"),
    ("fulfilled","fulfiled"),
    ("cancelled","cancelled"),
)

SHIPPING_SERVICE=(
    ("DHL","DHL"),
    ("Fedx","Fedx"),
    ("ups","ups"),
    ("GIG Logistics","GIG Logistics"),
)

RATING=(
    (1,"⭐️☆☆☆☆"),
    (2,"⭐️⭐️☆☆☆"),
    (3,"⭐️⭐️⭐️☆☆"),
    (4,"⭐️⭐️⭐️⭐️☆"),
    (5,"⭐️⭐️⭐️⭐️⭐️"),  
)


class Category(models.Model):
    title=models.CharField(max_length=255)
    image=models.ImageField(upload_to="image" )
    slug=models.SlugField(unique=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural="categories"
        ordering=['title']


class Product(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="images", blank=True, null=True, default="product.jpg")
    description = CKEditor5Field('Text', config_name='extend')
    category = models.ForeignKey(Category, max_length=255, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="sales price")
    regular_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="regular price")
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="shipping price")
    status = models.CharField(choices=STATUS, max_length=50, default="published")
    featured = models.BooleanField(default=False, verbose_name="marketplace is featured")
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sku = ShortUUIDField(unique=True, length=5, max_length=50, prefix="sku", alphabet="1234567890")
    slug = models.SlugField(null=True, blank=True, unique=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "products"

    def __str__(self):
        return self.name if self.name else f"Product {self.id}"

     
    def average_rating(self):
        return Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))['avg_rating']
    def reviews(self):
        return Review.objects.filter(product=self)
    def gallery(self):
        return Gallery.objects.filter(product=self)
    def variants(self):
        return Variant.objects.filter(product=self)
    def vendor_orders(self):
        return OrderItem.objects.filter(vendor=self.vendor)
    def save(self, *args, **kwargs):
        # Ensure the slug is generated only if it is empty
        if not self.slug and self.name:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
        
        # Always save the product instance
        super(Product, self).save(*args, **kwargs)

class Variant(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    name=models.CharField(max_length=1000, verbose_name="Variants Name",null=True,blank=True)
    def items(self):
        return VariantItem.objects.filter(variants=self)
    def __str__(self):
        return self.name
    
class VariantItem(models.Model):
    variant=models.ForeignKey(Variant,on_delete=models.CASCADE,related_name="items")
    title=models.CharField(max_length=1000,verbose_name="Item Title",null=True,blank=True)
    content=models.CharField(max_length=1000,verbose_name="item content",null=True,blank=True)
    
    
    def __str__(self):
        return self.variant.name
class Gallery(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    image=models.FileField(upload_to="images",default="gallery.jpg")
    gallery_id=ShortUUIDField(length=6,max_length=10,alphabet="1234567890")
    
    def __str__(self):
        return f"{self.product.name}.image"

class Cart(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    qty=models.PositiveIntegerField(default=0,null=True,blank=True)
    price=models.DecimalField(decimal_places=2,max_digits=12,default=0.00,null=True,blank=True)
    sub_total=models.DecimalField(decimal_places=2,max_digits=12,default=0.00,null=True,blank=True)
    shipping=models.DecimalField(decimal_places=2,max_digits=12,default=0.00,null=True,blank=True)
    tax=models.DecimalField(decimal_places=2,max_digits=12,default=0.00,null=True,blank=True)
    total=models.DecimalField(decimal_places=2,max_digits=12,default=0.00,null=True,blank=True)
    size=models.CharField(max_length=100,null=True,blank=True)
    color=models.CharField(max_length=100,null=True,blank=True)
    cart_id=models.CharField(max_length=1000,null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cart_id}.{self.product.name}"
    
class Coupon(models.Model):
    vendor=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    code=models.CharField(max_length=100)
    discount=models.IntegerField(default=1)
    
    def __str__(self):
        return self.code

class Order(models.Model):
    vendors=models.ManyToManyField(User,blank=True)
    customer=models.ForeignKey(User,on_delete=models.SET_NULL,related_name="customer",null=True,blank=True)
    sub_total=models.DecimalField(default=0.00,max_digits=12 ,decimal_places=2)
    shipping=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    tax=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    service_free=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    total=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    payment_status=models.CharField(max_length=100,choices=PAYMENT_STATUS,default="processing")
    payment_method=models.CharField(max_length=100, choices=PAYMENT_METHOD,null=True,blank=True)
    order_status=models.CharField(max_length=100, choices=ORDER_STATUS, default="pending")
    initial_total=models.DecimalField(default=0.00,max_digits=12,decimal_places=2,help_text="The original total benefit")
    saved=models.DecimalField(max_digits=12,decimal_places=2,default=0.00,null=True,blank=True,help_text="Amount of ")
    # address=models.ForeignKey("customer.Address",on_delete=models.SET_NULL,NULL=True)
    coupons=models.ManyToManyField(Coupon,blank=True)
    order_id=ShortUUIDField(length=6,max_length=25,alphabet="1234567890")
    payment_id=models.CharField(null=True,blank=True,max_length=1000)
    date=models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering=['-date']
        verbose_name_plural="Orders"
        
    def __str__(self):
        return self.order_id
    
    def order_items(self):
        return OrderItem.objects.filter(order=self)
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    order_status=models.CharField(max_length=100, choices=ORDER_STATUS, default="pending")
    shipping_service=models.CharField(max_length=100,choices=SHIPPING_SERVICE,default=None,null=True,blank=True)
    tracking_id=models.CharField(max_length=100,default=None,null=True,blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    qty=models.IntegerField(default=0)
    color=models.CharField(max_length=100,null=True,blank=True)
    size=models.CharField(max_length=100,null=True,blank=True)
    price=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    sub_total=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    shipping=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    tax=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    total=models.DecimalField(decimal_places=2,max_digits=12,default=0.00)
    initial_total=models.DecimalField(default=0.00,max_digits=12,decimal_places=2,help_text="The original total benefit")
    saved=models.DecimalField(max_digits=12,decimal_places=2,default=0.00,null=True,blank=True,help_text="Amount of ")
    coupon=models.ManyToManyField(Coupon,blank=True)
    applied_coupon=models.BooleanField(default=False)
    item_id=ShortUUIDField(length=6,max_length=25,alphabet="1234567890")
    vendor=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="vendor_order_items")
    date=models.DateTimeField(default=timezone.now)
    
    def order_id(self):
        return f"{self.Order.order_id}"
    def __str__(self):
        return self.item_id
    class Meta:
        ordering=['-date']
        
class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True,related_name="reviews")
    review=models.TextField(null=True,blank=True)
    reply=models.TextField(null=True,blank=True)
    rating=models.IntegerField(choices=RATING,default=None)
    active=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} review on { self.product.name}" 