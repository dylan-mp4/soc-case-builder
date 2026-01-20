"""
Server Manager - Manages Flask/WebSocket server lifecycle for Flet app.
Handles startup, shutdown, and communication with backend services.
"""

import threading
import logging
import time
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ServerManager:
    """Manages Flask and WebSocket server lifecycle."""

    def __init__(self, on_case_received: Optional[Callable] = None):
        """
        Initialize server manager.

        Args:
            on_case_received: Callback when a case is received via /receive endpoint
        """
        self.on_case_received = on_case_received
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.flask_app = None

    def start(self) -> bool:
        """Start Flask server in background thread."""
        if self.is_running:
            logger.warning("Server already running")
            return False

        try:
            self.server_thread = threading.Thread(
                target=self._run_flask_server,
                daemon=True,
            )
            self.server_thread.start()
            self.is_running = True
            logger.info("Flask server started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start Flask server: {e}")
            return False

    def stop(self) -> bool:
        """Stop Flask server."""
        if not self.is_running:
            logger.warning("Server not running")
            return False

        try:
            self.is_running = False
            logger.info("Flask server stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Flask server: {e}")
            return False

    def _run_flask_server(self):
        """Run Flask server in background thread."""
        try:
            from flask import Flask, request, jsonify
            from flask_cors import CORS

            self.flask_app = Flask(__name__)
            CORS(self.flask_app)

            # ==================== Routes ====================

            @self.flask_app.route("/receive", methods=["POST"])
            def receive_case():
                """Receive case data from external source."""
                try:
                    case_data = request.get_json()
                    if not case_data:
                        return jsonify({"error": "No data"}), 400

                    # Notify callback
                    if self.on_case_received:
                        self.on_case_received(case_data)

                    return jsonify({"status": "received"}), 200
                except Exception as e:
                    logger.error(f"Error in /receive: {e}")
                    return jsonify({"error": str(e)}), 500

            @self.flask_app.route("/session", methods=["GET"])
            def session_info():
                """Get session information."""
                return jsonify({
                    "status": "active",
                    "version": "1.0.0",
                }), 200

            @self.flask_app.route("/sl/api/send_notes", methods=["POST"])
            def send_notes():
                """Send notes to external service."""
                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({"error": "No data"}), 400

                    # Log notes
                    logger.info(f"Notes received: {data}")

                    return jsonify({"status": "sent"}), 200
                except Exception as e:
                    logger.error(f"Error in /sl/api/send_notes: {e}")
                    return jsonify({"error": str(e)}), 500

            # ==================== Start Server ====================

            # Run on port 8766 (default)
            self.flask_app.run(
                host="127.0.0.1",
                port=8766,
                debug=False,
                use_reloader=False,
                threaded=True,
            )
        except Exception as e:
            logger.error(f"Flask server error: {e}")
            self.is_running = False

    def is_server_running(self) -> bool:
        """Check if server is running."""
        return self.is_running and self.server_thread is not None and self.server_thread.is_alive()


# Global server manager instance
_server_manager: Optional[ServerManager] = None


def get_server_manager() -> ServerManager:
    """Get or create global server manager instance."""
    global _server_manager
    if _server_manager is None:
        _server_manager = ServerManager()
    return _server_manager


def start_server(on_case_received: Optional[Callable] = None) -> bool:
    """Start the Flask server."""
    manager = get_server_manager()
    manager.on_case_received = on_case_received
    return manager.start()


def stop_server() -> bool:
    """Stop the Flask server."""
    manager = get_server_manager()
    return manager.stop()


def is_running() -> bool:
    """Check if server is running."""
    manager = get_server_manager()
    return manager.is_server_running()
