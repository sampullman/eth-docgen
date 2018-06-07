
class Contract:

    def __init__(self, source, info):
        self.source = source
        self.source_lines = source.split('\n')
        self.parents = []
        self.pragmas = []
        self.name = None
        self.docs = None
        self.abi = info['abi']
        self.bytecode = info['bin']
        self.metadata = info['metadata']
        self.meta_doc = self.metadata['output']
        self.compiler_version = self.metadata['compiler']['version']

    def add_pragma(self, pragma):
        self.pragmas.append(pragma)