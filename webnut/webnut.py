import nut2
import datetime


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
        """Return a dict containing a dict of properties for each UPS."""
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

                        runtime = str(datetime.timedelta(
                            seconds=int(ups_vars.get('battery.runtime', 0))))
                        ups_list[ups+'@'+v.host] = {
                            'name': ups,
                            'server': k,
                            'description': client.description(ups),
                            'status': ups_vars.get('ups.status', 'Unknown'),
                            'battery': int(ups_vars.get('battery.charge', 0)),
                            'runtime': runtime,
                        }
            return ups_list
        except nut2.PyNUTError:
            return dict()

    def get_ups_name(self, ups):
        """Return the name of a UPS."""
        try:
            id = ups.split('@')
            if len(id) != 2:
                return ''
            server = self.servers[id[1]]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                                  login=server.username, password=server.password) as client:
                return client.list_ups()[id[0]]
        except nut2.PyNUTError:
            return ''

    def get_ups_vars(self, ups):
        """Returns a dict containing a(value, description) tuple for each UPS variable."""
        try:
            id = ups.split('@')
            if len(id) != 2:
                return dict()
            ups_name = id[0]
            server = self.servers[id[1]]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                                  login=server.username, password=server.password) as client:
                ups_vars = client.list_vars(ups_name)
                ups_rw_vars = client.list_rw_vars(ups_name)
                for var in ups_vars:
                    ups_vars[var] = (ups_vars[var],
                                     client.var_description(ups_name, var), var in ups_rw_vars)
                return ups_vars
        except nut2.PyNUTError:
            return dict()
