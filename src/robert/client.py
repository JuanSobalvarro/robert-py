import zmq
from robert.generated import protocol_pb2 as pb
from robert.protocol import JointTarget, RobTarget, Zone, as_pb_jointtarget, as_pb_robtarget, ServerResponse, Position, Orientation, ConfData, ExtJoint
from time import sleep
from typing import Callable, Any
from functools import wraps


def server_response(func: Callable[..., bytes]) -> Callable[..., ServerResponse]:
    """
    Decorator for each function called from the client that needs to return a `ServerResponse`

    :param func: The function to decorate
    :type func: Callable[..., bytes]
    :return: The decorated function that returns a `ServerResponse`
    :rtype: Callable[..., ServerResponse]
    """
    @wraps(func)
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
    """
    Client for interacting with the RobeRT Middleware.

    *Important*: As a user connecting to the middleware server at `ip:port`, you must first call `connect()` before any other methods.

    Then after connecting, you can start calling any method. You should always log in first, using `login()`.

    Also, as a suggestion, keep the timeout short (e.g. 5000ms) and use `wait_for_task_completion()` to check task status.
    """
    def __init__(self, ip: str, port: int, timeout: int = 5000):
        """
        Initialize the RobeRTClient with the given IP, port, and timeout.

        :param ip: The IP address of the RobeRT Middleware server.
        :type ip: str
        :param port: The port of the RobeRT Middleware server.
        :type port: int
        :param timeout: The timeout for socket operations, in milliseconds.
        :type timeout: int
        :raises RuntimeError: If the connection to the server fails.
        :return: None
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.endpoint = f"tcp://{ip}:{port}"
        self.session_token: str | None = None

    def connect(self):
        """
        Connect to the RobeRT Middleware server. ALWAYS call this before any other method.
        """
        try:
            print(f"[*] Connecting to RobeRT Middleware at {self.endpoint}...")
            self.socket.connect(self.endpoint)
        except Exception as e:
            raise RuntimeError(f"API ERROR: Failed to connect to {self.endpoint} - {str(e)}")

    def _request(self, payload: bytes) -> bytes:
        """
        Send a request to the RobeRT Middleware server and return the response. This is used internally by other methods.

        :param payload: The request payload to send.
        :type payload: bytes
        :return: The response from the server.
        :rtype: bytes
        """
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

    def _create_request(self, command: pb.CommandType, **kwargs: Any) -> pb.ClientRequest:
        """
        Create a ClientRequest message with the given command and optional keyword arguments.

        :param command: The command to send.
        :type command: pb.CommandType
        :param kwargs: Optional keyword arguments for the command.
        :type kwargs: Any
        :return: The created ClientRequest message.
        :rtype: pb.ClientRequest
        """
        req = pb.ClientRequest(command=command, **kwargs)

        if command != pb.CommandType.LOGIN:
            if not self.session_token:
                raise RuntimeError("API ERROR: Unauthorized. You must log in first.")
            req.session_token = self.session_token
        return req

    def login(self, username: str, password: str) -> ServerResponse:
        """
        Log in to the RobeRT Middleware server with the given username and password.

        :param username: The username to log in with.
        :type username: str
        :param password: The password to log in with.
        :type password: str
        :return: The response from the server.
        :rtype: ServerResponse
        :raises RuntimeError: If the login fails.
        """
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
        """
        Log out of the RobeRT Middleware server. Always log out from the robot after using it, because you will acquire a
        hardware lock on the robot. But do not worry, since the middleware will release it automatically after a some time.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.LOGOUT)
        response_bytes = self._request(req.SerializeToString())

        pb_response = pb.ServerResponse.FromString(response_bytes)
        response = ServerResponse.from_pb(pb_response)

        if response.status == pb.ResponseStatus.SUCCESS:
            self.session_token = None
            print("[*] Logged out successfully.")

        return response

    def wait_for_task_completion(self, task_id: int | None, timeout: float = 0.5) -> ServerResponse:
        """
        Wait for the task to complete on the RobeRT Middleware server.

        :param task_id: The ID of the task to wait for.
        :type task_id: int | None
        :param timeout: The time to wait between checks, in seconds.
        :type timeout: float
        :return: The response from the server.
        :rtype: ServerResponse
        :raises RuntimeError: If the task fails or the server reports an error.
        """

        if task_id is None:
            raise RuntimeError("Task ID is None, cannot wait for completion.")
        while True:
            response = self.check_task(task_id)

            if response.status == pb.ResponseStatus.ERROR:
                raise RuntimeError(f"Server reported an error: {response.error_message}")

            if response.task_status == pb.TaskStatus.TASK_COMPLETED:
                return response

            if response.task_status == pb.TaskStatus.TASK_FAILED:
                raise RuntimeError(f"Task {task_id} failed: {response.error_message}")

            sleep(timeout)

    @server_response
    def movel(self, target: RobTarget | pb.RobTarget) -> bytes:
        """
        Move the robot along a linear path to the given target.

        :param target: The target position to move to.
        :type target: RobTarget | pb.RobTarget
        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.MOVEL, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    @server_response
    def movec(self, target: RobTarget | pb.RobTarget, target2: RobTarget | pb.RobTarget) -> bytes:
        """
        Move the robot along a circular path between two targets.

        :param target: The first target position.
        :type target: RobTarget | pb.RobTarget
        :param target2: The second target position.
        :type target2: RobTarget | pb.RobTarget
        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(
            pb.CommandType.MOVEC,
            target=as_pb_robtarget(target),
            extra_target=as_pb_robtarget(target2),
        )
        return self._request(req.SerializeToString())

    @server_response
    def moveabsj(self, joint_target: JointTarget | pb.JointTarget) -> bytes:
        """
        Move the robot to the given joint target position.

        :param joint_target: The joint target position to move to.
        :type joint_target: JointTarget | pb.JointTarget
        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.MOVEABSJ, joint_target=as_pb_jointtarget(joint_target))
        return self._request(req.SerializeToString())

    @server_response
    def movej(self, target: RobTarget | pb.RobTarget) -> bytes:
        """
        Move the robot to the given target position.

        :param target: The target position to move to.
        :type target: RobTarget | pb.RobTarget
        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.MOVEJ, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    @server_response
    def move_zero(self) -> bytes:
        """
        Move the robot to the zero position.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.ZERO)
        return self._request(req.SerializeToString())

    @server_response
    def set_speed(self, speed: float) -> bytes:
        """
        Set the speed of the robot.

        :param speed: The speed to set.
        :type speed: float
        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.SETSPEED, speed=speed)
        return self._request(req.SerializeToString())

    @server_response
    def set_zone(self, zone: Zone | pb.Zone | str) -> bytes:
        """
        Set the zone of the robot.

        :param zone: The zone to set.
        :type zone: Zone | pb.Zone | str
        :return: The response from the server.
        :rtype: ServerResponse
        """
        zone_value = zone.value if isinstance(zone, Zone) else zone
        req = self._create_request(pb.CommandType.SETZONE, zone=zone_value)
        return self._request(req.SerializeToString())

    @server_response
    def ping(self) -> bytes:
        """
        Ping the server.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.PING)
        return self._request(req.SerializeToString())

    @server_response
    def ping_robot(self) -> bytes:
        """
        Ping the robot.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.PINGR)
        return self._request(req.SerializeToString())

    @server_response
    def get_status(self) -> bytes:
        """
        Get the status of the robot.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.GETSTATUS)
        return self._request(req.SerializeToString())

    @server_response
    def check_task(self, task_id: int) -> bytes:
        """
        Check the status of a task.

        :param task_id: The ID of the task to check.
        :type task_id: int
        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.CHECKTASK, task_id=task_id)
        return self._request(req.SerializeToString())

    @server_response
    def acquire(self) -> bytes:
        """
        Acquire the robot.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.ACQUIRE)
        return self._request(req.SerializeToString())

    @server_response
    def release(self) -> bytes:
        """
        Release the robot.

        :return: The response from the server.
        :rtype: ServerResponse
        """
        req = self._create_request(pb.CommandType.RELEASE)
        return self._request(req.SerializeToString())

    @server_response
    def move_l_offs(self, x: float, y: float, z: float) -> bytes:
        """
        Move the robot along a linear path with offset.

        :param x: The x offset.
        :type x: float
        :param y: The y offset.
        :type y: float
        :param z: The z offset.
        :type z: float
        :return: The response from the server.
        :rtype: ServerResponse
        """
        # dummy data for target different than pos
        target = RobTarget(trans=Position(x, y, z), rot=Orientation(0,0,0,1), robconf=ConfData(0,0,0,0), extax=ExtJoint(9e9,9e9,9e9,9e9,9e9,9e9))
        req = self._create_request(pb.CommandType.MOVEL_OFFS, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    @server_response
    def move_j_offs(self, x: float, y: float, z: float) -> bytes:
        """
        Move the robot to the given joint target position with offset.

        :param x: The x offset.
        :type x: float
        :param y: The y offset.
        :type y: float
        :param z: The z offset.
        :type z: float
        :return: The response from the server.
        :rtype: ServerResponse
        """
        # dummy data for target different than pos
        target = RobTarget(trans=Position(x, y, z), rot=Orientation(0,0,0,1), robconf=ConfData(0,0,0,0), extax=ExtJoint(9e9,9e9,9e9,9e9,9e9,9e9))
        req = self._create_request(pb.CommandType.MOVEJ_OFFS, target=as_pb_robtarget(target))
        return self._request(req.SerializeToString())

    def close(self):
        """Close the socket and terminate the ZMQ context."""
        if hasattr(self, 'socket') and self.socket:
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
        if hasattr(self, 'context') and self.context:
            self.context.term()

    def __enter__(self):
        """
        Enter the context manager. This is a great solution to handling automatically the connection and logout.

        Example:
        >>> with RobeRTClient("192.168.1.1", 42069) as client:
        ...     pass
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session_token:
            try:
                self.logout()
            except Exception as e:
                print(f"[WARN] Could not gracefully logout during cleanup: {e}")

        self.close()
