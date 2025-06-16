from collections.abc import Collection
from scipy import interpolate

from ithaka_powertrain_sim.efficiency_definitions import AbstractEfficiencyDefinition


class AngularVelocityEfficiency(AbstractEfficiencyDefinition):
    """
    This class represents a constant efficiency ratio for calculating energy required and energy demand.

    Parameters
    ----------
    angular_velocity_lookup : Collection[float]
        The angular velocity at which each efficiency ratio is defined.
    efficiency_lookup : Collection[float]
        The efficiency ratio at each angular velocity value.

    Raises
    ------
    ValueError
        If the efficiency_ratio is not between zero and one.

    Attributes
    --------
    _efficiency_ratio

    """

    def __init__(
        self,
        angular_velocity_lookup: Collection[float],
        efficiency_lookup: Collection[float],
    ) -> None:
        super().__init__()

        if any(
            efficiency_ratio > 1 or efficiency_ratio < 0
            for efficiency_ratio in efficiency_lookup
        ):
            raise ValueError("Efficiency ratio must be between zero and one.")

        self._efficiency_lookup = interpolate.interp1d(
            angular_velocity_lookup,
            efficiency_lookup,
            kind="linear",
            bounds_error=True,
            assume_sorted=False,
        )

    def calculate_energy_required(
        self, energy_demand: float, component_rpm: float | None = None
    ) -> float:
        if component_rpm is None:
            raise ValueError(
                "The component RPM must be defined in an RPM-dependent efficiency definition."
            )

        if energy_demand >= 0:
            return energy_demand / self._efficiency_lookup(component_rpm)
        else:
            return energy_demand * self._efficiency_lookup(component_rpm)

    def calculate_energy_demand(
        self, energy_required: float, component_rpm: float | None = None
    ) -> float:
        if component_rpm is None:
            raise ValueError(
                "The component RPM must be defined in an RPM-dependent efficiency definition."
            )

        if energy_required >= 0:
            return energy_required * self._efficiency_lookup(component_rpm)
        else:
            return energy_required / self._efficiency_lookup(component_rpm)
