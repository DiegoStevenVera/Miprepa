from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from ..accounts.models import User, UserUniversity
from .models import ChallengeTimeOut, History, ChallengeSurvival, ChallengeTest, CountQuestion
from ..courses.models import Question
from miprepa.settings.base import EXPERIENCE_FIRST, EXPERIENCE_SECOND, EXPERIENCE_OTHER


@shared_task
def create_historys_timeout(markeds, challenge_id):  # [{"id":id,"marked":"a","correct":True},...]
    try:
        challenge = ChallengeTimeOut.objects.get(id=challenge_id)
        user_university = challenge.user_university
        for marked in markeds:
            try:
                question = Question.objects.get(id=marked.get('id'))
                count_question = CountQuestion.objects.filter(user_university=user_university,
                                                              question=question).first()
                exp = 0
                if marked.get('correct') == 'True':
                    status = History.Type.correct.name
                    count_question.count += 1
                    count_question.save()
                    if count_question.count == 0:
                        user_university.experience += EXPERIENCE_FIRST
                        exp = EXPERIENCE_FIRST
                    elif count_question.count == 1:
                        user_university.experience += EXPERIENCE_SECOND
                        exp = EXPERIENCE_SECOND
                    else:
                        user_university.experience += EXPERIENCE_OTHER
                        exp = EXPERIENCE_OTHER
                    user_university.save()
                elif marked.get('correct') == 'False':
                    status = History.Type.wrong.name
                else:
                    status = History.Type.blank.name
                History.objects.create(user_university=user_university, question=question, ch_timeout=challenge,
                                       answer=marked.get('marked'), status=status, experience=exp)
            except ObjectDoesNotExist:
                pass
    except ObjectDoesNotExist:
        pass


@shared_task
def create_historys_survival(markeds, challenge_id):  # [{"id":id,"marked":"a","correct":True},...]
    try:
        challenge = ChallengeSurvival.objects.get(id=challenge_id)
        user_university = challenge.user_university
        for marked in markeds:
            try:
                question = Question.objects.get(id=marked.get('id'))
                count_question = CountQuestion.objects.filter(user_university=user_university,
                                                              question=question).first()
                exp = 0
                if marked.get('correct') == 'True':
                    status = History.Type.correct.name
                    count_question.count += 1
                    count_question.save()
                    if count_question.count == 0:
                        user_university.experience += EXPERIENCE_FIRST
                        exp = EXPERIENCE_FIRST
                    elif count_question.count == 1:
                        user_university.experience += EXPERIENCE_SECOND
                        exp = EXPERIENCE_SECOND
                    else:
                        user_university.experience += EXPERIENCE_OTHER
                        exp = EXPERIENCE_OTHER
                    user_university.save()
                elif marked.get('correct') == 'False':
                    status = History.Type.wrong.name
                else:
                    status = History.Type.blank.name
                History.objects.create(user_university=user_university, question=question, ch_survival=challenge,
                                       answer=marked.get('marked'), status=status, experience=exp)
            except ObjectDoesNotExist:
                pass
    except ObjectDoesNotExist:
        pass


@shared_task
def create_historys_test(markeds, challenge_id):  # [{"id":id,"marked":"a","correct":True},...]
    try:
        challenge = ChallengeTest.objects.get(id=challenge_id)
        user_university = challenge.user_university
        for marked in markeds:
            try:
                question = Question.objects.get(id=marked.get('id'))
                count_question = CountQuestion.objects.filter(user_university=user_university,
                                                              question=question).first()
                exp = 0
                if marked.get('correct') == 'True':
                    status = History.Type.correct.name
                    count_question.count += 1
                    count_question.save()
                    if count_question.count == 0:
                        user_university.experience += EXPERIENCE_FIRST
                        exp = EXPERIENCE_FIRST
                    elif count_question.count == 1:
                        user_university.experience += EXPERIENCE_SECOND
                        exp = EXPERIENCE_SECOND
                    else:
                        user_university.experience += EXPERIENCE_OTHER
                        exp = EXPERIENCE_OTHER
                    user_university.save()
                elif marked.get('correct') == 'False':
                    status = History.Type.wrong.name
                else:
                    status = History.Type.blank.name
                History.objects.create(user_university=user_university, question=question, ch_test=challenge,
                                       answer=marked.get('marked'), status=status, experience=exp)
            except ObjectDoesNotExist:
                pass
    except ObjectDoesNotExist:
        pass
