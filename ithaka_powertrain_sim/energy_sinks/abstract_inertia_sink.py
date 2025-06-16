from abc import ABC, abstractmethod

from .abstract_energy_sink import AbstractEnergySink


class AbstractInertiaSink(AbstractEnergySink, ABC):
    """
    Abstract class representing an inertia sink for energy calculations.

    This class extends the AbstractEnergySink class and is meant to be subclassed by specific inertia sink implementations.
    """

    @abstractmethod
    def calculate_kinetic_energy_coefficient(
        self,
        current_mass: float,
    ) -> float:
        """
        Parameters
        ----------
        current_mass : float
            The mass of the object in kilograms.

        Returns
        -------
        float
            The kinetic energy coefficient.
        """
        ...

    def calculate_energy_required(
        self,
        current_mass: float,
        current_speed: float,
        target_next_speed: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> float:
        return self.calculate_kinetic_energy_coefficient(current_mass) * (
            target_next_speed**2 - current_speed**2
        )
