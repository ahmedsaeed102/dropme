from django.urls import path, register_converter
from . import converts
from .views import *

register_converter(converts.FloatUrlParameterConverter, "float")

crud = [
    path("machines/list/", Machines.as_view(), name="machines"),
    path("machines_page_data/<float:long>/<float:lat>/", MachinePage.as_view(), name="machines_page"),
    path("machines/<int:pk>/", MachineDetail.as_view(), name="retrive_machine"),
    path("machines/delete/<int:pk>/", MachineDelete.as_view(), name="delete_machine"),
    path("recyclelog/user/<int:pk>/", RetrieveRecycleLog.as_view(), name="recycle_log"),
]

map_ = [
    path("machines/getbycity/<str:city>/",MachinesByCity.as_view(),name="retrive_machine_by_city"),
    path("machines/setcoordinates/<str:name>/",SetMachineCoordinates.as_view(),name="set_coordinates"),
    path("machines/nearestmachine/<float:long>/<float:lat>/",GetNearestMachine.as_view(),name="nearest_machine"),
    path("machines/travelinfo/<int:pk>/<float:long>/<float:lat>/",GetTravelInfo.as_view(),name="travel_info"),
    path("machines/directions/<int:pk>/<float:long>/<float:lat>/",GetDirections.as_view(),name="directions"),
]

machine = [
    path("machines/qrcode/<str:name>/", MachineQRCode.as_view(), name="retrive_qrcode"),
    path("machines/videos/", MachineVideos.as_view(), name="retrive_qrcode"),
    path("machines/isbusy/<str:name>/", IsMachineBusy.as_view(), name="is_machine_busy"),
    path("machines/full/<str:name>/", MachineIsFull.as_view(), name="machine_full"),
    path("machines/recycle/check/<str:name>/", CheckRecycle.as_view(), name="check_recycle"),
    path("machines/recycle/update/V2/<str:name>/", UpdateV2Recycle.as_view(), name="update_v2_recycle"),
    path("machines/recycle/finish/<str:name>/", FinishRecycle.as_view(), name="finish_recycle"),
    path("machines/recycle/add/<str:name>/", UpdateRecycle.as_view(), name="update_recycle"),
    path("machines/recycle/update/<str:name>/", UpdateRecycle.as_view(), name="update_recycle"),
    path("machines/recycle/add/<str:name>/<str:phone_number>/", RecycleWithPhoneNumber.as_view(), name="update_recycle_phone"),
    path("machines/<str:name>/overview/", MachineOverview.as_view(), name="machine_overview"),
]

urlpatterns = []

urlpatterns += crud
urlpatterns += map_
urlpatterns += machine
