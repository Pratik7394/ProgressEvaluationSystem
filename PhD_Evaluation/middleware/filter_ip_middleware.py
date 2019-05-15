from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

class FilterHostMiddleware(MiddlewareMixin):

    # /////////////// DONT REMOVE ///////////////
    # def __init__(self, get_response):
    #     self.get_response = get_response
    #
    # def __call__(self, request):
    #     return self.get_response(request)
    # /////////////// ---- ------ ///////////////

    def process_request(self, request):

        allowed_hosts = ['169.226.16.120:8000',]  # specify complete host names here
        host = request.META.get('HTTP_HOST')

        if host[len(host)-25:] == 'matrix.cs.albany.edu:8000':  # if the host name is matrix.cs.albany.edu:8000 then add to the allowed hosts
            allowed_hosts.append(host)

        print('allowedHost --> ' + str(allowed_hosts))

        # /////////////// If host not found .. HttpResponseForbidden ///////////////
        if host not in allowed_hosts:
            print("Forbidden")
            raise HttpResponseForbidden
        # /////////////// ------------------------------------------ ///////////////

        return None