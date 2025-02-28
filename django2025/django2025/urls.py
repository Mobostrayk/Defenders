
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name ='index'),
    path('about/', views.about, name ='about'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
