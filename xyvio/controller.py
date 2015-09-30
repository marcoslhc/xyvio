from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response
import json


class Controller(object):

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except HTTPException, e:
            return e

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


class TemplateController(Controller):
    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')


class APIController(Controller):
    def render(self, **context):
        return Response(json.dumps(context), mimetype='application/json')
