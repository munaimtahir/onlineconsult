from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, PatientViewSet, ConsultRequestViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'consults', ConsultRequestViewSet, basename='consult')

urlpatterns = [
    path('', include(router.urls)),
]
