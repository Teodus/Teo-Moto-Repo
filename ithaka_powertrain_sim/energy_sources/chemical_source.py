from ithaka_powertrain_sim.energy_sources import AbstractEnergySource
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractMechanicalComponent,
)


class ChemicalSource(AbstractMechanicalComponent, AbstractEnergySource):
    """
    The ChemicalSource class is a subclass of the AbstractMechanicalComponent and AbstractEnergySource classes. It represents an energy system that utilizes chemical fuel.

    Parameters
    ----------
    self : object
        The object instance being created.
    name : str
        The name of the energy system.
    energy_density : float
        The energy density of the fuel in the energy system.
    dry_mass : float, optional
        The dry mass of the energy system. Default is 0.
    initial_fuel_mass : float, optional
        The initial fuel mass of the energy system. Default is 0.
    """

    def __init__(
        self,
        name: str,
        energy_density: float,
        dry_mass: float = 0,
        initial_fuel_mass: float = 0.0,
        allow_negative_fuel: bool = False,
        allow_refueling: bool = False,
    ) -> None:
        super().__init__(
            name,
            energy_density,
            dry_mass,
            initial_fuel_mass,
            allow_negative_fuel,
            allow_refueling,
        )

        self._minimum_power_generation = 0.0

    @property
    def mass(self) -> float:
        feasible_remaining_fuel_mass = max(self.remaining_fuel_mass, 0)

        return super().mass + feasible_remaining_fuel_mass
