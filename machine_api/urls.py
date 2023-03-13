from django.urls import path
from .views import *

urlpatterns = [
    path('machines/list/', Machines.as_view(), name='machines'),
    path('machines/<int:pk>/', MachineDetail.as_view(), name='retrive_machine'),
    path('machines/delete/<int:pk>/', MachineDelete.as_view(), name='delete_machine'),
    path('machines/qrcode/<str:name>/', MachineQRCode.as_view(), name='retrive_qrcode'),
    path('machines/recycle/start/<str:name>/', StartRecycle.as_view(), name='start_recycle'),
    path('recyclelog/user/<int:pk>/', RetrieveRecycleLog.as_view(), name='recycle_log'),
]