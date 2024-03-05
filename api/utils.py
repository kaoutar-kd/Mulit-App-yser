import jwt
import datetime
from api.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status


def encode_token(user: User) -> str:
    """
    Encodes a JWT token with user information.

    Args:
        user (User): The user for whom the token is being generated.

    Returns:
        str: The encoded JWT token.
    """
    payload = {
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180),
        'iat': datetime.datetime.utcnow()
    }

    return jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')


def get_token(auth_header: str) -> Response:
    """
    Extracts the token from the Authorization header.

    Args:
        auth_header (str): The Authorization header containing the token.

    Returns:
        Response: A Response object with the token or an error message.
    """
    auth_header = auth_header.replace('"', '').replace("'", '')
    if auth_header.startswith('Bearer '):
        token = auth_header[len('Bearer '):]
        return Response({'token': token}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Authorization header'}, status=status.HTTP_400_BAD_REQUEST)


def decode_token(token: str) -> dict:
    """
    Decodes a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: Decoded token data.
    """
    try:
        decoded_data = jwt.decode(token, 'secret', algorithms=['HS256'])
        return decoded_data
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')


def check_access(header: dict) -> str:
    """
    Validates and retrieves the username from the Authorization header.

    Args:
        header (dict): The HTTP header containing the Authorization information.

    Returns:
        str: The username extracted from the token.

    Raises:
        AuthenticationFailed: If the token is invalid.
    """
    try:
        token = get_token(header.get('Authorization', ''))
        return decode_token(token.data['token'])['username']
    except:
        raise AuthenticationFailed()
