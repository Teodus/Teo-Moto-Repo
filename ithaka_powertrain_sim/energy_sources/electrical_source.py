from math import inf
from ithaka_powertrain_sim.energy_sources import AbstractEnergySource
from ithaka_powertrain_sim.efficiency_definitions import AbstractEfficiencyDefinition
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractElectricalComponent,
)


class ElectricalSource(AbstractElectricalComponent, AbstractEnergySource):
    """
    This class represents an electrical source that is an abstract electrical component and an abstract energy source.

    Parameters
    ----------
    name : str
        The name of the method.
    energy_density : float
        The energy density of the method.
    non_cell_mass : float, optional
        The non-cell mass of the method. Default is 0.
    cell_mass : float, optional
        The cell mass of the method. Default is 0.
    efficiency_definition : AbstractEfficiencyDefinition or None, optional
        The efficiency definition of the method. Default is None.
    minimum_power_generation : float, optional
        The minimum power generation of the method. Default is -inf.
    maximum_power_generation : float, optional
        The maximum power generation of the method. Default is inf.
    """

    def __init__(
        self,
        name: str,
        energy_density: float,
        non_cell_mass: float = 0,
        cell_mass: float = 0,
        efficiency_definition: AbstractEfficiencyDefinition | None = None,
        minimum_power_generation: float = -inf,
        maximum_power_generation: float = inf,
        allow_negative_fuel: bool = False,
        allow_refueling: bool = False,
    ) -> None:
        super().__init__(
            name,
            energy_density,
            dry_mass=non_cell_mass,
            initial_fuel_mass=cell_mass,
            allow_negative_fuel=allow_negative_fuel,
            allow_refueling=allow_refueling,
        )

        if efficiency_definition is not None:
            self._efficiency_definition = efficiency_definition

        self._minimum_power_generation = minimum_power_generation
        self._maximum_power_generation = maximum_power_generation

    @property
    def mass(self) -> float:
        initial_fuel_mass = self._initial_energy_capacity / self._energy_density

        return super().mass + initial_fuel_mass
