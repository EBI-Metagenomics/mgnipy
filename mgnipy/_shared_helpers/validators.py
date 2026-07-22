import logging

from pydantic import (
    TypeAdapter,
    ValidationError,
    conint,
)

from typing import Optional

import httpx

int_gt_adapter = TypeAdapter(conint(gt=0))


def validate_gt_int(input: int, smaller_int: int = 0) -> int:
    """
    Validates that the input integer is greater than a specified smaller integer (default is 0).
    Raises a ValueError if the validation fails.

    Parameters
    ----------
    input : int
        The integer to validate.
    smaller_int : int, optional
        The integer that the input must be greater than (default is 0).

    Returns
    -------
    int
        The validated integer if it is greater than the smaller integer.

    Raises
    ------
    ValueError
        If the input integer is not greater than the smaller integer.

    Examples
    --------
    >>> validate_gt_int(10, 5)
    10

    >>> validate_gt_int(3, 5)
    Traceback (most recent call last):
        ...
    ValueError: Int must be greater than 5: 3

    >>> validate_gt_int(1)
    1
    """
    try:
        return TypeAdapter(conint(gt=smaller_int)).validate_python(input)
    except ValidationError as e:
        raise ValueError(f"Int must be greater than {smaller_int}: {input}") from e


def validate_ge_int(input: int, smaller_int: int = 0) -> int:
    """
    Validates that the input integer is greater than or equal to a specified smaller integer (default is 0).
    Raises a ValueError if the validation fails.

    Parameters
    ----------
    input : int
        The integer to validate.
    smaller_int : int, optional
        The integer that the input must be greater than or equal to (default is 0).

    Returns
    -------
    int
        The validated integer if it is greater than or equal to the smaller integer.

    Raises
    ------
    ValueError
        If the input integer is not greater than or equal to the smaller integer.

    Examples
    --------
    >>> validate_ge_int(10, 5)
    10

    >>> validate_ge_int(3, 5)
    Traceback (most recent call last):
        ...
    ValueError: Int must be greater than or equal to 5: 3

    >>> validate_ge_int(5, 5)
    5
    """
    try:
        return TypeAdapter(conint(ge=smaller_int)).validate_python(input)
    except ValidationError as e:
        raise ValueError(
            f"Int must be greater than or equal to {smaller_int}: {input}"
        ) from e


def validate_status_code(
    response: httpx.Response,
    db: str = "MGnify",
    acc: Optional[str] = "",
    logger: Optional[logging.Logger] = None,
    raise_error: bool = False,
) -> bool:

    is_valid: bool = True

    if logger:
        feedback = logger.warning
    else:
        feedback = print

    if response.status_code == 403:
        feedback(
            f"{response.status_code}. {db} access forbidden: You do not have permission to access this {acc} resource."
        )
        is_valid = False
    elif response.status_code == 404:
        feedback(
            f"{response.status_code}. {db} record not found: The requested {acc} file may not exist or response not available at this time."
        )
        is_valid = False
    elif response.status_code == 400:
        feedback(
            f"{response.status_code}. {db} bad request: The request was invalid or cannot be processed. Check the request parameters and try again."
        )
        is_valid = False
    elif response.status_code != 200:
        feedback(f"{response.status_code}. {db} cannot access record {acc}")
        is_valid = False

    if raise_error and not is_valid:
        raise Exception(
            f"Response validation failed for {db} record {acc}. Status code: {response.status_code}"
        )
    else:
        logging.debug(
            f"Response validation for {db} record {acc} returned status code {response.status_code}. Valid: {is_valid}"
        )
        return is_valid
