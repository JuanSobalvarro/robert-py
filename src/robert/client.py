import zmq
from robert.generated import protocol_pb2 as pb
from robert.protocol import JointTarget, RobTarget, Zone, as_pb_jointtarget, as_pb_robtarget, ServerResponse
from time import sleep
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
    def __init__(self, endpoint: str, timeout: int = 5000):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.endpoint = endpoint
        self.session_token: str | None = None

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
        except zmq.error.Again:
            # socket REQ is corrupt
            print("[WARN] Socket timeout. Recreating socket to restore state...")

            # avoid blocks
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()

            # recreate socket and reset timeout
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 5000)
            self.connect()

            raise RuntimeError("API ERROR: Timeout while waiting for response. Connection reset.")
        except Exception as e:
            raise RuntimeError(f"API ERROR: Unexpected error waiting for response - {str(e)}")

    def _create_request(self, command: pb.CommandType, **kwargs) -> pb.ClientRequest:
        req = pb.ClientRequest(command=command, **kwargs)

        if command != pb.CommandType.LOGIN:
            if not self.session_token:
                raise RuntimeError("API ERROR: Unauthorized. You must log in first.")
            req.session_token = self.session_token
        return req

    def login(self, username: str, password: str) -> ServerResponse:
        req = self._create_request(pb.CommandType.LOGIN, username=username, password=password)
        response_bytes = self._request(req.SerializeToString())

        pb_response = pb.ServerResponse.FromString(response_bytes)
        response = ServerResponse.from_pb(pb_response)

        # Guardar el token en el estado de la clase si fue exitoso
        if response.status == pb.ResponseStatus.SUCCESS:
            self.session_token = response.text_payload
            print("[*] Login successful. Session token acquired.")
        else:
            raise RuntimeError(f"Login failed: {response.error_message}")

        return response

    def logout(self) -> ServerResponse:
        req = self._create_request(pb.CommandType.LOGOUT)
        response_bytes = self._request(req.SerializeToString())

        pb_response = pb.ServerResponse.FromString(response_bytes)
        response = ServerResponse.from_pb(pb_response)

        if response.status == pb.ResponseStatus.SUCCESS:
            self.session_token = None
            print("[*] Logged out successfully.")

        return response

    def wait_for_task_completion(self, task_id: int | None, timeout: float = 0.5) -> ServerResponse:
        if task_id is None:
            raise RuntimeError("Task ID is None, cannot wait for completion.")
        while True:
            response = self.check_task(task_id)

            if response.status == pb.ResponseStatus.ERROR:
                raise RuntimeError(f"Server reported an error: {response.error_message}")

            if response.task_status == pb.TaskStatus.TASK_COMPLETED:
                return response

            if response.task_status == pb.TaskStatus.TASK_FAILED:
                raise RuntimeError(f"Task {task_id} failed to execute on the robot.")

            sleep(timeout)

    @server_response
    def movel(self, target: RobTarget | pb.RobTarget) -> bytes:
        req = self._create_request(pb.CommandType.MOVEL, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    @server_response
    def movec(self, target: RobTarget | pb.RobTarget, target2: RobTarget | pb.RobTarget) -> bytes:
        req = self._create_request(
            pb.CommandType.MOVEC,
            target=as_pb_robtarget(target),
            extra_target=as_pb_robtarget(target2),
        )
        return self._request(req.SerializeToString())

    @server_response
    def moveabsj(self, joint_target: JointTarget | pb.JointTarget) -> bytes:
        req = self._create_request(pb.CommandType.MOVEABSJ, joint_target=as_pb_jointtarget(joint_target))
        return self._request(req.SerializeToString())

    @server_response
    def movej(self, target: RobTarget | pb.RobTarget) -> bytes:
        req = self._create_request(pb.CommandType.MOVEJ, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    @server_response
    def move_zero(self) -> bytes:
        req = self._create_request(pb.CommandType.ZERO)
        return self._request(req.SerializeToString())

    @server_response
    def set_speed(self, speed: float) -> bytes:
        req = self._create_request(pb.CommandType.SETSPEED, speed=speed)
        return self._request(req.SerializeToString())

    @server_response
    def set_zone(self, zone: Zone | pb.Zone | str) -> bytes:
        zone_value = zone.value if isinstance(zone, Zone) else zone
        req = self._create_request(pb.CommandType.SETZONE, zone=zone_value)
        return self._request(req.SerializeToString())

    @server_response
    def ping(self) -> bytes:
        req = self._create_request(pb.CommandType.PING)
        return self._request(req.SerializeToString())

    @server_response
    def ping_robot(self) -> bytes:
        req = self._create_request(pb.CommandType.PINGR)
        return self._request(req.SerializeToString())

    @server_response
    def get_status(self) -> bytes:
        req = self._create_request(pb.CommandType.GETSTATUS)
        return self._request(req.SerializeToString())

    @server_response
    def check_task(self, task_id: int) -> bytes:
        req = self._create_request(pb.CommandType.CHECKTASK, task_id=task_id)
        return self._request(req.SerializeToString())

    @server_response
    def acquire(self) -> bytes:
        req = self._create_request(pb.CommandType.ACQUIRE)
        return self._request(req.SerializeToString())

    @server_response
    def release(self) -> bytes:
        req = self._create_request(pb.CommandType.RELEASE)
        return self._request(req.SerializeToString())
