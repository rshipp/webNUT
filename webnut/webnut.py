import nut2
import datetime

# Some NUT variables don't have descriptions. This adds additional
# descriptions for variables that return "Description unavailable".
DEFAULT_DESCRIPTIONS = {
    "device.mfr": "Device manufacturer",
    "device.model": "Device model",
    "device.serial": "Device serial number",
    "device.type": "Device type",
    # "driver.parameter.mode": "",
    "driver.parameter.pollfreq": "Polling frequency",
    # "driver.parameter.pollinterval": "",
    # "driver.parameter.port": "",
    # "driver.parameter.synchronous": "",
    "driver.version.data": "Driver version - Additional data",
}


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

    def get_ups_name(self, ups: str):
        """Return the name of a UPS."""
        try:
            (ups_name, ups_server) = self._get_ups(ups)
            if not ups_name:
                return ''
            server = self.servers[ups_server]
            with nut2.PyNUTClient(host=server.host, port=server.port,
                                  login=server.username, password=server.password) as client:
                return client.list_ups()[ups_name]
        except nut2.PyNUTError:
            return ''

    def get_ups_vars(self, ups: str):
        """Returns a dict containing a (value, description) tuple for each UPS variable."""
        (ups_name, ups_server) = self._get_ups(ups)
        if not ups_name:
            return dict()
        server = self.servers[ups_server]
        try:
            with nut2.PyNUTClient(host=server.host, port=server.port,
                                  login=server.username, password=server.password) as client:
                ups_vars = client.list_vars(ups_name)
                ups_rw_vars = client.list_rw_vars(ups_name)
                for var in ups_vars:
                    desc = client.var_description(ups_name, var)
                    if desc == "Description unavailable" and var in DEFAULT_DESCRIPTIONS:
                        desc = DEFAULT_DESCRIPTIONS[var]
                    ups_vars[var] = (ups_vars[var], desc, var in ups_rw_vars)
                return ups_vars
        except nut2.PyNUTError:
            return dict()

    def _get_ups(self, ups: str):
        id = ups.split('@')
        if len(id) != 2:
            return (None, None)
        return (id[0], id[1])
