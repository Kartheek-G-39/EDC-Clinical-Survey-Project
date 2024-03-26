import logging

from django.conf import settings
from django.shortcuts import redirect, render, reverse
from django.views.generic import View

from survey.decorators import survey_available
from survey.forms import ResponseForm
from survey.models.survey import Participant  # Assuming you have a Participant model
from survey.models.answer import Answer
from survey.models.question import Question
import uuid

LOGGER = logging.getLogger(__name__)

from django.db import transaction

class SurveyDetail(View):
    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        step = kwargs.get("step", 0)
        template_name = self.get_template_name(survey)
        
        # Assuming you have a way to identify the participant, e.g., via session or request
        participant_id = request.session.get('participant_id')
        if survey.need_logged_user and not participant_id:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        
        participant = None
        if participant_id:
            participant = Participant.objects.get(id=participant_id)

        form = ResponseForm(survey=survey, participant=participant, step=step)
        categories = form.current_categories()

        asset_context = self.get_asset_context(form)
        context = {
            "response_form": form,
            "survey": survey,
            "categories": categories,
            "step": step,
            "asset_context": asset_context,
        }

        return render(request, template_name, context)

    @survey_available
    def post(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        participant_id = request.session.get('participant_id')
        if survey.need_logged_user and not participant_id:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        
        participant = None
        if participant_id:
            participant = Participant.objects.get(id=participant_id)
            
        if (participant != None):
            print("participant is not none " + str(participant_id))
        else:
            print("participant is none....")

        form = ResponseForm(request.POST, survey=survey, participant=participant, step=kwargs.get("step", 0))
        categories = form.current_categories()

        if not survey.editable_answers and form.response is not None:
            LOGGER.info("Redirects to survey list after trying to edit non editable answer.")
            return redirect(reverse("survey-list"))
        context = {"response_form": form, "survey": survey, "categories": categories}
        if form.is_valid():
            return self.treat_valid_form(form, kwargs, request, survey, participant)
        return self.handle_invalid_form(context, form, request, survey)

    @staticmethod
    def handle_invalid_form(context, form, request, survey):
        LOGGER.info("Non valid form: <%s>", form)
        template_name = SurveyDetail.get_template_name(survey)
        return render(request, template_name, context)

    def treat_valid_form(self, form, kwargs, request, survey, participant):
        session_key = "survey_{}".format(kwargs["id"])
        if session_key not in request.session:
            request.session[session_key] = {}
        for key, value in list(form.cleaned_data.items()):
            request.session[session_key][key] = value
            request.session.modified = True
        next_url = form.next_step_url()
        response = self.handle_survey_completion(form, survey, participant, request, session_key)

        if next_url is not None:
            return redirect(next_url)
        
        return self.redirect_after_completion(request, response, survey)

    @staticmethod
    def get_template_name(survey):
        if survey.template is not None and len(survey.template) > 4:
            return survey.template
        else:
            return "survey/one_page_survey.html" if survey.is_all_in_one_page() else "survey/survey.html"

    @staticmethod
    def get_asset_context(form):
        return {
            "flatpickr": any(field.widget.attrs.get("class") == "date" for _, field in form.fields.items())
        }

    @staticmethod
    def handle_survey_completion(form, survey, participant, request, session_key):
        if survey.is_all_in_one_page() or not form.has_next_step():
            # Directly save the form, which internally creates a new Response
            response = form.save(commit=False)
    
            # Set additional fields on the Response object if necessary
            response.survey = survey
            
            if (response.participant == None):
                print ("&&&&& response.participant is also none")
                
            # response.participant = participant
            # if (participant == None):
            #     print ("&&&&& participant none")
            response.interview_uuid = uuid.uuid4().hex
    
            # Now, explicitly save the Response object to the database
            response.save()
    
            # Assuming your form.cleaned_data already contains the answers,
            # iterate through them to create Answer objects.
            for field_name, field_value in form.cleaned_data.items():
                if field_name.startswith("question_"):
                    # Extract question ID and fetch the Question object
                    q_id = int(field_name.split("_")[1])
                    question = Question.objects.get(pk=q_id)
                    # Create and save the Answer object
                    Answer.objects.create(
                        response=response, 
                        question=question, 
                        body=field_value
                    )
    
            # If there's additional handling needed for many-to-many fields on the Response model,
            # ensure those are manually handled here, as save_m2m() is not applicable.
    
            # Return the newly created Response object
            return response

   

    @staticmethod
    def redirect_after_completion(request, response, survey):
        del request.session["survey_{}".format(survey.id)]
        if response is None:
            return redirect(reverse("survey-list"))
        next_ = request.session.get("next", None)
        if next_:
            del request.session["next"]
            return redirect(next_)
        return redirect(survey.redirect_url or "survey-confirmation", uuid=response.interview_uuid)
