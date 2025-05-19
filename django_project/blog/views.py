from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Pet
from .forms import PetForm

def pet_list(request):
    pets = Pet.objects.all()
    return render(request, 'blog/pet_list.html', {'pets': pets})

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
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
    else:
        form = PetForm()
    return render(request, 'blog/pet_form.html', {'form': form})

@login_required
def pet_update(request, pk):
    pet = Pet.objects.get(pk=pk)
    if request.user != pet.owner:
        messages.error(request, 'Вы не можете редактировать этого питомца!')
        return redirect('blog:pet_list')
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Питомец успешно обновлён!')
            return redirect('blog:pet_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
    else:
        form = PetForm(instance=pet)
    return render(request, 'blog/pet_form.html', {'form': form})

@login_required
def pet_delete(request, pk):
    pet = Pet.objects.get(pk=pk)
    if request.user != pet.owner:
        messages.error(request, 'Вы не можете удалить этого питомца!')
        return redirect('blog:pet_list')
    if request.method == 'POST':
        pet.delete()
        messages.success(request, 'Питомец успешно удалён!')
        return redirect('blog:pet_list')
    return render(request, 'blog/pet_confirm_delete.html', {'pet': pet})