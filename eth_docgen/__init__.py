
import sys, argparse
from argparse import ArgumentTypeError
from .docgen import generate_docs, compile_and_generate

def error_exit(message):
    print('\n{}\n'.format(message))
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Ethereum HTML Document Generator", epilog="\n\n")
    parser.add_argument("-o", "--output", metavar='file', help="Output file")

    parser.add_argument("-a", "--abi", metavar='file', help="Contract abi", required=True)

    parser.add_argument("-m", "--metadata", metavar='file', help="Contract metadata", required=True)

    args = parser.parse_args()
    
    output = open(args.output, 'w') if args.output else sys.stdout
    abi = args.abi
    metadata = args.metadata

    generate_docs(abi, metadata, output)

    if output is not sys.stdout:
        output.close()
