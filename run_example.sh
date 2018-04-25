solc --combined-json abi,bin,ast,devdoc,interface,metadata,userdoc examples/Example.sol
eth-docgen -a "./examples/support/Example.json" -m "./examples/support/Example_meta.json" -o "./examples/Example.html"
