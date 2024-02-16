from django.urls import path
from . import views , cashier_receipt, reports_pdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('index', views.index,name='index'),
    path('auth_login', views.auth_login, name='auth_login'),
    path('sign_out', views.sign_out, name='sign_out'),
    path('<str:hospno>/get_patient_enctr/',views.get_patient_enctr,name='get_patient_enctr'),
    path('<str:enccode>/get_patient_charges/',views.get_patient_charges,name='get_patient_charges'),
    path('final_bill',views.final_bill,name='final_bill'),
    path('get_final_charges', views.get_final_charges, name='get_final_charges'),
    path('<str:enccode>/<str:encdate>/input_charges', views.input_charges, name='input_charges'),
    path('cashier_or', cashier_receipt.cahier_or, name='cashier_or'),
    path('payment', views.payment, name='payment'),
    path('exportToexcel', views.exportToexcel, name='exportToexcel'),
    path('reports', views.reports, name='reports'),
    path('cancel_receipt', views.cancel_receipt, name='cancel_receipt'),
    path('<str:line_id>/<str:orno>/update_or', views.update_or, name='update_or'),
    path('verify_or_cancelation', views.verify_or_cancelation, name='verify_or_cancelation'),
    path('generate_rcd_report', reports_pdf.generate_rcd_report, name='generate_rcd_report'),
    path('non_patient', views.non_patient, name='non_patient'),
    path('dup_or', views.dup_or, name='dup_or'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)