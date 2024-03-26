try:
    from django.conf.urls import url
except ImportError:
    # Django 4.0 replaced url by something else
    # See https://stackoverflow.com/a/70319607/2519059
    from django.urls import re_path as url

from survey.views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail,redirection
from survey.views.survey_result import serve_result_csv
from survey.views.sites_v import survey_selection, site_selection, list_clinical_sites, protocol_detail
from django.urls import path
from survey.views.redirection import redirection,Addparticipant,AdverseEvents,add_adverse_event,participants,participant_details

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="survey-list"),
    url(r"^(?P<id>\d+)/", SurveyDetail.as_view(), name="survey-detail"),
    path('survey-detail/<int:id>/', SurveyDetail.as_view(), name='survey_detail'),
    path('add_participant/',Addparticipant.as_view(),name = "add_participant"),
    path('adverse_events/',AdverseEvents.as_view(),name = "adverse_events"),
    path('add_adverse_event/',add_adverse_event,name = 'add_adverse_event'),
    path('participants',participants,name = 'participants'),
    path('participant_details/<int:participant_id>/',participant_details,name = 'participant_detail'),

    url(r"^csv/(?P<primary_key>\d+)/", serve_result_csv, name="survey-result"),
    url(r"^(?P<id>\d+)/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    url(r"^(?P<id>\d+)-(?P<step>\d+)/", SurveyDetail.as_view(), name="survey-detail-step"),
    url(r"^confirm/(?P<uuid>\w+)/", ConfirmView.as_view(), name="survey-confirmation"),
    path('select-survey/', survey_selection, name='survey_selection'),
    path('clinical-sites/', list_clinical_sites, name='list_clinical_sites'),
    path("redirection/",redirection,name="redirection"),
    # url(r'^clinical-sites/$', list_clinical_sites, name='list_clinical_sites'),m                                                                
    url(r'^site-selection/(?P<site_id>\d+)/$', site_selection, name='site_selection'),
    url(r'^protocol-detail/(?P<protocol_id>\d+)/$', protocol_detail, name='protocol_detail'),
]


