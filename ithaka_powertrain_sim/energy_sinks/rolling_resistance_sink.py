from ithaka_powertrain_sim.energy_sinks import AbstractEnergySink


class RollingResistanceSink(AbstractEnergySink):
    """
    This class represents an energy sink that calculates the amount of energy required by an object due to rolling resistance.

    Parameters
    ----------
    mass_ratio : float
        The mass ratio of the object. Represents the ratio of the object's mass to the reference mass.

    coefficient_rolling_resistance : float
        The coefficient of rolling resistance. Represents the constant factor that determines the resistance to rolling motion.

    Attributes
    ----------
    _mass_ratio : float
        The mass ratio of the object.

    _coefficient_rolling_resistance : float
        The coefficient of rolling resistance.
    """

    def __init__(
        self, mass_ratio: float, coefficient_rolling_resistance: float
    ) -> None:
        super().__init__()

        self._mass_ratio = mass_ratio
        self._coefficient_rolling_resistance = coefficient_rolling_resistance

    def calculate_energy_required(
        self,
        current_mass: float,
        current_speed: float,
        target_next_speed: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> float:
        return (
            current_mass
            * self._mass_ratio
            * self._coefficient_rolling_resistance
            * 9.81
            * delta_distance
        )
