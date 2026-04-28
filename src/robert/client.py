import zmq
from robert.generated import protocol_pb2 as pb 
from robert.protocol import JointTarget, RobTarget, Zone, as_pb_jointtarget, as_pb_robtarget, ServerResponse

from typing import Callable


def server_response(func: Callable[..., bytes]) -> Callable[..., ServerResponse]:
    def wrapper(self, *args, **kwargs) -> ServerResponse:
        try:
            response_bytes = func(self, *args, **kwargs)
            if not response_bytes:
                raise RuntimeError("API ERROR: Received empty response from server")
            pb_response = pb.ServerResponse.FromString(response_bytes)
            return ServerResponse.from_pb(pb_response)
        except Exception as e:
            raise RuntimeError(f"API ERROR: Failed to process server response - {str(e)}")
    return wrapper

class RobeRTClient:
    def __init__(self, endpoint: str, timeout: int = 35000):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.endpoint = endpoint

    def connect(self):
        try:
            print(f"[*] Connecting to RobeRT Middleware at {self.endpoint}...")
            self.socket.connect(self.endpoint)
            print("[*] Connection established.")
        except Exception as e:
            raise RuntimeError(f"API ERROR: Failed to connect to {self.endpoint} - {str(e)}")

    def _request(self, payload: bytes) -> bytes:
        try:
            self.socket.send(payload)
        except Exception as e:
            raise RuntimeError(f"API ERROR: Failed to send message - {str(e)}")
            
        try:
            return self.socket.recv()
        except Exception as e:
            raise RuntimeError(f"API ERROR: Timeout while waiting for response - {str(e)}")

    @server_response
    def movel(self, target: RobTarget | pb.RobTarget) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.MOVEL, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())
        
    @server_response
    def movec(self, target: RobTarget | pb.RobTarget, target2: RobTarget | pb.RobTarget) -> bytes:
        req = pb.ClientRequest(
            command=pb.CommandType.MOVEC,
            target=as_pb_robtarget(target),
            extra_target=as_pb_robtarget(target2),
        )
        return self._request(req.SerializeToString())

    @server_response
    def moveabsj(self, joint_target: JointTarget | pb.JointTarget) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.MOVEABSJ, joint_target=as_pb_jointtarget(joint_target))
        return self._request(req.SerializeToString())

    @server_response
    def movej(self, target: RobTarget | pb.RobTarget) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.MOVEJ, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    @server_response
    def move_zero(self) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.ZERO)
        return self._request(req.SerializeToString())

    @server_response
    def set_speed(self, speed: float) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.SETSPEED, speed=speed)
        return self._request(req.SerializeToString())

    @server_response
    def set_zone(self, zone: Zone | pb.Zone | str) -> bytes:
        zone_value = zone.value if isinstance(zone, Zone) else zone
        req = pb.ClientRequest(command=pb.CommandType.SETZONE, zone=zone_value)
        return self._request(req.SerializeToString())

    @server_response
    def ping(self) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.PING)
        return self._request(req.SerializeToString())

    @server_response
    def ping_robot(self) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.PINGR)
        return self._request(req.SerializeToString())
        
    @server_response
    def get_status(self) -> bytes:
        req = pb.ClientRequest(command=pb.CommandType.GETSTATUS)
        return self._request(req.SerializeToString())
