import pytest
import zmq
from unittest.mock import patch, MagicMock

from robert.client import RobeRTClient
from robert.generated import protocol_pb2 as pb
from robert.protocol import ResponseStatus

def create_mock_response(status, text_payload=None, error_msg=None):
    resp = pb.ServerResponse(status=status)
    if text_payload:
        resp.text_payload = text_payload
    if error_msg:
        resp.error_message = error_msg
    return resp.SerializeToString()


@patch('robert.client.zmq.Context')
def test_login_and_session_token(mock_context):
    """Test that login correctly sets the session token."""
    mock_socket = MagicMock()
    mock_context.return_value.socket.return_value = mock_socket

    mock_socket.recv.return_value = create_mock_response(pb.SUCCESS, text_payload="super_secret_token")

    client = RobeRTClient("127.0.0.1", 42069)
    client.connect()

    assert client.session_token is None

    response = client.login("admin", "admin")

    assert client.session_token == "super_secret_token"
    assert response.status == ResponseStatus.SUCCESS


@patch('robert.client.zmq.Context')
def test_unauthorized_command_rejection(mock_context):
    """Test that the client prevents sending commands if not logged in."""
    client = RobeRTClient("127.0.0.1", 42069)

    with pytest.raises(RuntimeError, match="API ERROR: Unauthorized. You must log in first."):
        client.ping()


@patch('robert.client.zmq.Context')
def test_server_error_handling(mock_context):
    """Test that the client correctly unpacks and raises server-side errors."""
    mock_socket = MagicMock()
    mock_context.return_value.socket.return_value = mock_socket

    mock_socket.recv.side_effect = [
        create_mock_response(pb.SUCCESS, text_payload="token123"),
        create_mock_response(pb.ERROR, error_msg="Robot is in emergency stop")
    ]

    client = RobeRTClient("127.0.0.1", 42069)
    client.connect()
    client.login("admin", "admin")

    with pytest.raises(RuntimeError, match="API ERROR: Failed to process server response - Robot is in emergency stop"):
        client.ping()


@patch('robert.client.zmq.Context')
def test_context_manager_auto_logout(mock_context):
    """Test that the 'with' statement automatically logs out and closes sockets."""
    mock_socket = MagicMock()
    mock_context.return_value.socket.return_value = mock_socket

    mock_socket.recv.side_effect = [
        create_mock_response(pb.SUCCESS, text_payload="temp_token"),
        create_mock_response(pb.SUCCESS),
        create_mock_response(pb.SUCCESS)
    ]

    with RobeRTClient("127.0.0.1", 42069) as client:
        client.login("admin", "admin")
        assert client.session_token == "temp_token"
        client.ping()

    assert client.session_token is None
    mock_socket.close.assert_called_once()
    mock_context.return_value.term.assert_called_once()


@patch('robert.client.zmq.Context')
def test_socket_timeout_recovery(mock_context):
    """Test that the client handles ZeroMQ timeouts (Lazy Pirate pattern)."""
    mock_socket = MagicMock()
    mock_context.return_value.socket.return_value = mock_socket

    mock_socket.recv.side_effect = zmq.error.Again

    client = RobeRTClient("127.0.0.1", 42069, timeout=100)
    client.connect()

    with pytest.raises(RuntimeError, match="Timeout while waiting for response. Connection reset."):
        req = pb.ClientRequest(command=pb.CommandType.LOGIN)
        client._request(req.SerializeToString())

    mock_socket.close.assert_called_once()
