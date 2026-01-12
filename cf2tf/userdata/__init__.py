"""
CF2TF User Data Helper Module

Provides templates and utilities for generating EC2 user data scripts
for common VM customization scenarios.
"""

from cf2tf.userdata.generator import UserDataGenerator
from cf2tf.userdata.templates import (
    USERDATA_TEMPLATES,
    get_template,
    list_templates,
)

__all__ = [
    "UserDataGenerator",
    "USERDATA_TEMPLATES",
    "get_template",
    "list_templates",
]
