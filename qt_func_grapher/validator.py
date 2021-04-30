class LimitsValidator:
    """
    A class to validate input limits to the graph.

    ...

    Attributes
    ----------
    lower_limit : str
        The minimum number to evaluate
    upper_limit : str
        The maximum number to evaluate

    Methods
    -------
    parse(name)
        Get the floating-point value of the string
    """

    def __init__(self, lower_limit, upper_limit):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def parse(self, name):
        """Get the floating-point value of the string

        Parameters
        ----------
        name : str
            The limit as input by user

        Returns
        -------
        float
            The floating-point equivalent of the input string

        Raises
        ------
        ValueError
            If the input is not a valid number
        """

        try:
            self[name] = float(self[name])
            return self[name]
        except ValueError:
            raise ValueError(f"{name} is not a valid number")

    def validate(self):
        """Check whether the limits are valid

        Raises
        ------
        ValueError
            If the lower limit is greater than the upper limit
        """

        if (
            isinstance(self.lower_limit, float)
            and isinstance(self.upper_limit, float)
            and self.lower_limit >= self.upper_limit
        ):
            raise ValueError("From is greater than To")

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)