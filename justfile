
default:
    just --list

[group('setup')]
install:
    pip install -e .[dev]

[group('setup')]
proto:
    python -m grpc_tools.protoc -I=protocol protocol.proto --python_out=src/robert/generated --pyi_out=src/robert/generated
