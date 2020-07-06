from hashlib import sha256

from django.db import models


class URLShortener(models.Model):
    shortHash = models.CharField(unique=True, max_length=15)
    urlSuffix = models.CharField(unique=True, max_length=1000)
    dateCreated = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.shortHash = sha256(self.urlSuffix.encode()).hexdigest()[:15]

        return super().save(*args, **kwargs)

    class Meta:
        db_table = "courses_shortener"
        verbose_name = "Short URL"
        verbose_name_plural = "Short URLs"
