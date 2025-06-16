from collections.abc import Collection
from math import inf

from ithaka_powertrain_sim.components import AbstractComponent
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractMechanicalComponent,
)
from ithaka_powertrain_sim.efficiency_definitions import (
    AbstractEfficiencyDefinition,
)


class MechanicalComponent(AbstractMechanicalComponent, AbstractComponent):
    """
    The MechanicalComponent class represents an arbitrary mechanical component with no special properties.
    It inherits from the AbstractMechanicalComponent and AbstractComponent classes.

    Parameters
    ----------
    name : str
        The name of the component.
    dry_mass : float, optional
        The dry mass of the component. Defaults to 0.0.
    efficiency_definition : AbstractEfficiencyDefinition or None, optional
        The efficiency definition of the component.
        Defaults to None. If None, a ConstantEfficiency with a value of 1.0 will be used.
    child_components : Collection[AbstractComponent] or None, optional
        A collection of child components. Defaults to None. If None, an empty tuple will be used.
    minimum_power_generation : float, optional
        The minimum power generation of the component. Defaults to -inf.
    maximum_power_generation : float, optional
        The maximum power generation of the component. Defaults to inf.
    inertia : float, optional
        The inertia of the component. Defaults to 0.0.
    gearing_ratio : float, optional
        The child to parent gearing ratio. Defaults to 1.0.
    fixed_angular_velocity : float or None, optional
        Enforces a fixed angular velocity at the component. Necessary when there's no direct mechanical connection between the wheels and the component. An error will be raised if a component with fixed angular velocity is passed any other angular velocity. Defaults to None.
    minimum_torque_generation : float, optional
        The minimum torque generation of the component. Defaults to -inf.
    maximum_torque_generation : float, optional
        The maximum torque generation of the component. Defaults to inf.
    """

    def __init__(
        self,
        name: str,
        dry_mass: float = 0.0,
        efficiency_definition: AbstractEfficiencyDefinition | None = None,
        child_components: Collection[AbstractComponent] | None = None,
        minimum_power_generation: float = -inf,
        maximum_power_generation: float = inf,
        inertia: float = 0.0,
        gearing_ratio: float = 1.0,
        fixed_angular_velocity: float | None = None,
        minimum_torque_generation: float = -inf,
        maximum_torque_generation: float = inf,
    ) -> None:
        super().__init__(
            name,
            dry_mass=dry_mass,
            efficiency_definition=efficiency_definition,
            child_components=child_components,
            minimum_power_generation=minimum_power_generation,
            maximum_power_generation=maximum_power_generation,
        )

        self._inertia = inertia
        self._gearing_ratio = gearing_ratio
        self._fixed_angular_velocity = fixed_angular_velocity

        self._minimum_torque_generation = minimum_torque_generation
        self._maximum_torque_generation = maximum_torque_generation

    @property
    def inertia(self) -> float:
        return self._inertia + self._gearing_ratio**2 * sum(
            child_component.inertia for child_component in self.child_components
        )

    def _calculate_minimum_power_generation(
        self, component_angular_velocity: float | None
    ) -> float:
        if component_angular_velocity is None:
            return self._minimum_power_generation
        else:
            return max(
                self._minimum_power_generation,
                self._minimum_torque_generation * component_angular_velocity,
            )

    def _calculate_maximum_power_generation(
        self, component_angular_velocity: float | None
    ) -> float:
        if component_angular_velocity is None:
            return self._maximum_power_generation
        else:
            return min(
                self._maximum_power_generation,
                self._maximum_torque_generation * component_angular_velocity,
            )
