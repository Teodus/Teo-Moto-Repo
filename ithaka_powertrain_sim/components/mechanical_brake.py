from .mechanical_component import MechanicalComponent
from ithaka_powertrain_sim.components import (
    AbstractComponent,
)


class MechanicalBrake(MechanicalComponent):
    """
    The MechanicalComponent class represents a mechanical brake capable of providing infinite negative power and zero positive power.
    It inherits from the AbstractMechanicalComponent and AbstractComponent classes.

    Parameters
    ----------
    name : str
        The name of the object.
    dry_mass : float, optional
        The dry mass of the object. Default is 0.
    inertia : float, optional
        The inertia of the object. Default is 0.
    """

    def __init__(self, name: str, dry_mass: float = 0, inertia: float = 0) -> None:
        super().__init__(name, dry_mass, maximum_power_generation=0.0, inertia=inertia)

    def calculate_energy_delivered(
        self,
        energy_demand: float,
        delta_time: float,
        component_angular_velocity: float | None,
    ) -> tuple[float, dict[AbstractComponent, float]]:
        energy_delivered = min(energy_demand, 0)

        return energy_delivered, {self: energy_delivered}
