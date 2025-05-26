from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PetListView.as_view(), name='pet_list'),
    path('pet/<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),
    path('pet/create/', views.PetCreateView.as_view(), name='pet_create'),
    path('pet/<int:pk>/update/', views.PetUpdateView.as_view(), name='pet_update'),
    path('pet/<int:pk>/delete/', views.PetDeleteView.as_view(), name='pet_delete'),
    path('pet/<int:pk>/toggle-active/', views.PetToggleActiveView.as_view(), name='pet_toggle_active'),
    path('pet/<int:pet_pk>/review/', views.ReviewCreateView.as_view(), name='review_create'),
]
