import base64
import codecs
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class RoomSolver:
    @staticmethod
    def verify_header(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        user gotta send base64-encoded answer in x-secret-base header.
        decode it and compare it against the db answer. simple enough.
        """
        header_val = request_info.get("headers", {}).get("x-secret-base", "")
        try:
            decoded = base64.b64decode(header_val).decode('utf-8')
            if decoded.strip().lower() == answer.strip().lower():
                return True, "Correct."
        except Exception as e:
            logger.debug(f"Header decode failed, probably bad base64: {e}")
        return False, "The door stays shut. Look closely at your headers, they might be encoded."

    @staticmethod
    def verify_cipher(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        clue is ROT13 encoded. user decodes and submits plain text.
        """
        user_answer = request_info.get("body", {}).get("answer", "")
        expected = request_info.get("expected", "")
        if user_answer.strip().lower() == expected.strip().lower():
            return True, "Correct."
        return False, "The door stays shut. The letters seem shifted."

    @staticmethod
    def verify_method(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        The user must send the request with the correct HTTP method.
        """
        method = request_info.get("method", "").upper()
        if method == answer.upper():
            return True, "Correct."
        return False, "The door stays shut. You knocked the wrong way (check HTTP method)."

    @staticmethod
    def verify_useragent(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        The user must set User-Agent header to the expected value.
        """
        ua = request_info.get("headers", {}).get("user-agent", "")
        if ua.strip() == answer.strip():
            return True, "Correct."
        return False, "The door stays shut. Who are you? (Check User-Agent)"

    @staticmethod
    def verify_query_param(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        The user must include ?key=<answer> in the query parameters.
        """
        query_answer = request_info.get("query_params", {}).get("key", "")
        if query_answer.strip() == answer.strip():
            return True, "Correct."
        return False, "The door stays shut. There might be a query hiding."

    @staticmethod
    def verify_body_field(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        The user must include {"secret": {"key": "<answer>"}} in the request body.
        """
        body = request_info.get("body", {})
        try:
            val = body.get("secret", {}).get("key", "")
            if str(val).strip() == answer.strip():
                return True, "Correct."
        except Exception as e:
            # this happens if body isn't json or secret isn't a dict
            logger.debug(f"Body field extract failed: {e}")
        return False, "The door stays shut. Examine the payload structure."

    @staticmethod
    def verify_default(request_info: Dict[str, Any], answer: str) -> tuple[bool, str]:
        """
        Default verifier: compare user's submitted answer against expected.
        """
        user_answer = request_info.get("body", {}).get("answer", "")
        expected = request_info.get("expected", "")
        if user_answer.strip().lower() == expected.strip().lower():
            return True, "Correct."
        return False, "The door stays shut."

    @classmethod
    def get_verifier(cls, room_type: str) -> Callable:
        verifiers = {
            "header": cls.verify_header,
            "cipher": cls.verify_cipher,
            "method": cls.verify_method,
            "useragent": cls.verify_useragent,
            "query_param": cls.verify_query_param,
            "body_field": cls.verify_body_field,
            "hidden_header": cls.verify_default,
        }
        return verifiers.get(room_type, cls.verify_default)
