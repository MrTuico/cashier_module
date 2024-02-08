from datetime import datetime
from django.contrib.auth import authenticate,logout, login
from django.http import Http404, HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import render,redirect
from django.db.models import Q
import requests, json
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from reportlab.pdfgen import canvas
import io
from reportlab.lib.colors import blue, gray, whitesmoke,white,black
from reportlab.lib.units import inch
from django.contrib.auth.decorators import login_required

root = "http://172.22.10.11:9091/"
cashop_api = root + "api/cashop/lookup"
cashop_api_charges = root + "api/cashop/charges2"
cashop_api_ecntr = root + "api/cashop/encounter"
cashop_api_showRCD= root + "api/cashop/showRCD"
save_payment = root + "api/cashop/payment"
print_receipt = root + "api/cashop/printReceipt"
reportsOfColandDep = root + "api/cashop/reportsOfCollectionsandDeposits"
reportsOfColandDepByUser = root + "api/cashop/reportsOfCollectionsandDepositsByUser" #params date and user
login_api = root + "api/login"
getDetailsbyOR = root + "api/cashop/getDetailsbyOR"
getDetailsbyOR2 = root + "api/cashop/getDetailsbyOR2"
cancelOR = root + "api/cashop/cancelOR"
updateOR = root + "api/cashop/updateOR"
cancelOR2 = root + "api/cashop/cancelOR2"
updateOR2 = root + "api/cashop/updateOR2"
otherPayment = root + "api/cashop/otherPayment"
print_receipt2 = root + "api/cashop/printReceipt2"
reportsOfColandDep2 = root + "api/cashop/reportsOfCollectionsandDeposits2"
reportsOfColandDepByUser2 = root + "api/cashop/reportsOfCollectionsandDepositsByUser2"

def index(request):

    if request.session.get('employee_id') is not None:
        if request.session.get('report_no') is None:
            request.session['report_no'] = ''
        else:
            request.session['report_no'] = request.session['report_no']

        if request.session.get('or_no') is None:
            request.session['or_no'] = ''
        else:
            request.session['or_no'] = request.session['or_no']

        if request.session.get('date_dep') is None:
            request.session['date_dep'] = ''
        else:
            request.session['date_dep'] = request.session['date_dep']
        if request.method =='POST':
            report_num = request.POST.get('rep_no')
            or_num = request.POST.get('or_no')
            date = request.POST.get('date')
            request.session['report_no'] = report_num
            request.session['or_no'] = or_num
            request.session['date_dep'] = date
            return HttpResponseRedirect('/')
        return render(request, 'cashier/home.html',{'date':request.session['date_dep'],'user':request.session['name'],'report':request.session['report_no'],'or_no':request.session['or_no']})#,{'user':request.session['name']}
    else:
        return HttpResponseRedirect('/')

def auth_login(request):
    if request.session.get('employee_id') is None:
        if request.method == 'POST':
            userid = request.POST.get("userid").upper()
            password = request.POST.get("password")
            login_response = requests.post(login_api, data={'username': userid, 'password': password})
            login_json_response = login_response.json()

            if login_json_response['status'] == 'success':
                if json.dumps(login_json_response['data']) == "[]":
                    messages.warning(request, "Invalid Username or Password")  
                    return render(request, 'auth-login.html')
                else:
                    request.session['employee_id'] = login_json_response['data'][0]['employeeid']
                    request.session['user_level'] = login_json_response['data'][0]['user_level']
                    request.session['name'] = login_json_response['data'][0]['name']
                    request.session['position'] = login_json_response['data'][0]['postitle']
                    request.session['contactno'] = login_json_response['data'][0]['contactno']
                    request.session['email'] = login_json_response['data'][0]['email']
                    request.session['userid'] = userid
                    if login_json_response['data'][0]['user_level'] == 1:#ADMIN
                        return HttpResponseRedirect('index')
                    # elif login_json_response['data'][0]['user_level'] == 15:#BILLING
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 3:#LABORATORY
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 4:#RADIOLOGY
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 5:#PHARMACY
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 6:#PHILHEATH
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 16:#CASHIERING
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 2:#NURSING
                    #     return HttpResponseRedirect('/')
                    # elif login_json_response['data'][0]['user_level'] == 11:#CSSR
                    #     return HttpResponseRedirect('/')
                    else:
                        messages.error(request, "Access Denied! Please contact the system administrator")
                        return render(request, 'auth-login.html')
            else:
                messages.warning(request, "Invalid Username or Password")  
                return render(request, 'auth-login.html')

        else:
            return render(request, 'auth-login.html')
    else:
        return HttpResponseRedirect('/')
def sign_out(request):
    logout(request)
    messages.success(request, 'Successfully Logged-out in!')
    return HttpResponseRedirect("/auth_login")

def home(request):
    if request.session.get('employee_id') is not None:
        getData = ""
        if request.method == 'POST':
            search_text = request.POST.get('data-input','')
            if search_text:
                results = requests.post(cashop_api,data = {'hospno': search_text}).json()
                now = datetime.now()
                time_started = datetime.strftime(now, '%I:%M %p')
                request.session['start_time'] = time_started
                if results['status'] == 'success':
                    getData = results['data']
                    if getData == []:
                        results = requests.post(cashop_api,data = {'lastname': search_text}).json()
                        getData = results['data']
            else:
                getData =[]
        return render(request, 'cashier/patient_search.html',{'data':getData,'user':request.session['name']})
    else:
        return HttpResponseRedirect("/auth_login")

def get_patient_enctr(request,hospno):
    if request.session.get('employee_id') is not None:
        getPatientEnctrs = requests.post(cashop_api_ecntr,data = {'hospno': hospno}).json()
        results = requests.post(cashop_api,data = {'hospno': hospno}).json()
        get_results_name = results['data']
        for ii in get_results_name:
            fullname = ii['patfirst']+" "+ii['patmiddle']+" "+ii['patlast']
        if getPatientEnctrs['status'] == 'success':
            getPatientData = getPatientEnctrs['data']
            for c in getPatientData:
                c['enccode'] = c['enccode'].replace("/","-")
                timestamp_str = c['encdate']
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                c['encdate'] = timestamp.strftime("%B %d, %Y")
        return render(request, 'cashier/date_to_charge.html',{'enctrData':getPatientData, 'hospno':hospno,'fullname':fullname,'user':request.session['name']})
    else:
        return HttpResponseRedirect("/auth_login")
    
def get_patient_charges(request, enccode):
    enctr = enccode.replace("-","/")
    getPatientCharges = requests.post(cashop_api_charges,data = {'enctr': enctr}).json()
    get_patient_name = getPatientCharges['data']['patient']
    total_bill = 0
    for y in get_patient_name:
        fullname = y['patfirst']+" "+y['patmiddle']+" "+y['patlast']
        hospno = y['hpercode']
    if getPatientCharges['status'] == 'success':
        try:
            getPatientData = getPatientCharges['data']
            getPatientDataMedsup = getPatientCharges['detailed']['medsup']
            getPatientDataLab = getPatientCharges['detailed']['lab']
            getPatientDataMeds = getPatientCharges['detailed']['meds']
            if getPatientData['rnb'] == None:
                a = 0
            else:
                a = float(getPatientData['rnb'])
            if getPatientData['medsup'] == None:
                b = 0
            else:
                b = float(getPatientData['medsup'])
            if getPatientData['rad'] == None:
                c = 0
            else:
                c = float(getPatientData['rad'])
            if getPatientData['lab'] == None:
                d = 0
            else:
                d = float(getPatientData['lab'])
            if getPatientData['meds'] == None:
                e = 0
            else:
                e = float(getPatientData['meds'])
            if getPatientData['nursing'] == None:
                f = 0
            else:
                f = float(getPatientData['nursing'])
            if getPatientData['misc'] == None:
                g = 0
            else:
                g = float(getPatientData['misc'])
            if getPatientData['mrict'] == None:
                h = 0
            else:
                h = float(getPatientData['mrict'])
            if getPatientData['er'] == None:
                i = 0
            else:
                i = float(getPatientData['er'])
            if getPatientData['ordr'] == None:
                j = 0
            else:
                j = float(getPatientData['ordr'])
            if getPatientData['ecg'] == None:
                k = 0
            else:
                k = float(getPatientData['ecg'])
            if getPatientData['pt'] == None:
                l = 0
            else:
                l = float(getPatientData['pt'])
            if getPatientData['dialysis'] == None:
                m = 0
            else:
                m = float(getPatientData['dialysis'])
            if getPatientData['abtc'] == None:
                n = 0
            else:
                n = float(getPatientData['abtc'])
            total_bill = a+b+c+d+e+f+g+h+i+j+k+l+m+n
        except KeyError:
            getPatientData = []
            getPatientDataMedsup = []
            getPatientDataLab=[]
            getPatientDataMeds = []
    return render(request, 'charges.html',{'getPatientDataLab':getPatientDataLab,'getPatientDataMeds':getPatientDataMeds,'getPatientDataMedsup':getPatientDataMedsup,'chargesData':getPatientData,'fullname':fullname,'hospno':hospno,'total':total_bill,'enctr':enctr})

def final_bill(request): # test 1
    if request.method == 'POST':
        enctr = request.POST.get('enctr')
        getPatientCharges = requests.post(cashop_api_charges,data = {'enctr': enctr}).json()
        get_patient_name = getPatientCharges['data']['patient']
        for y in get_patient_name:
            fullname = y['patfirst']+" "+y['patmiddle']+" "+y['patlast']
            hospno = y['hpercode']
        rnb = request.POST.get('rnb')
        medsup = request.POST.get('medsup')
        medsup_list = request.POST.getlist('medsup_list')
    return render(request,'final_bill.html',{'rnb':rnb,'medsup':medsup,'medsup_list':medsup_list,'fullname':fullname,'hospno':hospno})

def get_final_charges(request): # test 2
    total_charge = 0
    if request.method == 'POST':
        charges = request.POST.getlist('medsup[]')
        rnb = request.POST.getlist('rnb[]')
        rad = request.POST.getlist('rad[]')
        lab = request.POST.getlist('lab[]')
        med = request.POST.getlist('med[]')
        nursing = request.POST.getlist('nursing[]')
        ecg = request.POST.getlist('ecg[]')
        misc = request.POST.getlist('misc[]')
        mriCt = request.POST.getlist('mriCt[]')
        er = request.POST.getlist('er[]')
        ordr = request.POST.getlist('ordr[]')
        pt = request.POST.getlist('pt[]')
        dialysis = request.POST.getlist('dialysis[]')
        abtc = request.POST.getlist('abtc[]')
        
        total_medsup_init  =[float(value) for value in charges]
        total_charge_rnb  =[float(rnb_value) for rnb_value in rnb]
        total_charge_rad  =[float(rad_value) for rad_value in rad]
        total_charge_lab  =[float(lab_value) for lab_value in lab]
        total_charge_med  =[float(med_value) for med_value in med]
        total_charge_nursing  =[float(nursing_value) for nursing_value in nursing]
        total_charge_ecg  =[float(ecg_value) for ecg_value in ecg]
        total_charge_misc  =[float(misc_value) for misc_value in misc]
        total_charge_mriCt  =[float(mriCt_value) for mriCt_value in mriCt]
        total_charge_er  =[float(er_value) for er_value in er]
        total_charge_ordr  =[float(ordr_value) for ordr_value in ordr]
        total_charge_pt =[float(pt_value) for pt_value in pt]
        total_charge_dialysis  =[float(dialysis_value) for dialysis_value in dialysis]
        total_charge_abtc  =[float(abtc_value) for abtc_value in abtc]
        total_rnb = sum(total_charge_rnb)
        total_medsup = sum(total_medsup_init)
        total_rad = sum(total_charge_rad)
        total_lab = sum(total_charge_lab)
        total_med = sum(total_charge_med)
        total_nursing = sum(total_charge_nursing)
        total_ecg = sum(total_charge_ecg)
        total_misc = sum(total_charge_misc)
        total_mriCt = sum(total_charge_mriCt)
        total_er = sum(total_charge_er)
        total_ordr = sum(total_charge_ordr)
        total_pt = sum(total_charge_pt)
        total_dialysis = sum(total_charge_dialysis)
        total_abtc = sum(total_charge_abtc)
        total = total_rnb + total_medsup + total_rad + total_med + total_lab + total_nursing + total_ecg + total_misc + total_mriCt + total_er + total_ordr + total_pt + total_dialysis + total_abtc
        return JsonResponse({'total_abtc':total_abtc,'total_dialysis':total_dialysis,'total_pt':total_pt,'total_ordr':total_ordr,'total_er':total_er,'total_mriCt':total_mriCt,'total_misc':total_misc,'total_nursing':total_nursing,'total_ecg':total_ecg,'total_med':total_med,'total_lab':total_lab,'total_rad':total_rad,'total_medsup':total_medsup,'total_rnb': total_rnb,'total':float(total)})

    else:
        return JsonResponse({'total_med':''})

def input_charges(request,enccode,encdate):
    now = datetime.now()
    date_today = datetime.strftime(now, '%Y-%m-%d')
    if request.session.get('employee_id') is not None:
        enctr = enccode.replace("-","/")
        getPatientCharges = requests.post(cashop_api_charges,data = {'enctr': enctr}).json()
        showRCD = requests.post(cashop_api_showRCD).json()
        if showRCD['status'] == 'success':
            get_rcd  = showRCD['data']
        get_patient_name = getPatientCharges['data']['patient']
     
        for y in get_patient_name:
            fullname = y['patfirst']+" "+y['patmiddle']+" "+y['patlast']
            hospno = y['hpercode']
        return render(request, 'cashier/input_charge.html',{'or_no':request.session['or_no'],'encdate':encdate,'now_date':date_today,'user':request.session['name'],'get_rcd':get_rcd,'fullname':fullname,'hospno':hospno,'enctr':enctr})
    else:
        return HttpResponseRedirect("/auth_login")

def payment(request):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            enccode = request.POST.get('enccode')
            items = request.POST.get('items')
            payment = request.POST.get('payment')
            orno = request.POST.get('orno')
            date_now = request.POST.get('date_today')
            enctr = enccode.replace("/","-")
            getPatientCharges = requests.post(cashop_api_charges,data = {'enctr': enccode}).json()
            showRCD = requests.post(cashop_api_showRCD).json()
            # print(showRCD)
            if showRCD['status'] == 'success':
                get_rcd  = showRCD['data']
                get_patient_name = getPatientCharges['data']['patient']
            for y in get_patient_name:
                fullname = y['patfirst']+" "+y['patmiddle']+" "+y['patlast']
                hospno = y['hpercode']
            
            results = requests.post(save_payment,data = {'enccode': enccode,'items':items,'payment':payment,'orno':orno,'entryby':request.session['employee_id']}).json()
            # receipt
            if results['status'] == 'success':
                request.session['or_no'] = str(int(orno) + 1).zfill(len(orno))
                payment_id = results['payment_id']
                getReceipt = requests.post(print_receipt,data = {'payment_id':payment_id}).json()
                # print(getReceipt)
                get_fullname = getReceipt['details']['patfirst']+" "+getReceipt['details']['patlast']
                get_date = getReceipt['details']['date']
                get_total_amt = str(getReceipt['details']['total_amount'])
                get_inWords = getReceipt['details']['InWords']
                get_line_item = getReceipt['line']
                # print(get_line_item)
                now = datetime.now()
                time_ended = datetime.strftime(now, '%I:%M %p')
                date_2day = datetime.strftime(now, '%B %d, %Y')
                buf = io.BytesIO()
                c = canvas.Canvas(buf)
                response = HttpResponse(content_type='application/pdf')
                c.setTitle("OFFICIAL RECEIPT")
                c.setPageSize((4*inch, 8*inch))
                c.setFillColor("black")# time started:
                c.setFont("Times-Roman", 8, leading=None)
                c.drawString(0.29*inch, 6.2*inch, "Time Started:")
                c.drawString(1*inch, 6.2*inch,request.session['start_time'])
                c.setFillColor("black")# time ended:
                c.setFont("Times-Roman", 8, leading=None)
                c.drawString(0.29*inch, 6.1*inch, "Time Ended:")
                c.drawString(1*inch, 6.1*inch, time_ended)
                c.setFillColor("black")#brghgmc
                c.setFont("Times-Roman", 9, leading=None)
                c.drawString(0.8*inch, 5.77*inch, "Bicol Region General Hospital")
                c.setFillColor("black")# brghgmc
                c.setFont("Times-Roman", 9, leading=None)
                c.drawString(0.8*inch, 5.67*inch, "and Geriatric Medical Center")
                c.setFillColor("black")# fullname
                c.setFont("Times-Roman", 12, leading=None)
                c.drawString(0.6*inch, 5.4*inch, get_fullname)
                c.setFillColor("black")# date
                c.setFont("Times-Roman", 10, leading=None)
                c.drawString(1.85*inch, 6.1*inch, date_2day)
                c.setFillColor("black")# total_amount
                c.setFont("Times-Roman", 12, leading=None)
                c.drawString(3*inch, 3*inch, get_total_amt)
                c.setFillColor("black")# cashier 
                c.setFont("Times-Roman", 12, leading=None)
                c.drawString(1.2*inch, 1.1*inch, request.session['name'] )

                c.setFillColor("black")# cashier 
                c.setFont("Times-Roman", 7.5, leading=None)
                c.drawString(0.4*inch, 2.48*inch, get_inWords)
                a = 4.8
                b= 0.2
                for i in get_line_item:
                    c.setFillColor("black")# description
                    c.setFont("Times-Roman", 12, leading=None)
                    c.drawString(0.35*inch, a*inch,i['description'])
                    c.setFillColor("black")# amount_item
                    c.setFont("Times-Roman", 12, leading=None)
                    c.drawString(3.15*inch, a*inch,str(i['amount']))
                    a-=b
                c.showPage()
                c.save()
                pdf = buf.getvalue()
                buf.close()
                response.write(pdf)
                return response
                # receipt
            elif results['status'] == 'failed':
                return HttpResponseRedirect("/dup_or")
            
            return render(request, 'cashier/input_charge.html',{'user':request.session['name'],'get_rcd':get_rcd,'fullname':fullname,'hospno':hospno,'enctr':enccode})
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/auth_login")
def reports(request):
    if request.session.get('employee_id') is not None:
        now = datetime.now()
        date_today = datetime.strftime(now, '%Y-%m-%d')
        data=''
        if request.method == 'POST':
            date_input = request.POST.get('date-input')
            get_reports = requests.post(reportsOfColandDep,data = {'date':date_input}).json()
            if get_reports['status'] == 'success':
                data = get_reports['data']
                for d in data:
                    d['date'] = datetime.strftime(now, '%B %d, %Y')
        return render(request, 'cashier/generate_report.html',{'date_today':date_today,'data':data,'user':request.session['name']})
    else:
        return HttpResponseRedirect("/auth_login")
def exportToexcel(request):
    if request.session.get('employee_id') is not None:
        now = datetime.now()
        date_today = datetime.strftime(now, '%Y-%m-%d')
        concat_data=''
        sort_data = ''
        if request.method == 'POST':
            date_input = request.POST.get('date-input')
            if date_input is None:
                date_today = datetime.strftime(now, '%Y-%m-%d')
            else:
                date_today =date_input
            get_reports = requests.post(reportsOfColandDepByUser,data = {'date':date_input,'user':request.session['employee_id']}).json()
            get_reports2 = requests.post(reportsOfColandDepByUser2,data = {'date':date_input,'user':request.session['employee_id']}).json()
            if get_reports['status'] == 'success' and get_reports2['status'] == 'success':
                data = get_reports['data']
                data2=get_reports2['data']
                concat_data = data + data2
                sort_data = sorted(concat_data, key=lambda x: x['or_no'])
        return render(request, 'cashier/export_report.html',{'date_today':date_today,'data':sort_data,'user':request.session['name']})
    
def cancel_receipt(request):
    if request.session.get('employee_id') is not None:
        data=''
        data_line =''
        change=''
        amt_tendered = ''
        tot_amt=''
        orno_show = ''
        now = datetime.now()
        orno_input =''
        try:
            if request.method == 'POST':
                data_input = request.POST.get('data_input', '')
                request.session['orno_input'] = data_input
                orno_input = request.session['orno_input']
                get_orDetails = requests.post(getDetailsbyOR,data = {'orno':data_input}).json()
                if get_orDetails['status'] == 'success':
                    request.session['cancel_stat'] = get_orDetails['status']
                    data_line = get_orDetails['line']
                    data = get_orDetails['details']
                    for c in data:
                        orno_show = c['or_no']
                        change = c['change']
                        amt_tendered = c['amount_tendered']
                        tot_amt = c['total_amount']
                        c['patmiddle'] = c['patmiddle'][0:1]
                        # print(format(c['date']))
                        # date_time = c['date']
                        # cdate = datetime.strptime(date_time, '%B %d, %Y %I:%M %p')
                        # c['date'] = cdate.strftime('%B %d, %Y %I:%M %p')
                else:
                    request.session['cancel_stat'] = get_orDetails['status']
                    get_orDetails2 = requests.post(getDetailsbyOR2,data = {'orno':data_input}).json()
                    data_line = get_orDetails2['line']
                    data = get_orDetails2['details']
                    for c in data:
                        orno_show = c['or_no']
                        change = c['change']
                        amt_tendered = c['amount_tendered']
                        tot_amt = c['total_amount']
        except KeyError:
            messages.warning(request, "Invalid OR Number!")
        return render(request, 'cashier/cancel_receipt.html',{'orno_input':orno_input,'orno_show':orno_show,'change':change,'amt_tendered':amt_tendered,'tot_amt':tot_amt,'data':data,'data_line':data_line,'user':request.session['name']})
    else:
        return HttpResponseRedirect("/auth_login")
    
def dup_or(request):
    if request.session.get('employee_id') is not None:
        return render(request, 'cashier/duplicate_orno.html',{'user':request.session['name']})
    else:
        return HttpResponseRedirect("/auth_login")
def verify_or_cancelation(request):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            ornum = request.POST.get('ornum')
            password = request.POST.get('pass_verify')
            if request.session['cancel_stat'] == 'success':
                or_cancel_verification = requests.post(cancelOR, data={'orno': ornum, 'password': password}).json()
                if or_cancel_verification['status'] == 'success':
                    messages.success(request, "OR "f'{ornum}' + " successfully cancelled!")
                    return HttpResponseRedirect("/cancel_receipt")
                else:
                    messages.warning(request, "Invalid Password!")
                    return HttpResponseRedirect("/cancel_receipt")
            else:
                or_cancel_verification2 = requests.post(cancelOR2, data={'orno': ornum, 'password': password}).json()
                if or_cancel_verification2['status'] == 'success':
                    messages.success(request, "OR "f'{ornum}' + " successfully cancelled!")
                    return HttpResponseRedirect("/cancel_receipt")
                else:
                    messages.warning(request, "Invalid Password!")
                    return HttpResponseRedirect("/cancel_receipt")
        else:
            return HttpResponseRedirect("/cancel_receipt")
    else:
        return HttpResponseRedirect("/auth_login")
def update_or(request,line_id,orno):
    if request.session.get('employee_id') is not None:
        get_orDetails = requests.post(getDetailsbyOR,data = {'orno':orno}).json()
        if get_orDetails['status'] == 'success':
            show_RCD = requests.post(cashop_api_showRCD).json()
            if show_RCD['status'] == 'success':
                get_rcd  = show_RCD['data']
            data_line = get_orDetails['line']
            for s in data_line:
                if line_id == s['line_id']:
                    payment_id = s['payment_id']
                    particular_id = s['id']
                    amt = s['amount']
            if request.method == 'POST':
                password = request.POST.get('pass_verify')
                f_payment_id = request.POST.get('payment_id')
                f_line_id = request.POST.get('line_id')
                f_amount = request.POST.get('amount')
                f_particular = request.POST.get('particular')
                or_update_verification = requests.post(updateOR, data={'password': password,'payment_id':f_payment_id,'id':f_line_id,'particular':f_particular,'amount':f_amount}).json()
                if or_update_verification['status'] == 'success':
                    messages.success(request, "OR No. "f'{orno}' + " successfully updated!")
                    return HttpResponseRedirect("/cancel_receipt")
                else:
                    messages.warning(request, "Invalid Password!")
                    return HttpResponseRedirect("/cancel_receipt")
        else:
            get_orDetails2 = requests.post(getDetailsbyOR2,data = {'orno':orno}).json()
            # print(get_orDetails2)
            if get_orDetails2['status'] == 'success':
                show_RCD = requests.post(cashop_api_showRCD).json()
                if show_RCD['status'] == 'success':
                    get_rcd  = show_RCD['data']
                data_line = get_orDetails2['line']
                for s in data_line:
                    if line_id == s['line_id']:
                        payment_id = s['payment_id']
                        particular_id = s['id']
                        amt = s['amount']
                if request.method == 'POST':
                    password = request.POST.get('pass_verify')
                    f_payment_id = request.POST.get('payment_id')
                    f_line_id = request.POST.get('line_id')
                    f_amount = request.POST.get('amount')
                    f_particular = request.POST.get('particular')
                    or_update_verification = requests.post(updateOR2, data={'password': password,'payment_id':f_payment_id,'id':f_line_id,'particular':f_particular,'amount':f_amount}).json()
                    if or_update_verification['status'] == 'success':
                        messages.success(request, "OR No. "f'{orno}' + " successfully updated!")
                        return HttpResponseRedirect("/cancel_receipt")
                    else:
                        messages.warning(request, "Invalid Password!")
                        return HttpResponseRedirect("/cancel_receipt")
        return render(request, 'cashier/update_or.html',{'user':request.session['name'],'get_rcd':get_rcd,'line_id':line_id,'payment_id':payment_id,'particular_id':particular_id,'amt':amt,'orno':orno})
    else:
        return HttpResponseRedirect("/auth_login")
    
def non_patient(request):
    if request.session.get('employee_id') is not None:
        now = datetime.now()
        date_today = datetime.strftime(now, '%Y-%m-%d')
        showRCD = requests.post(cashop_api_showRCD).json()
        if showRCD['status'] == 'success':
            get_rcd  = showRCD['data']
        if request.method == 'POST':
            name = request.POST.get('fullname').upper()
            items = request.POST.get('items')
            payment = request.POST.get('payment')
            orno = request.POST.get('orno')
            date_now = request.POST.get('date_today')
            total_bill = request.POST.get('total_bill')
            check_duplicate = requests.post(reportsOfColandDep,data = {'date':date_now}).json()
            # print(check_duplicate)
            chkDup_data = check_duplicate['data']
            for k in chkDup_data:
                dup_or_no = k['or_no']
                if orno == dup_or_no:
                    return HttpResponseRedirect("/dup_or")
            results = requests.post(otherPayment,data = {'items':items,'payment':payment,'orno':orno,'entryby':request.session['employee_id'],'total_amount':total_bill,'name':name}).json()
            # receipt
            if results['status'] == 'success':
                request.session['or_no'] = str(int(orno) + 1).zfill(len(orno))
                payment_id = results['payment_id']
                getReceipt = requests.post(print_receipt2,data = {'payment_id':payment_id}).json()
                # print(getReceipt)
                get_fullname = getReceipt['details']['name']
                get_date = getReceipt['details']['date']
                get_total_amt = str(getReceipt['details']['total_amount'])
                get_inWords = getReceipt['details']['InWords']
                get_line_item = getReceipt['line']
                # print(get_line_item)
                now = datetime.now()
                time_ended = datetime.strftime(now, '%I:%M %p')
                date_2day = datetime.strftime(now, '%B %d, %Y')
                buf = io.BytesIO()
                c = canvas.Canvas(buf)
                response = HttpResponse(content_type='application/pdf')
                c.setTitle("OFFICIAL RECEIPT")
                c.setPageSize((4*inch, 8*inch))
                c.setFillColor("black")# time started:
                c.setFont("Times-Roman", 8, leading=None)
                c.drawString(0.29*inch, 6.2*inch, "Time Started:")
                c.drawString(1*inch, 6.2*inch,request.session['start_time'])
                c.setFillColor("black")# time ended:
                c.setFont("Times-Roman", 8, leading=None)
                c.drawString(0.29*inch, 6.1*inch, "Time Ended:")
                c.drawString(1*inch, 6.1*inch, time_ended)
                c.setFillColor("black")#brghgmc
                c.setFont("Times-Roman", 9, leading=None)
                c.drawString(0.8*inch, 5.77*inch, "Bicol Region General Hospital")
                c.setFillColor("black")# brghgmc
                c.setFont("Times-Roman", 9, leading=None)
                c.drawString(0.8*inch, 5.67*inch, "and Geriatric Medical Center")
                c.setFillColor("black")# fullname
                c.setFont("Times-Roman", 12, leading=None)
                c.drawString(0.6*inch, 5.4*inch, get_fullname)
                c.setFillColor("black")# date
                c.setFont("Times-Roman", 10, leading=None)
                c.drawString(1.85*inch, 6.1*inch, date_2day)
                c.setFillColor("black")# total_amount
                c.setFont("Times-Roman", 12, leading=None)
                c.drawString(3*inch, 3*inch, get_total_amt)
                c.setFillColor("black")# cashier 
                c.setFont("Times-Roman", 12, leading=None)
                c.drawString(1.2*inch, 1.1*inch, request.session['name'] )

                c.setFillColor("black")# cashier 
                c.setFont("Times-Roman", 7.5, leading=None)
                c.drawString(0.4*inch, 2.48*inch, get_inWords)
                a = 4.8
                b= 0.2
                for i in get_line_item:
                    c.setFillColor("black")# description
                    c.setFont("Times-Roman", 12, leading=None)
                    c.drawString(0.35*inch, a*inch,i['description'])
                    c.setFillColor("black")# amount_item
                    c.setFont("Times-Roman", 12, leading=None)
                    c.drawString(3.15*inch, a*inch,str(i['amount']))
                    a-=b
                c.showPage()
                c.save()
                pdf = buf.getvalue()
                buf.close()
                response.write(pdf)
                return response
                # receipt
            elif results['status'] == 'failed':
                return HttpResponseRedirect("/dup_or")
        return render(request, 'cashier/non_patient.html',{'or_no':request.session['or_no'],'now_date':date_today,'user':request.session['name'],'get_rcd':get_rcd,})
    else:
        return HttpResponseRedirect("/auth_login")

    

