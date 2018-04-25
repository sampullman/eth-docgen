from os import path
from eth_docgen import compile_contract, generate_docs

here = path.abspath(path.dirname(__file__))
print(here)

if __name__ == '__main__':
    [source, info, ast] = compile_contract(path.join(here, 'examples/Example.sol'))
    generate_docs(source, info, ast, path.join(here, 'examples/build/'))