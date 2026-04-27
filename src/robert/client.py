import zmq
from robert.generated import protocol_pb2 as pb 
from robert.protocol import RobTarget, Zone, as_pb_robtarget

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
            print(f"API ERROR: Failed to connect to {self.endpoint} - {str(e)}")
            raise e

    def _request(self, payload: bytes) -> str:
        try:
            self.socket.send(payload)
        except Exception as e:
            return f"API ERROR: Failed to send message - {str(e)}"
            
        try:
            response = self.socket.recv().decode('utf-8')
            return response
        except Exception as e:
            return f"API ERROR: Timeout while waiting for response - {str(e)}"

    def movel(self, target: RobTarget | pb.RobTarget) -> str:
        try:
            req = pb.ClientRequest(command=pb.MOVEL, target=as_pb_robtarget(target))
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send movel command - {str(e)}"
        
    def movec(self, target: RobTarget | pb.RobTarget, target2: RobTarget | pb.RobTarget) -> str:
        try:
            req = pb.ClientRequest(
                command=pb.MOVEC,
                target=as_pb_robtarget(target),
                extra_target=as_pb_robtarget(target2),
            )
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send movec command - {str(e)}"

    def moveabsj(self, joint_target: pb.JointTarget) -> str:
        try:
            req = pb.ClientRequest(command=pb.MOVEABSJ, joint_target=joint_target)
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send moveabsj command - {str(e)}"

    def movej(self, target: RobTarget | pb.RobTarget) -> str:
        try:
            req = pb.ClientRequest(command=pb.MOVEJ, target=as_pb_robtarget(target))
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send movej command - {str(e)}"

    def move_zero(self) -> str:
        try:
            req = pb.ClientRequest(command=pb.ZERO)
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send zero command - {str(e)}"

    def set_speed(self, speed: float) -> str:
        try:
            req = pb.ClientRequest(command=pb.SETSPEED, speed=speed)
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send setspeed command - {str(e)}"

    def set_zone(self, zone: Zone | pb.Zone | str) -> str:
        try:
            zone_value = zone.name if isinstance(zone, Zone) else zone
            req = pb.ClientRequest(command=pb.SETZONE, zone=zone_value)
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send setzone command - {str(e)}"

    def ping(self) -> str:
        try:
            req = pb.ClientRequest(command=pb.PING)
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send ping command - {str(e)}"

    def ping_robot(self) -> str:
        try:
            req = pb.ClientRequest(command=pb.PINGR)
            return self._request(req.SerializeToString())
        except Exception as e:
            return f"API ERROR: Failed to send pingr command - {str(e)}"