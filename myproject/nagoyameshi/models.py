from django.db import models

# レストラン登録のモデル作成
class Restaurant(models.Model):
  name = models.CharField(max_length=200)
  price = models.PositiveIntegerField()
  description = models.TextField()
  postal_code = models.CharField(max_length=10)
  address = models.CharField(max_length=200)
  phone_number = models.CharField(max_length=15)
  open_time = models.TimeField()
  close_time = models.TimeField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.TimeField(auto_now=True)
  img = models.ImageField(upload_to='restaurant_images/')

  def __str__(self):
         return self.name