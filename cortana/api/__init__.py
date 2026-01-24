"""API Module for Cortana"""

from cortana.api.rest_api import CortanaAPI
from cortana.api.websocket import WebSocketHandler

__all__ = ['CortanaAPI', 'WebSocketHandler']

__version__ = '1.0.0'
