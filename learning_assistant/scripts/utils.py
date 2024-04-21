import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
import django
django.setup()

import secrets
import string

from acc.models import CustomUser, AnonUser
from learning_assistant.models import PlaygroundCode, UserGeneralTutorParent, PythonCourseParent, PythonCourseStudentBackground, PythonCourseNote, PythonCourseExercise


def _create_anon_custom_user():
    au_obj = AnonUser.objects.create()
    au_obj.save()

    cu_obj = CustomUser.objects.create(
        anon_user = au_obj
    )
    cu_obj.save()
    return cu_obj

def _get_customer_user(request):
    custom_user_id = request.session.get('custom_user_uuid', None)
    custom_user_obj = None
    if custom_user_id is None:
        custom_user_obj = _create_anon_custom_user()
        request.session['custom_user_uuid'] = str(custom_user_obj.id)
    else:
        custom_user_obj = CustomUser.objects.get(id = custom_user_id)
    
    return custom_user_obj

def _check_if_anon_user(user_obj):
    anon_user = True
    if user_obj.oauth_user is not None:
        anon_user = False
    return anon_user

def _generate_random_string(k = 10):
    return ''.join([secrets.choice(string.ascii_lowercase) for idx in range(k)])

def _create_playground_code_object(custom_user_obj, user_code):
    rnd_code_filename = _generate_random_string(k = 10)
    uc_obj = PlaygroundCode.objects.create(
        user_obj = custom_user_obj,
        code_unique_name = rnd_code_filename,
        user_code = user_code
    )
    uc_obj.save()
    return uc_obj

def _create_general_tutor_parent_object(custom_user_obj):
    ug_parent_obj = UserGeneralTutorParent.objects.create(
        user_obj = custom_user_obj
    )
    ug_parent_obj.save()
    return ug_parent_obj

def _is_bad_user_session(session_data):
    custom_user_obj_id = session_data.get('custom_user_uuid', None)
    err_message = 'User not found'
    if custom_user_obj_id is not None:
        custom_user_objects = CustomUser.objects.filter(id = custom_user_obj_id)
        if len(custom_user_objects) == 0:
            return True, err_message
        else:
            return False, ""
    else:
        return True, err_message


def _fetch_past_user_context_information(pcp_obj):
    
    student_background_full_str = ""
    sb_objects = PythonCourseStudentBackground.objects.filter(
        pg_obj = pcp_obj
    )
    if len(sb_objects) > 0:
        student_background_full_str = sb_objects[0].student_background

    course_notes_full_str = ""
    course_note_objects = PythonCourseNote.objects.filter(
        pg_obj = pcp_obj
    )
    if len(course_note_objects) > 0:
        course_notes_full_str = '\n'.join([f"Note ID: {cn_obj.id} | Note Text: {cn_obj.note}" for cn_obj in course_note_objects])

    course_exercise_full_str = ""
    course_exercise_objects = PythonCourseExercise.objects.filter(
        pg_obj = pcp_obj
    )
    if len(course_exercise_objects) > 0:
        course_exercise_full_str = '\n'.join([f"Note ID: {ce_obj.id} | Exercise Text: {ce_obj.exercise}" for ce_obj in course_exercise_objects])

    rv = {
        'student_background_text': student_background_full_str,
        'course_note_text': course_notes_full_str,
        'course_exercise_text': course_exercise_full_str
    }
    return rv
