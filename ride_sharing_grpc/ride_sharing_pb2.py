# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: ride_sharing.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'ride_sharing.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12ride_sharing.proto\x12\x0cride_sharing\"M\n\x0bRideRequest\x12\x10\n\x08rider_id\x18\x01 \x01(\t\x12\x17\n\x0fpickup_location\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65stination\x18\x03 \x01(\t\"B\n\x0cRideResponse\x12\x0f\n\x07ride_id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x11\n\tdriver_id\x18\x03 \x01(\t\"$\n\x11RideStatusRequest\x12\x0f\n\x07ride_id\x18\x01 \x01(\x05\"H\n\x12RideStatusResponse\x12\x0f\n\x07ride_id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x11\n\tdriver_id\x18\x03 \x01(\t\"7\n\x11\x41\x63\x63\x65ptRideRequest\x12\x11\n\tdriver_id\x18\x01 \x01(\t\x12\x0f\n\x07ride_id\x18\x02 \x01(\x05\"$\n\x12\x41\x63\x63\x65ptRideResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"7\n\x11RejectRideRequest\x12\x11\n\tdriver_id\x18\x01 \x01(\t\x12\x0f\n\x07ride_id\x18\x02 \x01(\x05\";\n\x12RejectRideResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x15\n\rnew_driver_id\x18\x02 \x01(\t\";\n\x15RideCompletionRequest\x12\x11\n\tdriver_id\x18\x01 \x01(\t\x12\x0f\n\x07ride_id\x18\x02 \x01(\x05\"(\n\x16RideCompletionResponse\x12\x0e\n\x06status\x18\x01 \x01(\t2\xab\x03\n\x12RideSharingService\x12\x44\n\x0bRequestRide\x12\x19.ride_sharing.RideRequest\x1a\x1a.ride_sharing.RideResponse\x12R\n\rGetRideStatus\x12\x1f.ride_sharing.RideStatusRequest\x1a .ride_sharing.RideStatusResponse\x12O\n\nAcceptRide\x12\x1f.ride_sharing.AcceptRideRequest\x1a .ride_sharing.AcceptRideResponse\x12O\n\nRejectRide\x12\x1f.ride_sharing.RejectRideRequest\x1a .ride_sharing.RejectRideResponse\x12Y\n\x0c\x43ompleteRide\x12#.ride_sharing.RideCompletionRequest\x1a$.ride_sharing.RideCompletionResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ride_sharing_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RIDEREQUEST']._serialized_start=36
  _globals['_RIDEREQUEST']._serialized_end=113
  _globals['_RIDERESPONSE']._serialized_start=115
  _globals['_RIDERESPONSE']._serialized_end=181
  _globals['_RIDESTATUSREQUEST']._serialized_start=183
  _globals['_RIDESTATUSREQUEST']._serialized_end=219
  _globals['_RIDESTATUSRESPONSE']._serialized_start=221
  _globals['_RIDESTATUSRESPONSE']._serialized_end=293
  _globals['_ACCEPTRIDEREQUEST']._serialized_start=295
  _globals['_ACCEPTRIDEREQUEST']._serialized_end=350
  _globals['_ACCEPTRIDERESPONSE']._serialized_start=352
  _globals['_ACCEPTRIDERESPONSE']._serialized_end=388
  _globals['_REJECTRIDEREQUEST']._serialized_start=390
  _globals['_REJECTRIDEREQUEST']._serialized_end=445
  _globals['_REJECTRIDERESPONSE']._serialized_start=447
  _globals['_REJECTRIDERESPONSE']._serialized_end=506
  _globals['_RIDECOMPLETIONREQUEST']._serialized_start=508
  _globals['_RIDECOMPLETIONREQUEST']._serialized_end=567
  _globals['_RIDECOMPLETIONRESPONSE']._serialized_start=569
  _globals['_RIDECOMPLETIONRESPONSE']._serialized_end=609
  _globals['_RIDESHARINGSERVICE']._serialized_start=612
  _globals['_RIDESHARINGSERVICE']._serialized_end=1039
# @@protoc_insertion_point(module_scope)
