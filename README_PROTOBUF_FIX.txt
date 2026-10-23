Protobuf fixes:
1. MajorLoginRes uses an isolated descriptor pool and no global registration.
2. main.py sets PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python before protobuf imports to support legacy MajoRLoGinrEq_pb2.
Tested: simultaneous imports of thunderFF_pb2, MajorLoginRes_pb2, MajoRLoGinrEq_pb2 on Python 3.13 protobuf 6.33.6.
Full bot / game server not tested.
Extract to a NEW folder and run python main.py.
