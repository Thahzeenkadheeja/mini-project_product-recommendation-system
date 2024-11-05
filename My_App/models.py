from django.db import models

class LoginTable(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    type = models.CharField(max_length=15)

class SellerTable(models.Model):
    LOGIN_ID = models.ForeignKey(LoginTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    place = models.CharField(max_length=30)
    phone = models.BigIntegerField()
    email = models.CharField(max_length=30)
    image = models.FileField()
    id_proof = models.FileField()

class ProductTable(models.Model):
    SELLER_ID = models.ForeignKey(SellerTable, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=30)
    Date=models.DateField()
    price = models.IntegerField()
    stock = models.IntegerField()
    image = models.FileField()

class OfferTable(models.Model):
    PRODUCT_ID = models.ForeignKey(ProductTable, on_delete=models.CASCADE)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    offers = models.FloatField()
    date = models.DateField()


class UserTable(models.Model):
    LOGIN_ID = models.ForeignKey(LoginTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    gender = models.CharField(max_length=10)
    image = models.FileField()
    place = models.CharField(max_length=25)
    pin = models.BigIntegerField()
    post = models.CharField(max_length=25)
    phone = models.BigIntegerField()
    email = models.CharField(max_length=30)


class OrderTable(models.Model):
    USER_ID = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.FloatField()
    status = models.CharField(max_length=30)

class OrderDetails(models.Model):
    ORDER_ID = models.ForeignKey(OrderTable, on_delete=models.CASCADE)
    PRODUCT_ID = models.ForeignKey(ProductTable, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)

class FeedbackTable(models.Model):
    ORDERDETAILS = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=200)
    ratings = models.CharField(max_length=50)


class ComplaintTable(models.Model):
    USER_ID = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    complaint = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    reply = models.CharField(max_length=200)


class UserHistoryTable(models.Model):
    USER_ID = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    Keyword = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)


