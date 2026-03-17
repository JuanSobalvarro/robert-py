from typing import List, Any
import zmq
from robert.protocol import Commands, RobTarget, Zone, RobJoint

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
            print(f"FRONTEND ERROR: Failed to connect to {self.endpoint} - {str(e)}")
            raise e

    def _request(self, message: str) -> str:
        try:
            self.socket.send_string(message)
        except Exception as e:
            return f"FRONTEND ERROR: Failed to send message - {str(e)}"
            
        try:
            response = self.socket.recv_string()

            return response
        except zmq.Again:
            return "FRONTEND ERROR: Timeout while waiting for response"

    def _format_message(self, elements: List[Any]) -> str:
        """
        This method formats a list of elements into a string message that can be sent to the server. in the format of
        "e1|e2|...|en" where e1, e2, ..., en are the string representations of the elements in the list. Always starting with the command as the first element. 
        For example, if the command is "MOVEJ" and the target is a RobTarget object, the message would be "MOVEJ|target"
        * Important: Each element should have a __str__ method that returns a string representation of the element.
        """
        return "|".join(str(element) for element in elements if element is not None)
    
    def moveabsj(self, target: RobJoint) -> str:
        try:
            response = self._request(self._format_message([Commands.MOVEABSJ, target]))
            return response
        except Exception as e:
            return f"FRONTEND ERROR: Failed to send moveabsj command - {str(e)}"

    def movej(self, target: RobTarget) -> str:
        try:
            response = self._request(self._format_message([Commands.MOVEJ, target]))
            return response
        except Exception as e:
            return f"FRONTEND ERROR: Failed to send movej command - {str(e)}"

    def set_speed(self, speed: float) -> str:
        try:
            response = self._request(self._format_message([Commands.SETSPEED, speed]))
            return response
        except Exception as e:
            return f"FRONTEND ERROR: Failed to send setspeed command - {str(e)}"

    def set_zone(self, zone: Zone) -> str:
        try:
            response = self._request(self._format_message([Commands.SETZONE, zone]))
            return response
        except Exception as e:
            return f"FRONTEND ERROR: Failed to send setzone command - {str(e)}"

    def ping(self) -> str:
        try:
            response = self._request(self._format_message([Commands.PING]))
            return response
        except Exception as e:
            return f"FRONTEND ERROR: Failed to send ping command - {str(e)}"