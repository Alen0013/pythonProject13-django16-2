from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PetListView.as_view(), name='pet_list'),
    path('create/', views.PetCreateView.as_view(), name='pet_create'),
    path('<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),
    path('<int:pk>/update/', views.PetUpdateView.as_view(), name='pet_update'),
    path('<int:pk>/delete/', views.PetDeleteView.as_view(), name='pet_delete'),
]
