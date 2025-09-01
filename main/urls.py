from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),

    # URLs для устройств
    path('devices/', views.devices_list, name='devices_list'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('devices/<int:device_id>/edit/', views.device_edit, name='device_edit'),
    path('devices/create/', views.device_create, name='device_create'),
    path('devices/<int:device_id>/delete/', views.device_delete, name='device_delete'),

    # URLs для деталей/узлов
    path('parts/', views.parts_list, name='parts_list'),
    path('parts/<int:part_id>/', views.part_detail, name='part_detail'),
    path('parts/<int:part_id>/edit/', views.part_edit, name='part_edit'),
    path('parts/create/', views.part_create, name='part_create'),
    path('parts/<int:part_id>/delete/', views.part_delete, name='part_delete'),

    # URLs для истории операций
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/<int:journal_id>/', views.journal_detail, name='journal_detail'),
    path('journal/<int:journal_id>/edit/', views.journal_edit, name='journal_edit'),
    path('journal/create/', views.journal_create, name='journal_create'),
    path('journal/<int:journal_id>/delete/', views.journal_delete, name='journal_delete'),
]
