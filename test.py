from os import path
from eth_docgen import compile_and_generate

here = path.abspath(path.dirname(__file__))

if __name__ == '__main__':
    compile_and_generate(path.join(here, 'examples/Example.sol'), path.join(here, 'examples/build/'))