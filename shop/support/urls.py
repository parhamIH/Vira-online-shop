from django.urls import path
from . import views



urlpatterns = [
    # ...سایر URL ها
    path('', views.support, name='support'),
    path('ajax/', views.support_ajax, name='support_ajax'),
    path('ticket/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
    path('ticket/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('ticket/<int:ticket_id>/reply/', views.add_reply, name='add_reply'),
    path('admin/', views.admin_tickets, name='admin_tickets'),  # پنل مدیریت تیکت ها
    path('ticket/<int:ticket_id>/status/<str:status>/', views.change_ticket_status, name='change_ticket_status'),  # تغییر وضعیت تیکت
] 