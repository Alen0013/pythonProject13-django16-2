from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Pet
from .forms import PetForm
from datetime import timedelta
from django.utils import timezone


def pet_list(request):
    pets = Pet.objects.all()

    species_filter = request.GET.get('species', '')
    if species_filter:
        pets = pets.filter(species=species_filter)

    age_min = request.GET.get('age_min', '')
    age_max = request.GET.get('age_max', '')
    if age_min and age_min.isdigit():
        pets = pets.filter(age__gte=int(age_min))
    if age_max and age_max.isdigit():
        pets = pets.filter(age__lte=int(age_max))

    owner_filter = request.GET.get('owner', '')
    if owner_filter and request.user.is_authenticated and request.user.role == 'admin':
        pets = pets.filter(owner__email__icontains=owner_filter)

    created_at_filter = request.GET.get('created_at', '')
    if created_at_filter == 'last_month':
        one_month_ago = timezone.now() - timedelta(days=30)
        pets = pets.filter(created_at__gte=one_month_ago)

    context = {
        'pets': pets,
        'species_filter': species_filter,
        'age_min': age_min,
        'age_max': age_max,
        'owner_filter': owner_filter if request.user.is_authenticated and request.user.role == 'admin' else '',
        'created_at_filter': created_at_filter,
        'species_choices': Pet.SPECIES_CHOICES,
    }
    return render(request, 'blog/pet_list.html', context)


def pet_detail(request, pk):
    pet = Pet.objects.get(pk=pk)
    return render(request, 'blog/pet_detail.html', {'pet': pet})


@login_required
def pet_create(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, 'Питомец успешно добавлен!')
            return redirect('blog:pet_list')
    else:
        form = PetForm()
    return render(request, 'blog/pet_form.html', {'form': form})


@login_required
def pet_update(request, pk):
    pet = Pet.objects.get(pk=pk)
    if request.user != pet.owner and request.user.role != 'admin':
        messages.error(request, 'Вы не можете редактировать этого питомца!')
        return redirect('blog:pet_list')
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Питомец успешно обновлён!')
            return redirect('blog:pet_list')
    else:
        form = PetForm(instance=pet)
    return render(request, 'blog/pet_form.html', {'form': form})


@login_required
def pet_delete(request, pk):
    pet = Pet.objects.get(pk=pk)
    if request.user != pet.owner and request.user.role != 'admin':
        messages.error(request, 'Вы не можете удалить этого питомца!')
        return redirect('blog:pet_list')
    if request.method == 'POST':
        pet.delete()
        messages.success(request, 'Питомец успешно удалён!')
        return redirect('blog:pet_list')
    return render(request, 'blog/pet_confirm_delete.html', {'pet': pet})
