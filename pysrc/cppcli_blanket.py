import pyblanket

class Transform(pyblanket.Transform):
    """ """
    def __init__(self, source):
        self.source = source

    def Execute(self):
        for item in self.source:
            if item['subtype'].lower() == 'interface':
                self.Interface(item)
            elif item['subtype'].lower() == 'factory':
                self.Factory(item)
            elif item['subtype'].lower() == 'class':
                self.Class(item)
            elif item['subtype'].lower() == 'enum':
                self.Enum(item)
            elif item['subtype'].lower() == 'struct':
                self.Struct(item)
            else:
                print 'Warning: unhandled type "'+ item['subtype'] +'"'

    def Interface(self, item):
        print 'interface: '+ item['name']

    def Factory(self, item):
        print 'factory: '+ item['name']

    def Class(self, item):
        print 'class: '+ item['name']

    def Enum(self, item):
        print 'enum: '+ item['name']

    def Struct(self, item):
        print 'struct: '+ item['name']
