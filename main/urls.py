from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),

    # URLs для материальных узлов (основная рабочая таблица)
    path('material-parts/', views.material_parts_list, name='material_parts_list'),
    path('material-parts/<int:part_id>/', views.material_part_detail, name='material_part_detail'),
    path('material-parts/<int:part_id>/edit/', views.material_part_edit, name='material_part_edit'),
    path('material-parts/create/', views.material_part_create, name='material_part_create'),
    path('material-parts/<int:part_id>/delete/', views.material_part_delete, name='material_part_delete'),

    # URLs для операций (журнал)
    path('operations/', views.operations_list, name='operations_list'),
    path('operations/<int:operation_id>/', views.operation_detail, name='operation_detail'),
    path('operations/<int:operation_id>/edit/', views.operation_edit, name='operation_edit'),
    path('operations/create/', views.operation_create, name='operation_create'),
    path('operations/<int:operation_id>/delete/', views.operation_delete, name='operation_delete'),

    # URLs для астральных ревизий
    path('astral-revisions/', views.astral_revisions_list, name='astral_revisions_list'),
    path('astral-revisions/<int:revision_id>/', views.astral_revision_detail, name='astral_revision_detail'),
    path('astral-revisions/<int:revision_id>/edit/', views.astral_revision_edit, name='astral_revision_edit'),
    path('astral-revisions/create/', views.astral_revision_create, name='astral_revision_create'),
    path('astral-revisions/<int:revision_id>/delete/', views.astral_revision_delete, name='astral_revision_delete'),

    # URLs для астральных узлов
    path('astral-parts/', views.astral_parts_list, name='astral_parts_list'),
    path('astral-parts/<int:part_id>/', views.astral_part_detail, name='astral_part_detail'),
    path('astral-parts/create/', views.astral_part_create, name='astral_part_create'),
    path('astral-parts/<int:part_id>/edit/', views.astral_part_edit, name='astral_part_edit'),
]
