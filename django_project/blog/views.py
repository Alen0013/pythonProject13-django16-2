from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Pet, Pedigree, Review
from .forms import PetForm, ReviewForm
from datetime import timedelta
from django.utils import timezone
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.conf import settings
from django.core.mail import send_mail

PedigreeFormSet = inlineformset_factory(
    Pet, Pedigree, fields=('parent_type', 'parent_name', 'breed', 'birth_date', 'description'),
    extra=2, max_num=2, can_delete=True
)


class PetListView(ListView):
    model = Pet
    template_name = 'blog/pet_list.html'
    context_object_name = 'pets'
    paginate_by = 5  # Пагинация: 5 записей на страницу для каждого списка

    def get_queryset(self):
        queryset = super().get_queryset()
        # Базовая фильтрация для неадминистраторов и не модераторов
        if not (self.request.user.is_authenticated and self.request.user.role in ['admin', 'moderator']):
            queryset = queryset.filter(is_active=True)

        # Применяем фильтры
        name_filter = self.request.GET.get('name', '')
        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)

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
        # Получаем все питомцев для фильтрации
        base_queryset = self.get_queryset()

        # Разделяем на активных и неактивных
        active_pets = base_queryset.filter(is_active=True)
        inactive_pets = base_queryset.filter(is_active=False)

        # Пагинация для активных питомцев
        paginator_active = self.get_paginator(active_pets, self.paginate_by, orphans=self.get_paginate_orphans(),
                                              allow_empty_first_page=self.get_allow_empty())
        page_number_active = self.request.GET.get('page_active', 1)
        page_obj_active = paginator_active.get_page(page_number_active)
        context['active_pets'] = page_obj_active
        context['is_paginated_active'] = page_obj_active.has_other_pages()

        # Пагинация для неактивных питомцев
        paginator_inactive = self.get_paginator(inactive_pets, self.paginate_by, orphans=self.get_paginate_orphans(),
                                                allow_empty_first_page=self.get_allow_empty())
        page_number_inactive = self.request.GET.get('page_inactive', 1)
        page_obj_inactive = paginator_inactive.get_page(page_number_inactive)
        context['inactive_pets'] = page_obj_inactive
        context['is_paginated_inactive'] = page_obj_inactive.has_other_pages()

        # Передаём фильтры в контекст
        context['name_filter'] = self.request.GET.get('name', '')
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

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.is_authenticated and obj.owner != self.request.user:
            obj.view_count += 1
            if obj.view_count % 100 == 0 and obj.owner:
                send_mail(
                    'Достигнуто 100 просмотров!',
                    f'Ваш питомец {obj.name} набрал {obj.view_count} просмотров.',
                    settings.EMAIL_HOST_USER,
                    [obj.owner.email],
                    fail_silently=True,
                )
            obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        if self.request.user.is_authenticated and self.request.user != self.object.owner:
            context['review_form'] = ReviewForm()
        return context


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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.role not in ['admin', 'moderator']:
            for field in ['is_active', 'owner', 'view_count']:
                form.fields[field].widget = form.fields[field].hidden_widget()
                form.fields[field].required = False
        return form


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


class PetToggleActiveView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pet
    fields = ['is_active']
    template_name = 'blog/pet_confirm_toggle_active.html'
    context_object_name = 'pet'

    def test_func(self):
        return self.request.user.role in ['admin', 'moderator']

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для изменения статуса активности!')
        return redirect('blog:pet_list')

    def form_valid(self, form):
        pet = self.get_object()
        pet.is_active = not pet.is_active
        pet.moderated_by = self.request.user
        pet.save()
        if pet.is_active:
            messages.success(self.request, f'Питомец {pet.name} активирован!')
        else:
            messages.success(self.request, f'Питомец {pet.name} деактивирован!')
        return redirect('blog:pet_list')

    def get_success_url(self):
        return reverse_lazy('blog:pet_list')


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'blog/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = Pet.objects.get(pk=self.kwargs['pet_pk'])
        context['pet'] = pet
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pet_id = self.kwargs['pet_pk']
        messages.success(self.request, 'Отзыв успешно добавлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:pet_detail', kwargs={'pk': self.kwargs['pet_pk']})


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'blog/review_detail.html'
    context_object_name = 'review'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet'] = self.object.pet
        return context
