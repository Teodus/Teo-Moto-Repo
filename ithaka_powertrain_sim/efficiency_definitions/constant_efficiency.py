from ithaka_powertrain_sim.efficiency_definitions import AbstractEfficiencyDefinition


class ConstantEfficiency(AbstractEfficiencyDefinition):
    """
    This class represents a constant efficiency ratio for calculating energy required and energy demand.

    Parameters
    ----------
    efficiency_ratio : float
        The efficiency ratio of the given object.

    Raises
    ------
    ValueError
        If the efficiency_ratio is not between zero and one.

    Attributes
    --------
    _efficiency_ratio : float

    """

    def __init__(self, efficiency_ratio: float) -> None:
        super().__init__()

        if efficiency_ratio > 1 or efficiency_ratio < 0:
            raise ValueError("Efficiency ratio must be between zero and one.")

        self._efficiency_ratio = efficiency_ratio

    def calculate_energy_required(
        self, energy_demand: float, component_rpm: float | None = None
    ) -> float:
        if energy_demand >= 0:
            return energy_demand / self._efficiency_ratio
        else:
            return energy_demand * self._efficiency_ratio

    def calculate_energy_demand(
        self, energy_required: float, component_rpm: float | None = None
    ) -> float:
        if energy_required >= 0:
            return energy_required * self._efficiency_ratio
        else:
            return energy_required / self._efficiency_ratio
