from .abstract_inertia_sink import AbstractInertiaSink


class AngularInertiaSink(AbstractInertiaSink):
    """
    An energy sink capturing rotational kinetic energy of a wheel of the motorbike.

    Parameters
    ----------
    angular_inertia : float
        The angular inertia of the object.

    nominal_radius : float
        The nominal radius of the object.
    """

    def __init__(self, angular_inertia: float, nominal_radius: float) -> None:
        self._angular_inertia = angular_inertia
        self._nominal_radius = nominal_radius

    @property
    def nominal_radius(self) -> float:
        """

        Returns
        -------
        float

        """
        return self._nominal_radius

    def calculate_kinetic_energy_coefficient(
        self,
        current_mass: float,
    ) -> float:
        # v = r * omega; omega^2 = v^2 / r^2
        return 0.5 * self._angular_inertia / self._nominal_radius**2
