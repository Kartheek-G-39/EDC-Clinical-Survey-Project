from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _




def in_duration_day():
    return now() + timedelta(days=settings.DEFAULT_SURVEY_PUBLISHING_DURATION)


class Survey(models.Model):
    ALL_IN_ONE_PAGE = 0
    BY_QUESTION = 1
    BY_CATEGORY = 2

    DISPLAY_METHOD_CHOICES = [
        (BY_QUESTION, _("By question")),
        (BY_CATEGORY, _("By category")),
        (ALL_IN_ONE_PAGE, _("All in one page")),
    ]

    name = models.CharField(_("Name"), max_length=400)
    description = models.TextField(_("Description"))
    is_published = models.BooleanField(_("Users can see it and answer it"), default=True)
    need_logged_user = models.BooleanField(_("Only authenticated users can see it and answer it"))
    editable_answers = models.BooleanField(_("Users can edit their answers afterwards"), default=True)
    display_method = models.SmallIntegerField(
        _("Display method"), choices=DISPLAY_METHOD_CHOICES, default=ALL_IN_ONE_PAGE
    )
    template = models.CharField(_("Template"), max_length=255, null=True, blank=True)
    publish_date = models.DateField(_("Publication date"), blank=True, null=False, default=now)
    expire_date = models.DateField(_("Expiration date"), blank=True, null=False, default=in_duration_day)
    redirect_url = models.URLField(_("Redirect URL"), blank=True)

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __str__(self):
        return str(self.name)

    @property
    def safe_name(self):
        return self.name.replace(" ", "_").encode("utf-8").decode("ISO-8859-1")

    def latest_answer_date(self):
        """Return the latest answer date.

        Return None is there is no response."""
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        return reverse("survey-detail", kwargs={"id": self.pk})

    def non_empty_categories(self):
        return [x for x in list(self.categories.order_by("order", "id")) if x.questions.count() > 0]

    def is_all_in_one_page(self):
        return self.display_method == self.ALL_IN_ONE_PAGE



class ClinicalSite(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    location = models.TextField(_("Location"))
    site_code = models.CharField(_("Site Code"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("clinical site")
        verbose_name_plural = _("clinical sites")

    def __str__(self):
        return f"{self.name} - {self.site_code}"

class Protocol(models.Model):
    study_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    protocol_start_date = models.DateField()
    protocol_end_date = models.DateField(null=True, blank=True)
    actual_start_date = models.DateField(null = True , blank = True)
    actual_end_date = models.DateField(null=True, blank=True)
    clinical_site = models.ForeignKey(ClinicalSite, on_delete=models.CASCADE, related_name='protocols')
    status_list = [("Unknown","-------"),("Completed","Completed"),("Ongoing","ongoing")]
    status = models.CharField(max_length=20, choices = status_list,default = "Unknown")

    class Meta:
        verbose_name = _("protocol")
        verbose_name_plural = _("protocols")

    def __str__(self):
        return f"{self.study_id} - {self.title}"

class SurveyProtocolLink(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='protocol_links')
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE, related_name='survey_links', null=True, blank=True)
    clinical_site = models.ForeignKey(ClinicalSite, on_delete=models.CASCADE, related_name='survey_links') 

    class Meta:
        verbose_name = _("survey protocol link")
        verbose_name_plural = _("survey protocol links")
        unique_together = ('survey', 'protocol', 'clinical_site')

    def __str__(self):
        protocol_str = self.protocol.study_id if self.protocol else 'No Protocol'
        return f"{self.survey.name} - {protocol_str} - {self.clinical_site.site_code}"

    
class Participant(models.Model):
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    clinical_site = models.ForeignKey(ClinicalSite, on_delete=models.CASCADE, related_name='participants')
    protocols = models.ManyToManyField(Protocol, blank=True, related_name='participants')
    status_list = [("Enrolled","Enrolled"),("Screened","Screened"),("Excluded","Excluded")]

    enrollment_status= models.CharField(max_length = 30, choices = status_list,default = "Enrolled")
    reasons_list = [("Withdrawn Consent","Withdrawn"),("Ineligible","Ineligible"),("Other","Other")]
    exclusion_reason=models.CharField(max_length=20,choices = reasons_list, default= "Withdrawn Consent")
    enrollment_date = models.DateField(null=True, blank=True)
    screening_date = models.DateField(null=True, blank=True)

    
    def __str__(self):
        # This will display both the first name and last name in the dropdown
        return f"{self.name}"
class Adverse_events(models.Model):
    participant_name = models.ForeignKey(Participant,on_delete = models.CASCADE,related_name = "adverse_evnents")
    protocol_id = models.ForeignKey(Protocol,on_delete = models.CASCADE,related_name = "adverse_events")
    condition = [("Low","Low"),("Medium","Medium"),("High","High")]
    event_list= [("Mild","Mild"),("Moderate","Moderate"),("Severe","Severe")]
    event_type = models.CharField(max_length = 20, choices = event_list,default = "Mild")
    severity = models.CharField(max_length = 20 , choices = condition)
    description = models.TextField(_("Description"),blank = True)
    action_list = [("Monitored","Monitored"),("No Action","No Action"),("Treatment Adjusted","Treatment Adjusted")]
    action_taken = models.CharField(max_length = 20 , choices = action_list,default = "No Action" )
    outcome_list = [("Ongoing","Ongoing"),("Escalated","Escalated"),("Resolved","Resolved")]
    outcome = models.CharField(max_length = 20, choices = outcome_list,default = "Ongoing")
    
     
    class Meta:
        verbose_name = "Adverse Event"
        verbose_name_plural = "Adverse Evnets"
    
class Medications(models.Model):
    medication = models.CharField(max_length = 255)
    def __str__(self):
        return f"{self.medication}"
    
class MedicationRecord(models.Model):
    medication = models.ForeignKey(Medications, on_delete=models.CASCADE)
    participant_name = models.ForeignKey(Participant, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=150, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    record_number = models.IntegerField(default=1)  # Additional field to differentiate records

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.duration = self.end_date - self.start_date
        super().save(*args, **kwargs)

    
