from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.conf import settings
from django.http import HttpResponseRedirect
import os


from .models import Photo, Wallet, WalletConfig


class IndexView(generic.ListView):
    template_name = 'index.html'
    model = Photo
    queryset = Photo.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


class UpdateUserDataView(generic.base.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'index-page'

    def get_redirect_url(self, *args, **kwargs):
        self.get_user_data()
        return super().get_redirect_url(*args, **kwargs)

    def get_user_data(self):
        from imfs_io.eos_imfs import EosFile, EosDir

        user_wallet = Wallet.objects.first()
        wallet_config = WalletConfig.objects.first()

        dir_1 = EosDir(user_wallet.address, settings.USER_TMP_ROOT, wallet_config.address, wallet_config.private_key)
        out = dir_1.get_dir()
        print(dir_1, out)

        allowed_file_list = [
            '{}/{}'.format(settings.USER_TMP_NAME, x)
            for x in os.listdir(settings.USER_TMP_ROOT)
            if x.lower().split('.')[-1] in ('jpg', 'jpeg', 'png')
        ]

        print(allowed_file_list)
        self.save_user_data(allowed_file_list)

    def save_user_data(self, data):
        if not data:
            return
        Photo.objects.all().delete()
        for fp in data:
            photo = Photo(file=fp)
            photo.save()


class AddPhotoView(generic.edit.CreateView):
    template_name = 'add_photo.html'
    model = Photo
    fields = ['file', 'dir']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return HttpResponseRedirect(reverse('add-photo'))


class SetWalletView(generic.edit.CreateView):
    template_name = 'set_wallet.html'
    model = Wallet
    fields = ['address', ]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return HttpResponseRedirect(reverse('set-wallet'))
