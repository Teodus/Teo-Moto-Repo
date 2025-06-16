from ithaka_powertrain_sim.energy_sinks import AbstractEnergySink

_NOMINAL_AIR_DENSITY = 1.18


class AerodynamicDragSink(AbstractEnergySink):
    """
    This class represents an aerodynamic drag sink that calculates the amount of energy required by an object due to aerodynamic drag.

    Parameters
    ----------
    frontal_area : float
        The frontal area of the object, in square units.

    coefficient_of_drag : float
        The coefficient of drag of the object, a dimensionless quantity.
    """

    def __init__(self, frontal_area: float, coefficient_of_drag: float) -> None:
        super().__init__()

        self._frontal_area = frontal_area
        self._coefficient_of_drag = coefficient_of_drag

    def calculate_energy_required(
        self,
        current_mass: float,
        current_speed: float,
        target_next_speed: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> float:
        return (
            0.5
            * self._frontal_area
            * self._coefficient_of_drag
            * _NOMINAL_AIR_DENSITY
            * current_speed**2
            * delta_distance
        )
