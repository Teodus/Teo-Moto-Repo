from collections.abc import Collection
from math import inf

import numpy as np

from .mechanical_component import MechanicalComponent
from ithaka_powertrain_sim.components import AbstractComponent
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractMechanicalComponent,
)
from ithaka_powertrain_sim.efficiency_definitions import (
    AbstractEfficiencyDefinition,
)


class Gearbox(MechanicalComponent):
    """
    A mechanical component with the sole functionality of applying a gearing ratio step.
    It inherits from the MechanicalComponent class.

    It can apply one of many ratios and chooses the ratio based on upshift rpms for each gear.
    """

    def __init__(
        self,
        name: str,
        child_gear_ratios: Collection[float],
        upshift_child_angular_velocity: Collection[float],
        dry_mass: float = 0.0,
        efficiency_definition: AbstractEfficiencyDefinition | None = None,
        child_components: Collection[AbstractComponent] | None = None,
        minimum_power_generation: float = -inf,
        maximum_power_generation: float = inf,
        inertia: float = 0.0,
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
            inertia=inertia,
            fixed_angular_velocity=fixed_angular_velocity,
            minimum_torque_generation=minimum_torque_generation,
            maximum_torque_generation=maximum_torque_generation,
        )

        self._child_gear_ratios = np.array(child_gear_ratios)
        self._upshift_child_angular_velocity = np.array(upshift_child_angular_velocity)

    def _calculate_child_gearing_ratio(
        self, component_angular_velocity: float | None
    ) -> float:
        possible_child_angular_velocity = (
            component_angular_velocity * self._child_gear_ratios
        )
        child_angular_velocity_overspeed = (
            possible_child_angular_velocity - self._upshift_child_angular_velocity
        )

        selected_gear_index = np.argwhere(child_angular_velocity_overspeed < 0)[0][0]

        return self._child_gear_ratios[selected_gear_index]
