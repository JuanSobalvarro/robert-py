from typing import List, Any
import zmq
from robert.protocol import Commands, RobTarget

class RobeRTClient:
    def __init__(self, endpoint: str, timeout: int = 5000):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.endpoint = endpoint

    def connect(self):
        self.socket.connect(self.endpoint)

    def _request(self, message: str) -> str:
        try:
            self.socket.send_string(message)
            
            response = self.socket.recv_string()

            return response
        except zmq.Again:
            return "ERROR: Timeout while waiting for response"

    def _format_message(self, elements: List[Any]) -> str:
        """
        This method formats a list of elements into a string message that can be sent to the server. in the format of
        "e1|e2|...|en" where e1, e2, ..., en are the string representations of the elements in the list. Always starting with the command as the first element. 
        For example, if the command is "MOVEJ" and the target is a RobTarget object, the message would be "MOVEJ|target"
        * Important: Each element should have a __str__ method that returns a string representation of the element.
        """
        return "|".join(str(element) for element in elements if element is not None)

    def movej(self, target: RobTarget) -> str:
        return self._request(self._format_message([Commands.MOVEJ, target]))

    def ping(self) -> str:
        return self._request(self._format_message([Commands.PING]))