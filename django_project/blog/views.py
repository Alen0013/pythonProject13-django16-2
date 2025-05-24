from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Pet
from .forms import PetForm
from datetime import timedelta
from django.utils import timezone


class PetListView(ListView):
    model = Pet
    template_name = 'blog/pet_list.html'
    context_object_name = 'pets'

    def get_queryset(self):
        queryset = super().get_queryset()
        species_filter = self.request.GET.get('species', '')
        if species_filter:
            queryset = queryset.filter(species=species_filter)

        age_min = self.request.GET.get('age_min', '')
        age_max = self.request.GET.get('age_max', '')
        if age_min and age_min.isdigit():
            queryset = queryset.filter(age__gte=int(age_min))
        if age_max and age_max.isdigit():
            queryset = queryset.filter(age__lte=int(age_max))

        owner_filter = self.request.GET.get('owner', '')
        if owner_filter and self.request.user.is_authenticated and self.request.user.role == 'admin':
            queryset = queryset.filter(owner__email__icontains=owner_filter)

        created_at_filter = self.request.GET.get('created_at', '')
        if created_at_filter == 'last_month':
            one_month_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=one_month_ago)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['species_filter'] = self.request.GET.get('species', '')
        context['age_min'] = self.request.GET.get('age_min', '')
        context['age_max'] = self.request.GET.get('age_max', '')
        context['owner_filter'] = self.request.GET.get('owner',
                                                       '') if self.request.user.is_authenticated and self.request.user.role == 'admin' else ''
        context['created_at_filter'] = self.request.GET.get('created_at', '')
        context['species_choices'] = Pet.SPECIES_CHOICES
        return context


class PetDetailView(DetailView):
    model = Pet
    template_name = 'blog/pet_detail.html'
    context_object_name = 'pet'


class PetCreateView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = PetForm
    template_name = 'blog/pet_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Питомец успешно добавлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:pet_list')


class PetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pet
    form_class = PetForm
    template_name = 'blog/pet_form.html'

    def test_func(self):
        pet = self.get_object()
        return self.request.user == pet.owner or self.request.user.role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, 'Вы не можете редактировать этого питомца!')
        return redirect('blog:pet_list')

    def form_valid(self, form):
        messages.success(self.request, 'Питомец успешно обновлён!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:pet_list')


class PetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pet
    template_name = 'blog/pet_confirm_delete.html'
    context_object_name = 'pet'

    def test_func(self):
        pet = self.get_object()
        return self.request.user == pet.owner or self.request.user.role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, 'Вы не можете удалить этого питомца!')
        return redirect('blog:pet_list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Питомец успешно удалён!')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:pet_list')
