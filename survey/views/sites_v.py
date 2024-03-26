from django.shortcuts import render
from survey.forms import SurveySelectionForm
from survey.models.survey import SurveyProtocolLink, ClinicalSite, Protocol
from django.shortcuts import render, get_object_or_404


def survey_selection(request):
    form = SurveySelectionForm(request.POST or None)
    surveys = None

    if request.method == 'POST' and form.is_valid():
        site = form.cleaned_data['site']
        protocol = form.cleaned_data['protocol']
        
        if protocol:
            surveys = SurveyProtocolLink.objects.filter(clinical_site=site, protocol=protocol)
        else:
            surveys = SurveyProtocolLink.objects.filter(clinical_site=site)

    return render(request, 'survey/survey_selection.html', {'form': form, 'surveys': surveys})

def site_selection(request, site_id):
    site = get_object_or_404(ClinicalSite, id=site_id)
    search_query = request.GET.get('search', '')

    protocols = Protocol.objects.filter(clinical_site=site)
    if search_query:
        protocols = protocols.filter(title__icontains=search_query)

    surveys = SurveyProtocolLink.objects.filter(clinical_site=site).select_related('survey')
    if search_query:
        surveys = surveys.filter(survey__name__icontains=search_query)

    return render(request, 'survey/site_selection.html', {
        'site': site,
        'protocols': protocols,
        'surveys': surveys,
        'search_query': search_query,
    })

def list_clinical_sites(request):
    print ("************************list_clinical_sites ========")
    sites = ClinicalSite.objects.all()
    return render(request, 'survey/list_clinical_sites.html', {'sites': sites})

def protocol_detail(request, protocol_id):
    protocol = get_object_or_404(Protocol, pk=protocol_id)
    surveys = SurveyProtocolLink.objects.filter(protocol=protocol).select_related('survey')
    
    return render(request, 'survey/protocol_detail.html', {
        'protocol': protocol,
        'surveys': surveys,
    })