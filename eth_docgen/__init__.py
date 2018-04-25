
import sys, argparse
from argparse import ArgumentTypeError
from .docgen import generate_docs, compile_contract

def error_exit(message):
    print('\n{}\n'.format(message))
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Ethereum HTML Document Generator", epilog="\n\n")
    parser.add_argument("-o", "--output", metavar='dir', help="Output directory")

    parser.add_argument("-a", "--abi", metavar='file', help="Contract abi", required=True)

    parser.add_argument("-m", "--metadata", metavar='file', help="Contract metadata", required=True)

    parser.add_argument("-s", "--style", help="Inline CSS with output HTML")

    args = parser.parse_args()
    
    output = open(args.output, 'w') if args.output else sys.stdout
    abi = args.abi
    metadata = args.metadata

    generate_docs(abi, metadata, output, inline=args.style)

    if output is not sys.stdout:
        output.close()
