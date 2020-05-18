from pyramid.exceptions import NotFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config

from .webnut import WebNUT
from . import config

class NUTViews(object):
    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        self.webnut = WebNUT(config.server, config.port,
                config.username, config.password)

    @view_config(route_name='home', renderer='templates/index.pt')
    def home(self):
        return dict(title='UPS Devices',
                ups_list=self.webnut.get_ups_list())

    @view_config(route_name='ups_view', renderer='templates/ups_view.pt')
    def ups_view(self):
        ups = self.request.matchdict['ups']
        try:
            ups_name = self.webnut.get_ups_name(ups)
            ups_vars = self.webnut.get_ups_vars(ups)
            return dict(title=ups_name, ups_vars=ups_vars[0],
                    ups_status=ups_vars[1])
        except KeyError:
            raise NotFound

def notfound(request):
    request.response.status = 404
    return dict(title='No Such UPS')
