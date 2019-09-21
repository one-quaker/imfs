from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.conf import settings
from django.http import HttpResponseRedirect


from .models import Photo, Wallet


class IndexView(generic.ListView):
    template_name = 'index.html'
    model = Photo
    queryset = Photo.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


class AddPhotoView(generic.edit.CreateView):
    template_name = 'add_photo.html'
    model = Photo
    fields = ['file', 'dir']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return HttpResponseRedirect(reverse('index-page'))


class SetWalletView(generic.edit.CreateView):
    template_name = 'set_wallet.html'
    model = Wallet
    fields = ['address', ]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        return HttpResponseRedirect(reverse('index-page'))
