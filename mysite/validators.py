import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Custom password validator to enforce:
    - Minimum length of 8 characters
    - At least one capital letter
    - At least one number
    - At least one special character from the allowed set: !@#$%^&*()_+=\-{}[\]:;\"'<>,.?/
    - Cannot be only numbers
    - Cannot be only letters
    - Cannot be too common (using Django's common password list)
    """

    SPECIAL_CHARACTERS = r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]"

    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."), code="password_too_short")

        if password.isdigit():
            raise ValidationError(_("Password cannot contain only numbers."), code="password_only_numbers")

        if password.isalpha():
            raise ValidationError(_("Password cannot contain only letters."), code="password_only_letters")

        if not any(char.isdigit() for char in password):
            raise ValidationError(_("Password must contain at least one number."), code="password_no_number")

        if not any(char.isupper() for char in password):
            raise ValidationError(_("Password must contain at least one uppercase letter."), code="password_no_uppercase")

        if not re.search(self.SPECIAL_CHARACTERS, password):
            raise ValidationError(
                _("Password must contain at least one special character from: !@#$%^&*()_+=-{}[]:;\"'<>,.?/"),
                code="password_no_special"
            )

        # Check if password is too common
        from django.contrib.auth.password_validation import CommonPasswordValidator
        common_validator = CommonPasswordValidator()
        try:
            common_validator.validate(password)
        except ValidationError:
            raise ValidationError(_("Password is too common. Please choose a more secure password."), code="password_too_common")

    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, including a number, an uppercase letter, "
            "and at least one of the following special characters: !@#$%^&*()_+=-{}[]:;\"'<>,.?/"
        )
