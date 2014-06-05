import nut2


class WebNUT(object):
    def __init__(self, server='127.0.0.1', port=3493, username=None, password=None):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def get_ups_list(self):
        try:
            with nut2.PyNUTClient(host=self.server, port=self.port,
                    login=self.username, password=self.password) as client:
                ups_dict = client.list_ups()
                ups_list = dict()
                for ups in ups_dict:
                    try:
                        ups_vars = client.list_vars(ups)
                    except nut2.PyNUTError:
                        continue

                    ups_list[ups] = {
                        'description': client.description(ups),
                        'status': self._get_ups_status(ups_vars),
                        'battery': ups_vars['battery.charge'],
                    }
                return ups_list
        except nut2.PyNUTError:
            return dict()

    def get_ups_name(self, ups):
        try:
            with nut2.PyNUTClient(host=self.server, port=self.port,
                    login=self.username, password=self.password) as client:
                return client.list_ups()[ups.encode('utf-8')]
        except nut2.PyNUTError:
            return dict()

    def get_ups_vars(self, ups):
        try:
            with nut2.PyNUTClient(host=self.server, port=self.port,
                    login=self.username, password=self.password) as client:
                ups_vars = client.list_vars(ups.encode('utf-8'))
                for var in ups_vars:
                    ups_vars[var] = (ups_vars[var],
                            client.var_description(ups.encode('utf-8'), var.encode('utf-8')))
                return (ups_vars, self._get_ups_status(ups_vars))
        except nut2.PyNUTError:
            return (dict(), str())


    def _get_ups_status(self, ups_vars):
        status = ups_vars['ups.status']
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
        return status
