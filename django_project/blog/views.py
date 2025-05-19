from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pet
from .forms import PetForm


def pet_list(request):
    pets = Pet.objects.all()
    return render(request, 'blog/pet_list.html', {'pets': pets})


@login_required
def pet_create(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user  # Установка текущего пользователя как владельца
            pet.save()
            messages.success(request, 'Питомец успешно добавлен!')
            return redirect('blog:pet_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
    else:
        form = PetForm()
    return render(request, 'blog/pet_form.html', {'form': form, 'title': 'Добавить питомца'})


@login_required
def pet_update(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Питомец успешно обновлен!')
            return redirect('blog:pet_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
    else:
        form = PetForm(instance=pet)
    return render(request, 'blog/pet_form.html', {'form': form, 'title': 'Редактировать питомца'})


@login_required
def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        pet.delete()
        messages.success(request, 'Питомец успешно удален!')
        return redirect('blog:pet_list')
    return render(request, 'blog/pet_confirm_delete.html', {'pet': pet})


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    return render(request, 'blog/pet_detail.html', {'pet': pet})
