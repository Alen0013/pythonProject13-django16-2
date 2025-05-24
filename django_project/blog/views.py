from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Pet, Pedigree
from .forms import PetForm
from datetime import timedelta
from django.utils import timezone
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.conf import settings

# Создаём formset для родословной
PedigreeFormSet = inlineformset_factory(
    Pet, Pedigree, fields=('parent_type', 'parent_name', 'breed', 'birth_date', 'description'),
    extra=2, max_num=2, can_delete=True
)


@method_decorator(cache_page(settings.CACHE_TTL), name='dispatch')
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


@method_decorator(cache_page(settings.CACHE_TTL), name='dispatch')
class PetDetailView(DetailView):
    model = Pet
    template_name = 'blog/pet_detail.html'
    context_object_name = 'pet'


class PetCreateView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = PetForm
    template_name = 'blog/pet_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.object)
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']
        if pedigree_formset.is_valid():
            self.object = form.save()
            pedigree_formset.instance = self.object
            pedigree_formset.save()
            messages.success(self.request, 'Питомец и родословная успешно добавлены!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('blog:pet_list')


class PetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pet
    form_class = PetForm
    template_name = 'blog/pet_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.get_object())
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.get_object())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']
        if pedigree_formset.is_valid():
            self.object = form.save()
            pedigree_formset.instance = self.object
            pedigree_formset.save()
            messages.success(self.request, 'Питомец и родословная успешно обновлены!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def test_func(self):
        pet = self.get_object()
        return self.request.user == pet.owner or self.request.user.role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, 'Вы не можете редактировать этого питомца!')
        return redirect('blog:pet_list')

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
