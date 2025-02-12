from django.db import models
from store.models import Product
from userauth.models import User


TYPE=(
    ("New Order","New Order"),
    ("Item Shipped","Item shipped"),
    ("Item delived","Item derived"),
)

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="wishlist")
    
    class Meta:
        verbose_name_plural="wishlists"
        
    def __str__(self):
        if self.product.name:
            return self.product.name
        else:
            return "wishlist"
        
class Adress(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    full_name=models.CharField(max_length=200,null=True,blank=True,default=None)
    mobile=models.CharField(max_length=50,null=True,blank=True,default=None)
    email=models.EmailField(max_length=100,null=True,blank=True,default=None)
    country=models.CharField(max_length=100,null=True,blank=True,default=None)
    state=models.CharField(max_length=100,null=True,blank=True,default=None)
    city=models.CharField(max_length=100,null=True,blank=True,default=None)
    address=models.CharField(max_length=100,null=True,blank=True,default=None)
    zip_code=models.CharField(max_length=50,null=True,blank=True,default=None)
    class Meta:
        verbose_name_plural="customer Addresses"
        
    def __str__(self):
        return self.full_name
class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True, related_name='+')
    type=models.CharField(max_length=100,choices=TYPE,default=None)
    seen=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural="Notifications"
    def __str__(self):
        return self.type