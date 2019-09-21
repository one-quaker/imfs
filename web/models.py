from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import os


class CreatedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def human_date(self):
        return self.created_at.strftime('%d/%B/%Y - %H:%M')

    class Meta:
        abstract = True


class Photo(CreatedMixin):
    file = models.ImageField(upload_to='photo', max_length=255)
    dir = models.CharField(max_length=64, default='main')

    def __str__(self):
        return self.file.name

    @property
    def file_name(self):
        return os.path.basename(self.file.name)


class Wallet(CreatedMixin):
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address


@receiver(post_save, sender=Photo)
def process_photo(sender, instance, *args, **kwargs):
    import os
    cmd = 'cp -fv {fp} {root}/tmp/{fn}'.format(fp=instance.file.path, root=settings.BASE_DIR, fn=instance.file_name)
    print(cmd)
    os.system(cmd)


@receiver(pre_save, sender=Wallet)
def singletone_wallet(sender, instance, *args, **kwargs):
    Wallet.objects.all().delete()
