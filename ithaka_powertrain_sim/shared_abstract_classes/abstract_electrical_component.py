from abc import ABC


class AbstractElectricalComponent(ABC):
    """
    Abstract base class for electrical components.
    """

    @property
    def is_electrical(self) -> bool:
        """
        Check if the object is electrical.

        Returns
        -------
        bool
            True if the object is electrical, False otherwise.
        """
        return True
