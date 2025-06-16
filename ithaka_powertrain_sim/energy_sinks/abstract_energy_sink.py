from abc import ABC, abstractmethod


class AbstractEnergySink(ABC):
    """
    This is an abstract base class for energy sinks.
    """

    @abstractmethod
    def calculate_energy_required(
        self,
        current_mass: float,
        current_speed: float,
        target_next_speed: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> float:
        """
        Parameters
        ----------
        current_mass : float
            The current mass of the object in kilograms.

        current_speed : float
            The current speed of the object in meters per second.

        target_next_speed : float
            The target speed of the object for the next time step in meters per second.

        delta_distance : float
            The change in distance traveled by the object in meters.

        delta_elevation : float
            The change in elevation of the object in meters.

        Returns
        -------
        float
            The amount of energy required by the object for the given parameters, in joules.
        """
        ...
