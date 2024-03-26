import logging
import uuid

from django import forms
from django.conf import settings
from django.forms import models
from django.urls import reverse
from django.utils.text import slugify

from survey.models import Answer, Category
from survey.models.question import Question
from survey.models.response import Response
from survey.models.survey import Survey
from survey.signals import survey_completed
from survey.widgets import ImageSelectWidget

from survey.models.survey import Participant,Adverse_events

from django.db import transaction


LOGGER = logging.getLogger(__name__)

from survey.models.survey import Protocol, ClinicalSite



class SurveySelectionForm(forms.Form):
    site = forms.ModelChoiceField(queryset=ClinicalSite.objects.all(), label="Select Site", required=True)
    protocol = forms.ModelChoiceField(queryset=Protocol.objects.all(), label="Select Protocol (optional)", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['protocol'].queryset = Protocol.objects.none()

        if 'site' in self.data:
            try:
                site_id = int(self.data.get('site'))
                self.fields['protocol'].queryset = Protocol.objects.filter(clinical_site_id=site_id).order_by('title')
            except (ValueError, TypeError):
                pass  # invalid input; fallback to empty Protocol queryset


class ResponseForm(models.ModelForm):
    FIELDS = {
        Question.TEXT: forms.CharField,
        Question.SHORT_TEXT: forms.CharField,
        Question.SELECT_MULTIPLE: forms.MultipleChoiceField,
        Question.INTEGER: forms.IntegerField,
        Question.FLOAT: forms.FloatField,
        Question.DATE: forms.DateField,
        Question.TIME: forms.TimeField,
    }

    WIDGETS = {
        Question.TEXT: forms.Textarea,
        Question.SHORT_TEXT: forms.TextInput,
        Question.RADIO: forms.RadioSelect,
        Question.SELECT: forms.Select,
        Question.SELECT_IMAGE: ImageSelectWidget,
        Question.SELECT_MULTIPLE: forms.CheckboxSelectMultiple,
    }

    class Meta:
        model = Response
        fields = ['participant']

    def __init__(self, *args, **kwargs):
        """Expects a survey object to be passed in initially"""
        self.for_new_response = kwargs.pop('for_new_response', True)

        self.survey = kwargs.pop("survey")
        self.participant = kwargs.pop('participant', None)  # Use None as a default if 'participant' is not provided
        


        try:
            self.step = int(kwargs.pop("step"))
        except KeyError:
            self.step = None
        super().__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex

        # self.fields['participant'].queryset = Participant.objects.all()


        self.categories = self.survey.non_empty_categories()
        self.qs_with_no_cat = self.survey.questions.filter(category__isnull=True).order_by("order", "id")

        if self.survey.display_method == Survey.BY_CATEGORY:
            self.steps_count = len(self.categories) + (1 if self.qs_with_no_cat else 0)
        else:
            self.steps_count = len(self.survey.questions.all())
        # will contain prefetched data to avoid multiple db calls
        self.response = False
        self.answers = False

        self.add_questions(kwargs.get("data"))

        self._get_preexisting_response()

        if not self.survey.editable_answers and self.response is not None:
            for name in self.fields.keys():
                self.fields[name].widget.attrs["disabled"] = True

    def add_questions(self, data):
        # add a field for each survey question, corresponding to the question
        # type as appropriate.

        if self.survey.display_method == Survey.BY_CATEGORY and self.step is not None:
            if self.step == len(self.categories):
                qs_for_step = self.survey.questions.filter(category__isnull=True).order_by("order", "id")
            else:
                qs_for_step = self.survey.questions.filter(category=self.categories[self.step])

            for question in qs_for_step:
                self.add_question(question, data)
        else:
            for i, question in enumerate(self.survey.questions.all()):
                not_to_keep = i != self.step and self.step is not None
                if self.survey.display_method == Survey.BY_QUESTION and not_to_keep:
                    continue
                self.add_question(question, data)

    def current_categories(self):
        if self.survey.display_method == Survey.BY_CATEGORY:
            if self.step is not None and self.step < len(self.categories):
                return [self.categories[self.step]]
            return [Category(name="No category", description="No cat desc")]
        else:
            extras = []
            if self.qs_with_no_cat:
                extras = [Category(name="No category", description="No cat desc")]

            return self.categories + extras

    def _get_preexisting_response(self):
        if self.for_new_response:
            # If the form is for a new response, don't fetch a preexisting response
            self.response = None
        else:
            try:
                self.response = Response.objects.prefetch_related("participant", "survey")\
                    .filter(participant=self.participant, survey=self.survey)\
                    .latest('created')
            except Response.DoesNotExist:
                LOGGER.debug("No saved response for '%s' for participant %s", self.survey, self.participant)
                self.response = None
        return self.response

    def _get_preexisting_answers(self):
        """Recover pre-existing answers in database.

        The user must be logged. A Response containing the Answer must exists.
        Will create an attribute containing the answers retrieved to avoid multiple
        db calls.

        :rtype: dict of Answer or None"""
        if self.answers:
            return self.answers

        response = self._get_preexisting_response()
        if response is None:
            self.answers = None
        try:
            answers = Answer.objects.filter(response=response).prefetch_related("question")
            self.answers = {answer.question.id: answer for answer in answers.all()}
        except Answer.DoesNotExist:
            self.answers = None

        return self.answers

    def _get_preexisting_answer(self, question):
        """Recover a pre-existing answer in database.

        The user must be logged. A Response containing the Answer must exists.

        :param Question question: The question we want to recover in the
        response.
        :rtype: Answer or None"""
        answers = self._get_preexisting_answers()
        return answers.get(question.id, None)

    def get_question_initial(self, question, data):
        """Get the initial value that we should use in the Form

        :param Question question: The question
        :param dict data: Value from a POST request.
        :rtype: String or None"""
        initial = None
        answer = self._get_preexisting_answer(question)
        if answer:
            # Initialize the field with values from the database if any
            if question.type == Question.SELECT_MULTIPLE:
                initial = []
                if answer.body == "[]":
                    pass
                elif "[" in answer.body and "]" in answer.body:
                    initial = []
                    unformated_choices = answer.body[1:-1].strip()
                    for unformated_choice in unformated_choices.split(settings.CHOICES_SEPARATOR):
                        choice = unformated_choice.split("'")[1]
                        initial.append(slugify(choice))
                else:
                    # Only one element
                    initial.append(slugify(answer.body))
            else:
                initial = answer.body
        if data:
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            initial = data.get("question_%d" % question.pk)
        return initial

    def get_question_widget(self, question):
        """Return the widget we should use for a question.

        :param Question question: The question
        :rtype: django.forms.widget or None"""
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    @staticmethod
    def get_question_choices(question):
        """Return the choices we should use for a question.

        :param Question question: The question
        :rtype: List of String or None"""
        qchoices = None
        if question.type not in [Question.TEXT, Question.SHORT_TEXT, Question.INTEGER, Question.FLOAT, Question.DATE]:
            qchoices = question.get_choices()
            # add an empty option at the top so that the user has to explicitly
            # select one of the options
            if question.type in [Question.SELECT, Question.SELECT_IMAGE]:
                qchoices = tuple([("", "-------------")]) + qchoices
        return qchoices

    def get_question_field(self, question, **kwargs):
        """Return the field we should use in our form.

        :param Question question: The question
        :param **kwargs: A dict of parameter properly initialized in
            add_question.
        :rtype: django.forms.fields"""
        # logging.debug("Args passed to field %s", kwargs)
        try:
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)

    def add_question(self, question, data):
        """Add a question to the form.

        :param Question question: The question to add.
        :param dict data: The pre-existing values from a post request."""
        kwargs = {"label": question.text, "required": question.required}
        initial = self.get_question_initial(question, data)
        if initial:
            kwargs["initial"] = initial
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget
        field = self.get_question_field(question, **kwargs)
        field.widget.attrs["category"] = question.category.name if question.category else ""

        if question.type == Question.DATE:
            field.widget.attrs["class"] = "date"
        if question.type == Question.TIME:
            field.widget.attrs["class"] = "time"
        # logging.debug("Field for %s : %s", question, field.__dict__)
        self.fields["question_%d" % question.pk] = field

    def has_next_step(self):
        if not self.survey.is_all_in_one_page():
            if self.step < self.steps_count - 1:
                return True
        return False

    def next_step_url(self):
        if self.has_next_step():
            context = {"id": self.survey.id, "step": self.step + 1}
            return reverse("survey-detail-step", kwargs=context)

    def current_step_url(self):
        return reverse("survey-detail-step", kwargs={"id": self.survey.id, "step": self.step})

    @transaction.atomic
    def save(self, commit=True):
        """Save the response object, always creating a new one."""
        if not self.is_valid():
            # Optionally raise an exception or handle it as per your application's requirements
            raise ValueError("Cannot save the form: The form is not valid.")

        with transaction.atomic():  # Ensure atomicity of the Response and Answers creation
            response = Response()  # Always create a new Response object.
            response.survey = self.survey
            response.participant = self.participant
            if (self.participant == None):
                print ("&&&&& self.participant is none")
            
            response.participant = self.cleaned_data.get('participant')
            if (response.participant == None):
                print ("&&&&& response.participant is none")
            else:
                print ("&&& participant not none " + response.participant.name)
                
            response.interview_uuid = uuid.uuid4().hex  # Generate a unique identifier for the response.
            if commit:
                response.save()
                
                # Create an answer object for each question and associate it with this response.
                for field_name, field_value in self.cleaned_data.items():
                    print ("****** after&&&&")
                    if field_name.startswith("question_"):
                        # Extract question ID and fetch the Question object
                        q_id = int(field_name.split("_")[1])
                        question = Question.objects.get(id=q_id)
                        # Create and save the Answer object
                        Answer.objects.create(
                            response=response, 
                            question=question, 
                            body=field_value
                        )

                # Signal or additional logic for post-response handling can go here.
                survey_completed.send(sender=Response, instance=response, data={
                    "survey_id": response.survey.id, 
                    "interview_uuid": response.interview_uuid,
                    "participant_id": response.participant.id
                })

        return response
    
from survey.models.redirect import Redirection
class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name','birth_date','clinical_site','protocols','enrollment_status','exclusion_reason','enrollment_date','screening_date']
    
class ChoicessForm(forms.ModelForm):
    class Meta:
        model = Redirection
        fields = ['question', 'text', 'redirect_survey']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add classes for styling
        self.fields['question'].widget.attrs['class'] = 'question-dropdown'
        self.fields['redirect_survey'].widget.attrs['class'] = 'redirect-survey-dropdown' 

from survey.models.survey import Adverse_events
      
class AdverseEventsForm(forms.ModelForm):
    class Meta:
        model = Adverse_events
        fields = ['participant_name','protocol_id','event_type','severity','description','action_taken','outcome']
   
# # forms.py
# from django import forms

# class SurveyForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         questions = kwargs.pop('questions')
#         super(SurveyForm, self).__init__(*args, **kwargs)
#         for question in questions:
#             choices = [(choice.id, choice.text) for choice in question.choice_set.all()]
#             if question.choice_set.exists():
#                 self.fields[f"question_{question.id}"] = forms.ChoiceField(label=question.text, choices=choices, widget=forms.RadioSelect)
#             else:
#                 self.fields[f"question_{question.id}"] = forms.CharField(label=question.text)

# views.py
        
