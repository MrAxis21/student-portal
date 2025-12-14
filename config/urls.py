"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('portal.urls')),
    path('admin/', admin.site.urls),
    # path('portal/', include('portal.urls')), # Handled by root include for now, or keep both? 
    # Let's keep the explicitly requested portal/ path as well if needed, but for now we want root to work.
    # Actually, previous config had 'portal/' -> portal.urls. 
    # If I map '' -> portal.urls, the routes in portal.urls (like 'login/') become '/login/'.
    # If I keep 'portal/' -> portal.urls, they are '/portal/login/'.
    # The user asked for a homepage.
    # I will map '' to 'portal.urls' AND keep 'portal/' if I want to support legacy links, but better to just use one.
    # I will replace the previous 'portal/' include with a comment or remove it, to avoid confusion.
    # But wait, 'portal.urls' has 'dashboard/', 'login/' etc.
    # If I map '' -> portal.urls, then '/dashboard/' works.
    # If I leave 'portal/' -> portal.urls, then '/portal/dashboard/' works.
    # I'll just map '' to portal.urls and remove the old 'portal/' one to be clean.
]
