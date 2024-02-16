from django.shortcuts import render,get_object_or_404,reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from reportlab.pdfgen import canvas
import io
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from datetime import date, datetime, time
from django.template.loader import get_template
import requests,json
from xhtml2pdf import pisa
from itertools import groupby
from operator import itemgetter

root = "http://173.10.2.108:9092/"
reportsOfColandDepByUser = root + "api/cashop/reportsOfCollectionsandDepositsByUser"
cashop_api_showRCD= root + "api/cashop/showRCD"
reportsOfColandDepByUser2 = root + "api/cashop/reportsOfCollectionsandDepositsByUser2"

def generate_rcd_report(request):
    data=''
    now = datetime.now()
    date_today = datetime.strftime(now, '%Y-%m-%d')
    today = datetime.strftime(now, '%B %d, %Y')
    if request.method == 'POST':
        date_input = request.POST.get('date-input')
        date_object = datetime.strptime(date_input, "%Y-%m-%d").date()
        if date_input is None:
            date_today = datetime.strftime(now, '%Y-%m-%d')
        else:
            date_today =date_object
        showRCD = requests.post(cashop_api_showRCD).json()
        if showRCD['status'] == 'success':
            get_rcd  = showRCD['data']
        get_reports = requests.post(reportsOfColandDepByUser,data = {'date':date_input,'user':request.session['employee_id']}).json()
        get_reports2 = requests.post(reportsOfColandDepByUser2,data = {'date':date_input,'user':request.session['employee_id']}).json()
        total_amt = 0
        total_dm = 0
        total_sercices = 0
        total_desc= 0
        concat_data =''
        first_ornum = ''
        last_ornum = ''
        if get_reports['status'] == 'success' and get_reports2['status'] == 'success':
            data = get_reports['data']
            data2=get_reports2['data']            
            concat_data = data + data2
            try:
                sort_data = sorted(concat_data, key=lambda x: x['or_no'])
                first_ornum_i =sort_data[0]
                last_ornum_i = sort_data[-1]
                first_ornum = first_ornum_i['or_no']
                last_ornum = last_ornum_i['or_no']
            except IndexError:
                print("Something went wrong with first and last or number")
            total_desc = {}
            for d in concat_data:
                d['ac'] = d['ac'].replace("-"," - ")
                ac_desc = d['particulars']
                if d['status'] == 'CANCELLED':
                    d['amount'] = 0
                    total_amt_init = float(d['amount'])
                    total_amt += total_amt_init
                else:
                    total_amt_init = float(d['amount'])
                    total_amt += total_amt_init
                if d['particulars'] == 'Drugs & medicine':
                    if d['status'] == 'CANCELLED':
                        d['amount'] = 0
                        particular_init = float(d['amount'])
                        total_dm += particular_init
                    else:
                        particular_init = float(d['amount'])
                        total_dm += particular_init
                if d['particulars'] != 'Drugs & medicine':
                    if d['status'] == 'CANCELLED':
                        d['amount'] = 0
                        services_init = float(d['amount'])
                        total_sercices += services_init
                    else:
                        services_init = float(d['amount'])
                        total_sercices += services_init
                # print(ac_desc)
                if ac_desc in total_desc:
                    total_desc[ac_desc] += total_amt_init
                else:   
                    total_desc[ac_desc] = total_amt_init
            
    template_path = 'cashier/report_pdf.html'
    context = {'date_dep':request.session['date_dep'],'report_no':request.session['report_no'],'name':request.session['name'],'last_or':last_ornum,'first_or':first_ornum,'today':today,'td':total_desc.items(),'get_rcd':get_rcd,'report':sort_data,'date_today':date_today,'dm_tot':round(total_dm,2),'services_tot':round(total_sercices,2),'amt_tot':round(total_amt,2)}
    response = HttpResponse(content_type='application/pdf')
    #to download:
    # response['Content-Disposition'] = 'attachment; filename="DATA.pdf"'
    # to view
    response['Content-Disposition'] = 'filename="RCD.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(
    html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response