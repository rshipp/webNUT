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
                    ups_vars = client.list_vars(ups)
                    status = ups_vars['ups.status']
                    if status == 'OL':
                        status = 'Online'
                    elif status == 'OB':
                        status = 'Discharging'

                    ups_list[ups] = {
                        'name': ups_dict[ups],
                        'description': client.description(ups),
                        'status': status,
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
                return client.list_vars(ups.encode('utf-8'))
        except nut2.PyNUTError:
            return dict()
