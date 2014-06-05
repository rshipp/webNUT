from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('ups_view', '/{ups}')
    config.add_view('webnut.views.notfound',
            renderer='webnut:templates/404.pt',
            context='pyramid.exceptions.NotFound')
    config.scan()
    return config.make_wsgi_app()
