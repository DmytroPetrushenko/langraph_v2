import os
import threading

from pymetasploit3.msfrpc import MsfRpcClient

from constants import PASSWORD, HOST, PORT, SSL, FALSE


class CustomMsfRpcClient:
    _instance = None
    _lock = threading.Lock()  # Lock for thread-safe singleton initialization

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                # Create a new instance
                cls._instance = super(CustomMsfRpcClient, cls).__new__(cls)

                # Initialize environment variables
                cls._instance._get_env_vars()

                # Initialize the MsfRpcClient with the loaded environment variables
                cls._instance.client = MsfRpcClient(
                    password=cls._instance.password,
                    host=cls._instance.host,
                    port=cls._instance.port,
                    ssl=cls._instance.ssl
                )
        return cls._instance

    def get_client(self) -> MsfRpcClient:
        """
        Returns the initialized MsfRpcClient instance.

        :return: An instance of MsfRpcClient
        """
        return self.client

    def _get_env_vars(self):
        """
        Retrieves environment variables required for MsfRpcClient initialization.
        """
        self.password = os.getenv(PASSWORD)
        self.host = os.getenv(HOST)
        port_str = os.getenv(PORT)
        ssl_str = os.getenv(SSL, FALSE).lower()

        if port_str is None:
            raise ValueError("Environment variable 'PORT' is not set.")
        try:
            self.port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid PORT value: {port_str}")

        if ssl_str not in ['true', 'false']:
            raise ValueError(f"Invalid SSL value: {ssl_str}. Must be 'true' or 'false'.")
        self.ssl = ssl_str == 'true'

        # Optional: Validate that required environment variables are set
        if not all([self.password, self.host]):
            missing = [var for var in [PASSWORD, HOST] if not os.getenv(var)]
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

