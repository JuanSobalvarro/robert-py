# RobeRT Client
This is the python client for RobeRT (middleware for ABB robots)

# protoc
python -m grpc_tools.protoc --proto_path=./protocol --python_out=./src/robert/generated --pyi_out=./src/robert/generated ./protocol/protocol.proto
