from pydantic import (
    TypeAdapter,
    ValidationError,
    conint,
)

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
