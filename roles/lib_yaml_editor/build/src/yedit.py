# pylint: skip-file

class YeditException(Exception):
    ''' Exception class for Yedit '''
    pass

class Yedit(object):
    ''' Class to modify yaml files '''

    def __init__(self, filename=None, content=None):
        self.content = content
        self.filename = filename
        self.__yaml_dict = content
        if self.filename and not self.content:
            self.get()
        elif self.filename and self.content:
            self.write()

    @property
    def yaml_dict(self):
        ''' getter method for yaml_dict '''
        return self.__yaml_dict

    @yaml_dict.setter
    def yaml_dict(self, value):
        ''' setter method for yaml_dict '''
        self.__yaml_dict = value

    @staticmethod
    def remove_entry(data, keys):
        ''' remove an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            keys = a.b
            item = c
        '''
        if "." in keys:
            key, rest = keys.split(".", 1)
            if key in data.keys():
                Yedit.remove_entry(data[key], rest)
        else:
            del data[keys]

    @staticmethod
    def add_entry(data, keys, item):
        ''' Add an item to a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            keys = a.b
            item = c
        '''
        if "." in keys:
            key, rest = keys.split(".", 1)
            if key not in data:
                data[key] = {}

            if not isinstance(data, dict):
                raise YeditException('Invalid add_entry called on a [%s] of type [%s].' % (data, type(data)))
            else:
                Yedit.add_entry(data[key], rest, item)

        else:
            data[keys] = item


    @staticmethod
    def get_entry(data, keys):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            keys = a.b
            return c
        '''
        if keys and "." in keys:
            key, rest = keys.split(".", 1)
            if not isinstance(data[key], dict):
                raise YeditException('Invalid get_entry called on a [%s] of type [%s].' % (data, type(data)))

            else:
                return Yedit.get_entry(data[key], rest)

        else:
            return data.get(keys, None)


    def write(self):
        ''' write to file '''
        if not self.filename:
            raise YeditException('Please specify a filename.')

        with open(self.filename, 'w') as yfd:
            yfd.write(yaml.safe_dump(self.yaml_dict, default_flow_style=False))

    def read(self):
        ''' write to file '''
        # check if it exists
        if not self.exists():
            return None

        contents = None
        with open(self.filename) as yfd:
            contents = yfd.read()

        return contents

    def exists(self):
        ''' return whether file exists '''
        if os.path.exists(self.filename):
            return True

        return False

    def get(self):
        ''' return yaml file '''
        contents = self.read()

        if not contents:
            return None

        # check if it is yaml
        try:
            self.yaml_dict = yaml.load(contents)
        except yaml.YAMLError as _:
            # Error loading yaml
            return None

        return self.yaml_dict

    def delete(self, key):
        ''' put key, value into a yaml file '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, key)
        except KeyError as _:
            entry = None
        if not entry:
            return  (False, self.yaml_dict)

        Yedit.remove_entry(self.yaml_dict, key)
        self.write()
        return (True, self.get())

    def put(self, key, value):
        ''' put key, value into a yaml file '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, key)
        except KeyError as _:
            entry = None

        if entry == value:
            return (False, self.yaml_dict)

        Yedit.add_entry(self.yaml_dict, key, value)
        self.write()
        return (True, self.get())

    def create(self, key, value):
        ''' create the file '''
        if not self.exists():
            self.yaml_dict = {key: value}
            self.write()
            return (True, self.get())

        return (False, self.get())
