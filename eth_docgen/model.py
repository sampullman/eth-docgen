
class Contract:

    def __init__(self, source):
        self.source = source
        self.source_lines = source.split('\n')
        self.parents = []
        self.pragmas = []
        self.name = None
        self.docs = None

    def add_pragma(self, pragma):
        self.pragmas.append(pragma)