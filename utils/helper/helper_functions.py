import contextlib
import os
from datetime import datetime
from uuid import uuid4

import MailChecker
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .blocked_domains import domain_list

# phone number validate
phone_validator = RegexValidator(
    r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
    "The phone number provided is invalid",
)


def content_file_path(instance, filename, file_extension=None):
    # Remove 'Model' from the model name if present
    model_name = instance.__class__.__name__.replace("Model", "")

    # Extract the original file extension if none is provided
    original_ext = filename.split(".")[-1]

    # Use the passed extension or the original one
    ext = file_extension if file_extension else original_ext

    # Get current date for the directory structure
    current_date = datetime.now()
    date_path = current_date.strftime("%Y-%m-%d")

    # Generate unique filename using the instance's primary key or UUID if not saved yet
    unique_filename = f"{uuid4()}-{uuid4()}.{ext}"

    # Construct the final file path
    return os.path.join(model_name, date_path, unique_filename)


def validate_email(email):
    with contextlib.suppress(IndexError):
        if (
            (host := email.rsplit("@", 1)[1]) in domain_list
            or email
            and "@" in email
            and MailChecker.MailChecker.is_blacklisted(email)
        ):
            raise ValidationError(f"Email with domain: {host} not accepted")
