from django.urls import path
from .views import *

urlpatterns = [
    path('machines/list/', Machines.as_view(), name='machines'),
    path('machines/<int:pk>/', MachineDetail.as_view(), name='retrive_machine'),
    path('machines/<str:city>/', MachinesByCity.as_view(), name='retrive_machine_by_city'),
    path('machines/delete/<int:pk>/', MachineDelete.as_view(), name='delete_machine'),
    path('machines/qrcode/<str:name>/', MachineQRCode.as_view(), name='retrive_qrcode'),

    path('machines/recycle/update/<str:name>/', UpdateRecycle.as_view(), name='update_recycle'),

    path('recyclelog/user/<int:pk>/', RetrieveRecycleLog.as_view(), name='recycle_log'),


]