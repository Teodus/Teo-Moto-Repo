from abc import ABC


class AbstractMechanicalComponent(ABC):
    """
    This class represents an abstract mechanical component. It defines a property `is_mechanical`
    to check if the object is mechanical.
    """

    @property
    def is_mechanical(self) -> bool:
        """
        Check if the object is mechanical.

        Returns
        --------
        bool
            True if the object is mechanical, False otherwise.
        """
        return True
