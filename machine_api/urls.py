from django.urls import path
from .views import *

urlpatterns = [
    path('list/', Machines.as_view(), name='machines'),
    path('<int:pk>/', MachineDetail.as_view(), name='retrive_machine'),
    path('delete/<int:pk>/', MachineDelete.as_view(), name='delete_machine'),
]