# -*- coding: utf-8 -*-
import os
import urlparse
from datastore import RedisDataStore
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader


class Shortly(object):

    def __init__(self, config=None, dataStore=None):
        if dataStore is None:
            raise Exception('No data store defined')
        self.dataStore = dataStore
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.url_map = Map([
            Rule('/', endpoint='new_url'),
            Rule('/<short_id>', endpoint='follow_short_link'),
            Rule('/<short_id>+', endpoint='short_link_details')
        ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def on_new_url(self, request):
        error = None
        url = ''
        if request.method == 'POST':
            url = {
                'url': request.form['url'],
                'custom_id': request.form['custom_id']
            }
            if not is_valid_url(url['url']):
                error = 'Please enter a valid URL'
            else:
                short_id = self.insert_url(**url)
                return redirect('/%s+' % short_id)
        return self.render_template('new_url.html', error=error, url=url)

    def insert_url(self, url, custom_id=None):
        short_id = self.dataStore.get('reverse-url:' + url)
        if custom_id is None and short_id is not None:
            return short_id
        elif custom_id is None or custom_id == '':
            url_num = self.dataStore.incr('last-url-id')
            short_id = base36_encode(url_num)
        else:
            short_id = custom_id
        self.dataStore.set('url-target:' + short_id, url)
        self.dataStore.set('reverse-url:' + url, short_id)
        return short_id

    def on_follow_short_link(self, request, short_id):
        link_target = self.dataStore.get('url-target:' + short_id)
        if link_target is None:
            raise NotFound()
        self.dataStore.incr('click-count:' + short_id)
        return redirect(link_target)

    def on_short_link_details(self, request, short_id):
        link_target = self.dataStore.get('url-target:' + short_id)
        if link_target is None:
            raise NotFound()
        click_count = int(self.dataStore.get('click-count:' + short_id) or 0)
        return self.render_template('short_link_details.html',
                                    link_target=link_target,
                                    short_id=short_id,
                                    click_count=click_count
                                    )

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def is_valid_url(url):
    parts = urlparse.urlparse(url)
    return parts.scheme in ('http', 'https')


def base36_encode(number):
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append('0123456789abcdefgh1jklmnopqrstuvwxyz'[i])
    return ''.join(reversed(base36))


def create_app(redis_host='', redis_port=0, with_static=True):
    redisDataStore = RedisDataStore(redis_host=redis_host,
                                    redis_port=redis_port)
    app = Shortly(dataStore=redisDataStore)
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


config = {
    'redis_host': os.environ.get('XYVIO_REDIS_HOST') or 'redis.xiryvella.net',
    'redis_port': os.environ.get('XYVIO_REDIS_PORT') or 12783
}

app = create_app(**config)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app(**config)
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
