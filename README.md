# RobeRT Client
This is the python client for RobeRT (middleware for ABB robots)

# protoc
python -m grpc_tools.protoc --proto_path=./protocol --python_out=./src/robert/generated --pyi_out=./src/robert/generated ./protocol/protocol.proto

# Generate docs
```bash
sphinx-build -b html docs/source docs/build/html
```

Then to generate api docs, run:
```bash
cd docs/
make html
```

# Deploying
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

# Compiling package
