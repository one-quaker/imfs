import os
import shutil
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.conf import settings
from django.http import HttpResponseRedirect
from sorl.thumbnail import get_thumbnail


from .models import Photo, Wallet, WalletConfig
from .utils import random_string, path_and_rename, rm_file, rm_dir, mk_dir


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

        self.remove_local_data()

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

    def remove_local_data(self):
        Photo.objects.all().delete()
        rm_dir(settings.USER_TMP_ROOT)
        mk_dir(settings.USER_TMP_ROOT)

    def save_user_data(self, data):
        if not data:
            return

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
        self.save_user_file(obj.file.path)
        return HttpResponseRedirect(reverse('add-photo'))

    def save_user_file(self, fp):
        from imfs_io.eos_imfs import EosFile, EosDir

        fext = fp.split('.')[-1]
        fname = '{}.{}'.format(random_string(), fext)

        user_wallet = Wallet.objects.first()
        wallet_config = WalletConfig.objects.first()

        tmp_fp = os.path.join(settings.USER_TMP_ROOT, fname)
        resized_im = get_thumbnail(fp, '300x200', crop='center', quality=50)

        with open(tmp_fp, 'wb') as f:
            f.write(resized_im.read())

        file_1 = EosFile(user_wallet.address, settings.USER_TMP_ROOT, fname, wallet_config.address, wallet_config.private_key)

        try:
            file_1.put_file()
        except Exception as e:
            print(e)

        rm_file(tmp_fp)


class SetWalletView(generic.edit.CreateView):
    template_name = 'set_wallet.html'
    model = Wallet
    fields = ['address', ]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return HttpResponseRedirect(reverse('update-user-data'))
