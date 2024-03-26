import logging
from .question import Question
from .survey import Survey
from django.db import models
class QuestionSurvey(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    text = models.TextField()

class Redirection(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    redirect_survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=True, null=True)
