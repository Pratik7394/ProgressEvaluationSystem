from django.core.exceptions import PermissionDenied


def user_type_professor(function):

    def wrap(request, *args, **kwargs):
        studentProfessor = request.session['studentProfessor']
        if studentProfessor == 'professor':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def user_type_student(function):

    def wrap(request, *args, **kwargs):
        studentProfessor = request.session['studentProfessor']
        if studentProfessor == 'student':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

