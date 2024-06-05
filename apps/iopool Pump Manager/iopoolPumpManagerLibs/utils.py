import re


def isEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant entity.

    Parameters:
        value (str): The value to be checked.

    Returns:
        str: The input value if it is in the correct format.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    if re.match(r"^(([a-z_]+)\.([a-z0-9_]+))(\.(([a-z0-9_]+)(\[([a-z0-9_]+)\])?)+)?$", value) is None:
        raise ValueError("Value must be a valid HA sensor format")
    return value


def isSpecificEntityFormat(value: str, format: str) -> str:
    """
    Checks if the given value is in a specific entity format.

    Args:
        value (str): The value to be checked.
        format (str): The specific entity format.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the specified entity format.
    """
    value = isEntityFormat(value)
    if not value.startswith(f"{format}."):
        raise ValueError(f"Value must be a valid HA {format} entity")
    return value


def isSensorEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant sensor entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, "sensor")


def isSwitchEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant switch entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, "switch")


def isInputSelectEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant Input_Select entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, "input_select")


def isTimerEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant Timer entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, "timer")


def isSlotNameFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a slot.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    if re.match(r"^slot[0-9]+$", value) is None:
        raise ValueError("Value must be a valid slot format. Example: slot1, slot2, ...")
    return value
