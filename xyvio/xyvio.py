# -*- coding: utf-8 -*-
import os
import urlparse
from datastore import RedisDataStore, DataManager
from controller import APIController, TemplateController
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader


class Shortly(TemplateController, DataManager):

    def __init__(self, config=None, dataStore=None):
        super(Shortly, self).__init__(dataStore=dataStore)
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.url_map = Map([
            Rule('/',
                 endpoint='on_new_url',
                 methods=['GET', 'POST']),
            Rule('/<short_id>',
                 endpoint='on_follow_short_link',
                 methods=['GET']),
            Rule('/<short_id>+',
                 endpoint='on_short_link_details',
                 methods=['GET', 'POST']),
            Rule('/list',
                 endpoint='on_list_urls',
                 methods=['GET'])
        ])

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
        short_id = self.dataStore.get("reverse-url:{0}".format(url))
        if custom_id is None and short_id is not None:
            return short_id
        elif custom_id is None or custom_id == '':
            url_num = self.dataStore.incr('last-url-id')
            short_id = base36_encode(url_num)
        else:
            short_id = custom_id
        self.dataStore.set("url-target:{0}".format(short_id), url)
        self.dataStore.set("reverse-url:{0}".format(url), short_id)
        return short_id

    def on_follow_short_link(self, request, short_id):
        link_target = self.dataStore.get("url-target:{0}".format(short_id))

        if link_target is None:
            raise NotFound()

        self.dataStore.incr("click-count:{0}".format(short_id))

        return redirect(link_target)

    def on_short_link_details(self, request, short_id):
        print(request.method)
        if request.method == 'POST':
            url = {
                'short_id': short_id,
                'url': request.form['url'],
                'custom_id': request.form['custom_id']
            }
            new_url = self.edit_url(**url)
            short_id = new_url['short_id']

        link_target = self.dataStore.get("url-target:{0}".format(short_id))

        if link_target is None:
            raise NotFound()

        click_count = int(self.dataStore.get("click-count:{0}".format(short_id)
                                             ) or 0)
        return self.render_template('short_link_details.html',
                                    link_target=link_target,
                                    short_id=short_id,
                                    click_count=click_count
                                    )

    def edit_url(self, short_id=None, url='', custom_id=None):
        if short_id is None:
            raise Exception("Can't work like this anymore")

        old_url = self.dataStore.get("url-target:{0}".format(short_id))
        is_empty_custom_id = custom_id is None or custom_id == u''
        is_new_custom_id = not is_empty_custom_id and short_id != custom_id

        if is_new_custom_id:
            self.dataStore.delete("url-target:{0}".format(short_id))
            self.dataStore.set("url-target:{0}".format(custom_id), old_url)
            self.dataStore.set("reverse-url:{0}".format(old_url), custom_id)

        current_id = self.dataStore.get("reverse-url:{0}".format(old_url))
        is_new_url = (url is not None) and (url is not u'')

        if is_new_url:
            self.dataStore.delete("reverse-url:{0}".format(old_url))
            self.dataStore.set("url-target:{0}".format(current_id), url)
            self.dataStore.set("reverse-url:{0}".format(url), current_id)

        url_key = "url-target:{0}".format(current_id)
        new_url = self.dataStore.get(url_key)
        id_key = "reverse-url:{0}".format(new_url)
        current_short_id = self.dataStore.get(id_key)

        return {
            'short_id': current_short_id,
            'url': new_url,
            'custom_id': current_short_id
        }

    def on_list_urls(self, request):
        urls = []
        urlkeys = self.dataStore.keys('url-target:*')
        for key in urlkeys:
            urls.append({
                'short_url': 'http://{0}/{1}'.format(request.host,
                                                     key.split(':')[1]),
                'target': self.dataStore.get(key),
            })
        return self.render_template('url_list.html', urls=urls)


class ShortlyAPI(APIController, DataManager):

    def __init__(self, config=None, dataStore=None):
        super(ShortlyAPI, self).__init__(dataStore=dataStore)

        self.url_map = Map([
            Rule('/', endpoint='new_url'),
            Rule('/<short_id>', endpoint='follow_short_link'),
            Rule('/<short_id>+', endpoint='short_link_details'),
            Rule('/list', endpoint='list_urls')
        ])

    def list_urls(self, request):
        urls = []
        urlkeys = self.dataStore.keys('url-target:*')
        for key in urlkeys:
            urls.append({
                'short_url': 'http://{0}/{1}'.format(request.host,
                                                     key.split(':')[1]),
                'target': self.dataStore.get(key),
            })
        return self.render(urls=urls)


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
