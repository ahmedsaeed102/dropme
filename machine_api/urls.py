from django.urls import path ,include
from .views import *

urlpatterns = [
    path('list', ListMachines.as_view(), name='list_machines'),
    path('list/<str:pk>/', RetrieveMachine.as_view(), name='retrive_machine'),

]