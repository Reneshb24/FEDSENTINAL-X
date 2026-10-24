"""
FedSentinel role-based access control definitions.
"""

from enum import Enum


class Role(str, Enum):
    """
    Roles supported by the FedSentinel security control plane.
    """

    SUPER_ADMIN = "SUPER_ADMIN"

    ADMIN = "ADMIN"

    SECURITY_ANALYST = "SECURITY_ANALYST"

    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"

    HOSPITAL_OPERATOR = "HOSPITAL_OPERATOR"