import nut2


class NUTServer(object):
    def __init__(self, host='127.0.0.1', port=3493, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password


class WebNUT(object):
    def __init__(self, servers=[]):
        self.servers = dict()
        for s in servers:
            self.servers[s.host] = s

    def get_ups_list(self):
        try:
            ups_list = dict()
            for k, v in self.servers.items():
                with nut2.PyNUTClient(host=v.host, port=v.port,
                                      login=v.username, password=v.password) as client:
                    ups_dict = client.list_ups()
                    for ups in ups_dict:
                        try:
                            ups_vars = client.list_vars(ups)
                        except nut2.PyNUTError:
                            continue

                        charge = int(ups_vars.get('battery.charge', 0))
                        ups_list[ups+'@'+v.host] = {
                            'name': ups,
                            'server': k,
                            'description': client.description(ups),
                            'status': self._get_ups_status(ups_vars),
                            'battery': self._get_battery_status(charge)
                        }
            return ups_list
        except nut2.PyNUTError:
            return dict()

    def get_ups_name(self, ups):
        try:
            id = ups.split('@')
            if len(id) != 2:
                return dict()
            server = self.servers[id[1]]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                                  login=server.username, password=server.password) as client:
                return client.list_ups()[id[0]]
        except nut2.PyNUTError:
            return dict()

    def get_ups_vars(self, ups):
        try:
            id = ups.split('@')
            if len(id) != 2:
                return (dict(), str())
            server = self.servers[id[1]]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                                  login=server.username, password=server.password) as client:
                ups_vars = client.list_vars(id[0])
                for var in ups_vars:
                    ups_vars[var] = (ups_vars[var],
                                     client.var_description(id[0], var))
                return (ups_vars, self._get_ups_status(ups_vars))
        except nut2.PyNUTError:
            return (dict(), str())

    def _get_ups_status(self, ups_vars):
        status = ups_vars.get('ups.status', 'unknown')
        if type(status) == tuple:
            status = status[0]

        class Status(object):
            # Allows Chameleon to print unescaped HTML.
            def __init__(self, icon, color, title):
                self.icon = icon
                self.color = color
                self.title = title

            def __html__(self):
                return '<i class="fa fa-%s" style="color: %s" title="%s"></i>' % (
                    self.icon, self.color, self.title)

        if status.startswith('OL'):
            return Status('check', 'green', 'Online')
        elif status.startswith('OB'):
            return Status('warning', 'orange', 'On Battery')
        elif status.startswith('LB'):
            return Status('warning', 'red', 'Low Battery')
        return Status('unknown', 'black', 'Unknown')

    def _get_battery_status(self, charge):

        class Status(object):
            def __init__(self, charge, color):
                self.charge = charge
                self.color = color

            def __html__(self):
                height = 20
                return '''
                <div class="progress" style="height:{0}px;background-color:silver">
                    <div class="progress-bar {1}" 
                        style="width:{2}%;color:black" 
                        role="progressbar" 
                        aria-valuenow="{2}" 
                        aria-valuemin="0" 
                        aria-valuemax="100">{2}%</div>
                </div>
                '''.format(height, self.color, self.charge)

        if charge > 90:
            return Status(charge, 'bg-success')
        elif charge > 60:
            return Status(charge, 'bg-warning')
        else:
            return Status(charge, 'bg-danger')
