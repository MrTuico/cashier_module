from django.shortcuts import render,get_object_or_404,reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
import io
from reportlab.lib.colors import blue, gray, whitesmoke,white,black,skyblue
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from datetime import date, datetime, time

def uis(request):
    malasakit = 'cashier/static/malasakit.png'
    brglogo = 'cashier/static/logo.png'
    doh = 'cashier/static/doh.png'
    dswd = 'cashier/static/dswd.png'
    pcso = 'cashier/static/pcso.png'
    philhealth = 'cashier/static/philhealth.png'

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    response = HttpResponse(content_type='application/pdf')
    c.setTitle("UNIFIED INTAKE SHEET")
    c.setPageSize((8.27*inch, 11.69*inch))

    c.drawImage(malasakit, 2.6*inch, 11.2*inch, mask='auto', width=30, height=30)
    c.drawImage(brglogo,3.05*inch, 11.2*inch, mask='auto', width=30, height=30)
    c.drawImage(doh,3.53*inch, 11.2*inch, mask='auto', width=30, height=30)
    c.drawImage(dswd,3.93*inch, 11.2*inch, mask='auto', width=30, height=30)
    c.drawImage(pcso,4.38*inch, 11.2*inch, mask='auto', width=30, height=30)
    c.drawImage(philhealth,4.9*inch, 11.2*inch, mask='auto', width=50, height=30)

    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)
    c.drawString(3.3*inch, 11.05*inch, "UNIFIED INTAKE SHEET")

    c.setFillColor("black")
    c.setFont("Times-Roman", 7, leading=None)
    c.drawString(0.3*inch, 10.85*inch, "Philhealth Identification No")
    c.drawString(1.5*inch, 10.84*inch, "_______________________________________________")
    

    c.setFillColor("black")
    c.setFont("Times-Roman", 7, leading=None)
    c.drawString(6*inch, 10.85*inch, "Hospital No")
    c.drawString(6.5*inch, 10.85*inch, "_______________________________")
    

    # square
    c.setFillColor(white)
    c.rect(0.25*inch,0.25*inch,7.8*inch,10.55*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    c.setFillColor(skyblue)
    c.rect(0.25*inch,10.15*inch,7.8*inch,0.1*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    c.setFillColor(skyblue)
    c.rect(0.25*inch,8.15*inch,7.8*inch,0.1*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    c.setFillColor(skyblue)
    c.rect(0.25*inch,5.55*inch,7.8*inch,0.1*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    c.setFillColor(skyblue)
    c.rect(0.25*inch,4*inch,7.8*inch,0.1*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    c.setFillColor(skyblue)
    c.rect(0.25*inch,2.3*inch,7.8*inch,0.1*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    c.setFillColor(skyblue)
    c.rect(0.25*inch,1.35*inch,7.8*inch,0.1*inch,fill=1)
    c.setFillColor("black")
    c.setFont("Times-Bold", 10, leading=None)

    

 
    
    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    response.write(pdf)
    return response
