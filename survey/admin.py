from django.contrib import admin

from survey.actions import make_published
from survey.exporter.csv import Survey2Csv
from survey.exporter.tex import Survey2Tex
from survey.models import Answer, Category, Question, Response, Survey

admin.site.site_header = 'Mushroom EDC Administration'


from survey.models.survey import ClinicalSite, Protocol, SurveyProtocolLink, Participant,Adverse_events,MedicationRecord,Medications

# Optionally, you can create custom admin classes to customize the admin interface


class MedicationAdmin(admin.ModelAdmin):
    list_display = ('medication',)
    search_fields = ('medication',)
admin.site.register(Medications,MedicationAdmin)
class ClinicalSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'site_code')
    search_fields = ('name', 'site_code')
class MedicationRecordAdmin(admin.ModelAdmin):
    list_display = ('participant_name', 'medication', 'dosage')
    search_fields = ('medication', 'participant_id')
class AdverseEventsAdmin(admin.ModelAdmin):
    list_display = ('participant_name','protocol_id','severity','action_taken')
    search_fields = ('partcipant_name','severity')
admin.site.register(MedicationRecord,MedicationRecordAdmin)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('study_id', 'title', 'protocol_start_date', 'protocol_end_date')
    search_fields = ('study_id', 'title')
    list_filter = ('protocol_start_date', 'protocol_end_date')

class SurveyProtocolLinkAdmin(admin.ModelAdmin):
    list_display = ('survey', 'protocol', 'clinical_site')
    list_filter = ('survey', 'protocol', 'clinical_site')
    search_fields = ('survey__name', 'protocol__study_id', 'clinical_site__site_code')

# Register your models here.
admin.site.register(ClinicalSite, ClinicalSiteAdmin)
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(SurveyProtocolLink, SurveyProtocolLinkAdmin)
admin.site.register(Adverse_events,AdverseEventsAdmin)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'clinical_site',"enrollment_status")   
    list_filter = ('clinical_site', 'protocols')
    search_fields = ('name', 'clinical_site__name')

    # If you want to customize how the protocols are displayed in the admin,
    # you might need to define a custom form and use formfield_for_manytomany
    # method. For simplicity, it's not included here, but you can customize
    # this admin class as needed.
    


class QuestionInline(admin.StackedInline):
    model = Question
    ordering = ("order", "category")
    extra = 1

    def get_formset(self, request, survey_obj, *args, **kwargs):
        formset = super().get_formset(request, survey_obj, *args, **kwargs)
        if survey_obj:
            formset.form.base_fields["category"].queryset = survey_obj.categories.all()
        return formset


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "need_logged_user", "template")
    list_filter = ("is_published", "need_logged_user")
    inlines = [CategoryInline, QuestionInline]
    actions = [make_published, Survey2Csv.export_as_csv, Survey2Tex.export_as_tex]


# class AnswerBaseInline(admin.StackedInline):
#     fields = ("question", "body")
#     readonly_fields = ("question",)
#     extra = 0
#     model = Answer

class AnswerBaseInline(admin.StackedInline):
    model = Answer
    extra = 1  # Set to 1 or 0 based on your preference


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'participant', 'protocol', 'created', 'updated', 'interview_uuid')
    list_filter = ('survey', 'protocol', 'created', 'updated', 'participant')
    search_fields = ('interview_uuid', 'survey__name', 'participant__user__username', 'protocol__study_id')
    raw_id_fields = ('participant', 'protocol')  # Use raw_id_fields for ForeignKey fields to improve usability
    
    inlines = [AnswerBaseInline]


    # If 'participant' and 'protocol' models have a 'name' or similar attribute for easier identification, consider adding:
    # search_fields = ('interview_uuid', 'survey__name', 'participant__name', 'protocol__title')



# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
# admin.py
from django.contrib import admin
from survey.models.redirect import  QuestionSurvey, Redirection


admin.site.register(QuestionSurvey)
admin.site.register(Redirection)
