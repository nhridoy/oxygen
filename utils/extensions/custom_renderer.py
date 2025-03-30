import contextlib
from typing import Any, Dict, Optional, Union

from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that formats API responses into a standardized structure.
    Handles both success and error cases, with support for pagination.
    """

    def extract_base_data(self, data: Dict[str, Any]) -> tuple:
        """Extract basic fields from the response data."""
        message = ""
        errors = None

        # Handle 'detail' field which might contain ErrorDetail objects
        if "detail" in data:
            detail = data.pop("detail")
            # For error responses (like permission denied), use detail as both message and error
            message = str(detail)  # Convert ErrorDetail to string
            errors = {"detail": str(detail)}
            if hasattr(detail, "code"):
                errors["code"] = detail.code
        elif "message" in data:
            message = data.pop("message")

        # If errors field exists, extract it
        if "errors" in data and not errors:
            errors = data.pop("errors")

        final_data = data.pop("data") if "data" in data else data

        return message, errors, final_data

    def extract_pagination_data(self, data: Dict[str, Any]) -> tuple:
        """Extract pagination-related fields from the response data."""
        links = data.pop("links") if "links" in data else {}
        count = data.pop("count") if "count" in data else 0
        total_pages = data.pop("total_pages") if "total_pages" in data else 0
        results = data.pop("results") if "results" in data else data

        return links, count, total_pages, results

    def extract_error_detail(self, errors: Union[Dict, list, str]) -> Optional[str]:
        """Recursively extract the first 'detail' message from nested structure."""
        if isinstance(errors, dict):
            if "detail" in errors and isinstance(errors["detail"], str):
                return errors["detail"]

            for value in errors.values():
                if result := self.extract_error_detail(value):
                    return result

        elif isinstance(errors, list):
            for item in errors:
                if result := self.extract_error_detail(item):
                    return result

        return None

    def format_error_message(self, errors: Union[Dict, list, str]) -> Optional[str]:
        """Extract and format a meaningful error message from different structures."""
        if isinstance(errors, dict):
            for value in errors.values():
                if isinstance(value, (dict, list)):
                    if result := self.format_error_message(value):
                        return result
                elif isinstance(value, list) and value:
                    return " ".join(str(msg).replace("'", "") for msg in value)

        elif isinstance(errors, list):
            for item in errors:
                if isinstance(item, dict):
                    if result := self.format_error_message(item):
                        return result
                elif isinstance(item, str):
                    return item.replace("'", "")

        elif isinstance(errors, str):
            return errors.replace("'", "")

        return None

    def get_error_message(self, errors: Union[Dict, list, str]) -> str:
        """Get the most appropriate error message from the error data."""
        return (
            self.extract_error_detail(errors) or self.format_error_message(errors) or ""
        )

    def render(
        self,
        data: Optional[Dict],
        accepted_media_type: Optional[str] = None,
        renderer_context: Optional[Dict] = None,
    ) -> bytes:
        """
        Render the response data into a standardized format.
        """
        if data is None:
            return super().render(data, accepted_media_type, renderer_context)

        # Extract status information
        status_code = renderer_context["response"].status_code
        is_success = 200 <= status_code < 300

        # Process the data
        # Debug print to see what's coming in
        # print("Original data:", data)

        message, errors, extracted_data = self.extract_base_data(data.copy())
        links, count, total_pages, final_data = self.extract_pagination_data(
            extracted_data
        )

        # For error responses, ensure we have a message
        if not is_success and not message:
            message = self.get_error_message(extracted_data)

        # Prepare the final response
        response_data = {
            "message": message,  # Now message will have the ErrorDetail string directly
            "errors": (
                errors
                if errors is not None
                else (extracted_data if not is_success else None)
            ),
            "status": "success" if is_success else "failure",
            "status_code": status_code,
            "links": links,
            "count": count,
            "total_pages": total_pages,
            "data": [] if not is_success else final_data,
        }

        # Attempt to get resource name (suppressing any errors)
        with contextlib.suppress(Exception):
            getattr(
                renderer_context.get("view").get_serializer().Meta,
                "resource_name",
                "objects",
            )

        return super().render(response_data, accepted_media_type, renderer_context)
