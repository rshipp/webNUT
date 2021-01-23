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

                        ups_list[ups+'@'+v.host] = {
                            'name': ups,
                            'server': k,
                            'description': client.description(ups),
                            'status': self._get_ups_status(ups_vars),
                            'battery': ups_vars.get('battery.charge', '--')
                        }
            return ups_list
        except nut2.PyNUTError:
            return dict()

    def get_ups_name(self, ups):
        try:
            (name, host) = ups.split('@')
            server = self.servers[host]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                    login=server.username, password=server.password) as client:
                return client.list_ups()[name]
        except nut2.PyNUTError:
            return dict()

    def get_ups_vars(self, ups):
        try:
            (name, host) = ups.split('@')
            server = self.servers[host]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                    login=server.username, password=server.password) as client:
                ups_vars = client.list_vars(name)
                for var in ups_vars:
                    ups_vars[var] = (ups_vars[var],
                            client.var_description(name, var))
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
            status = Status('check', 'green', 'Online')
        elif status.startswith('OB'):
            status = Status('warning', 'orange', 'On Battery')
        elif status.startswith('LB'):
            status = Status('warning', 'red', 'Low Battery')
        return status
