from django.shortcuts import render,get_object_or_404,reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
import io
from reportlab.lib.colors import blue, gray, whitesmoke,white,black
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from datetime import date, datetime, time

def cahier_or(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    response = HttpResponse(content_type='application/pdf')
    c.setTitle("OFFICIAL RECEIPT")
    c.setPageSize((3.93701*inch, 9.84252*inch))
    if request.method == 'POST':
        rnb = request.POST.get('pdf_rnb')
        medsup = request.POST.get('pdf_medsup')
        rad = request.POST.get('pdf_rad')
        lab = request.POST.get('pdf_lab')
        med = request.POST.get('pdf_med')
        nursing = request.POST.get('pdf_nursing')
        ecg = request.POST.get('pdf_ecg')
        misc = request.POST.get('pdf_misc')
        mriCt = request.POST.get('pdf_mriCt')
        er = request.POST.get('pdf_er')
        ordr = request.POST.get('pdf_ordr')
        pt = request.POST.get('pdf_pt')
        dialysis = request.POST.get('pdf_dialysis')
        abtc = request.POST.get('pdf_abtc')
        totalbill = request.POST.get('pdf_total')
        print(totalbill)
        
        if rnb == 0:
            c.drawString(0.3*inch, 8*inch, "")
        else:
            c.setFillColor("black")# Amount.:
            c.setFont("Times-Bold", 10, leading=None)
            c.drawString(0.3*inch, 8*inch, "ROOM AND BOARD")
            c.drawString(3*inch, 8*inch,rnb)
            
        # if medsup == 0:
        #     c.drawString(0.3*inch, 5*inch, "Q")
        # else:
        #     c.setFillColor("black")# Amount.:
        #     c.setFont("Times-Bold", 10, leading=None)
        #     c.drawString(0.3*inch, 7.75*inch, "MEDICAL SUPPLIES")
        #     c.drawString(3*inch, 7.75*inch,medsup)
        # if rad == '':
        #     c.drawString(0.3*inch, 8*inch, "")
        # else:
        #     c.setFillColor("black")# Amount.:
        #     c.setFont("Times-Bold", 10, leading=None)
        #     c.drawString(0.3*inch, 7.5*inch, "RADIOLOGY")
        #     c.drawString(3*inch, 7.5*inch,rad)
    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    response.write(pdf)
    return response
