import os

from pyramid.exceptions import NotFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import FileResponse

from .webnut import WebNUT
from .webnut import NUTServer

from . import config


class NUTViews(object):
    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        # Backward compatible support for single server configuration
        servers = []
        if hasattr(config, 'servers'):
            servers = config.servers
        if (hasattr(config, 'server') and hasattr(config, 'port') and
                hasattr(config, 'username') and hasattr(config, 'password')):
            servers.append(NUTServer(config.server, config.port,
                                     config.username, config.password))
        self.webnut = WebNUT(servers)

    @view_config(route_name="favicon")
    def favicon_view(self):
        here = os.path.dirname(__file__)
        icon = os.path.join(here, "static", "favicon.ico")
        return FileResponse(icon, request=self.request)

    @view_config(route_name='home', renderer='templates/index.pt')
    def home(self):
        ups_list = self.webnut.get_ups_list()
        # Update some list values with custom HTML rendering.
        for (_, ups_vars) in ups_list.items():
            ups_vars['status'] = self._ups_status(ups_vars['status'])
            ups_vars['battery'] = self._ups_battery(ups_vars['battery'])
        return dict(title='UPS Devices', ups_list=ups_list)

    @view_config(route_name='ups_view', renderer='templates/ups_view.pt')
    def ups_view(self):
        ups = self.request.matchdict['ups']
        try:
            ups_name = self.webnut.get_ups_name(ups)
            ups_vars = self.webnut.get_ups_vars(ups)
            ups_status = ups_vars.get('ups.status', ('Unknown', ''))[0]
            ups_battery = int(ups_vars.get('battery.charge', (0, ''))[0])
            return dict(title=ups_name, ups_vars=ups_vars,
                        ups_status=self._ups_status(ups_status),
                        ups_battery=self._ups_battery(ups_battery))
        except KeyError:
            raise NotFound

    def _ups_status(self, status):
        class Status(object):
            # Allows Chameleon to print unescaped HTML.
            def __init__(self, icon, color, title):
                self.icon = icon
                self.color = color
                self.title = title

            def __html__(self):
                return '<i class="fa fa-{0}" style="color:{1}" title="{2}"></i>'.format(
                    self.icon, self.color, self.title)

        if status.startswith('OL'):
            return Status('check', 'green', 'Online')
        elif status.startswith('OB'):
            return Status('warning', 'orange', 'On Battery')
        elif status.startswith('LB'):
            return Status('warning', 'red', 'Low Battery')
        return Status('unknown', 'black', 'Unknown')

    def _ups_battery(self, charge):

        class Status(object):
            # Allows Chameleon to print unescaped HTML.
            def __init__(self, charge, color):
                self.charge = charge
                self.color = color

            def __html__(self):
                height = 20
                return '''
                <div class="progress position-relative" style="height:{0}px;background-color:silver;line-height:{0}px;">
                    <div class="progress-bar {1}"
                        style="width:{2}%;color:black"
                        role="progressbar";
                        aria-valuenow="{2}"
                        aria-valuemin="0"
                        aria-valuemax="100"></div>
                    <span title="{2}%" class="justify-content-center align-middle d-flex position-absolute w-100">{2}%</span>
                </div>
                '''.format(height, self.color, self.charge)

        if charge > 90:
            return Status(charge, 'bg-success')
        elif charge > 60:
            return Status(charge, 'bg-warning')
        else:
            return Status(charge, 'bg-danger')


def notfound(request):
    request.response.status = 404
    return dict(title='No Such UPS')
