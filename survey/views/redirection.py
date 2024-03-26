from django.views.generic import View
from survey.models.redirect import Redirection
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from survey.models.survey import Participant,ClinicalSite,Protocol,Adverse_events,MedicationRecord
from django.shortcuts import render
from datetime import datetime,date
from ..forms import ParticipantForm,AdverseEventsForm
@csrf_exempt
def redirection(request):
    if request.method=="POST":
        try:
            # Get the JSON data from the request body
            data = json.loads(request.body)
            form = data.get("formdata")
            print(form)
            print(data.get("participant"))
            participant_id = form["id_participant"]
            # Extract necessary values from the JSON data
            checkboxid = data.get('checkboxid')
            value = data.get('text')
            print(form)
            if participant_id:
                
                combination = Redirection.objects.filter(Q(question_id=(checkboxid.split("_")[2])) & Q(text__iexact=value))
            # print(combination,"iuhytgfredfgjuhygted")
            if participant_id:
                if combination:
                    redirect_id = combination.values_list('redirect_survey_id',flat=True)[0]
                    listdata = {'msg':"ok","redirect_url":"/survey/"+str(redirect_id),'participant_id':participant_id}
                    return JsonResponse(listdata)
            else :
                return JsonResponse({'msg':"no"})

            # Return a success response
            

        except json.JSONDecodeError:
            # Return an error response if JSON decoding fails
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

class Addparticipant(View):

    def post(self, request, *args, **kwargs):
        form = ParticipantForm(request.POST)
        if Participant.objects.filter(name = form['name'].value(), birth_date = form['birth_date'].value()).exists():
            return HttpResponse("Participant already exists")
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            return HttpResponse("Saved Successully")
        else:
            print(form.errors)
            return HttpResponse("Failure")
    def get(self, request, *args, **kwargs):
        clinical_sites = ClinicalSite.objects.all()
        status_list = Participant.status_list
        reason_list = Participant.reasons_list
        protocols = Protocol.objects.all()
        context ={
            'clinical_sites'
        }
        return render(request,"survey\\add_participant.html",{'clinical_sites':clinical_sites,'status':status_list,'reasons':reason_list,'protocols':protocols})
class AdverseEvents(View):
    def get(self, request, *args, **kwargs):
        adverse_events = Adverse_events.objects.all()
        no_adverse_events = not adverse_events.exists()  # Check if there are no adverse events
    
        context = {
            'adverse_events': adverse_events,
            'no_adverse_events': no_adverse_events,
        }
        return render(request,"survey\\adverse_display.html",context)
def add_adverse_event(request):
    if request.method == "POST":
        form  = AdverseEventsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Saved sucesfully")
        else:
            print(form.errors)
            return HttpResponse("Failed to save")

    adverse_events = Adverse_events.objects.all()
    no_adverse_events = not adverse_events.exists()
    participants = Participant.objects.all()
    protocols = Protocol.objects.all()
    context = {
            'adverse_events': adverse_events,
            'no_adverse_events': no_adverse_events,
            'participants' : participants,
            'protocols':protocols,
            'event_list' : Adverse_events.event_list,
            'condition' : Adverse_events.condition,
            'action_list' : Adverse_events.action_list,
            'outcome_list' : Adverse_events.outcome_list,

        }
    return render(request,"survey\\add_adverse_event.html",context)
def participants(request):
    sort_by = request.GET.get('sort', 'id')
    participants = Participant.objects.order_by(sort_by)
    context = {
        'participants' : participants

    }
    return render(request,'survey\\participants.html',context)
def participant_details(request,participant_id):
    participant_details = Participant.objects.filter(id = participant_id).first()
    adverse_events = Adverse_events.objects.filter(participant_name_id = participant_id)
    medications = MedicationRecord.objects.filter(participant_name_id = participant_id)
    context = {
        'adverse_events' : adverse_events,
        'medications' : medications,
        'participant' : participant_details,
    }
    return render(request,"survey\\participant_details.html",context)
