from __future__ import annotations

from abc import ABC
from collections.abc import Collection
import numpy as np
from math import inf
import shortuuid

from ithaka_powertrain_sim.efficiency_definitions import (
    AbstractEfficiencyDefinition,
    ConstantEfficiency,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ithaka_powertrain_sim.energy_sources import AbstractEnergySource


class AbstractComponent(ABC):
    """
    The AbstractComponent class represents an abstract component in the component tree. This is the most basic level physical component.

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
    """

    def __init__(
        self,
        name: str,
        dry_mass: float = 0.0,
        efficiency_definition: AbstractEfficiencyDefinition | None = None,
        child_components: Collection[AbstractComponent] | None = None,
        minimum_power_generation: float = -inf,
        maximum_power_generation: float = inf,
    ) -> None:
        super().__init__()

        self._name = name
        self._id = shortuuid.uuid()
        self._dry_mass = dry_mass
        self._inertia = 0.0
        self._gearing_ratio = 1.0
        self._fixed_angular_velocity = None

        if efficiency_definition is None:
            efficiency_definition = ConstantEfficiency(1.0)
        self._efficiency_definition = efficiency_definition

        if child_components is None:
            self._child_components = tuple()
        else:
            self._child_components = tuple(child_components)

        self._test_child_components_for_compatibility()

        self._minimum_power_generation = minimum_power_generation
        self._maximum_power_generation = maximum_power_generation

    def __eq__(self, other: AbstractComponent) -> bool:
        """
        Performs equality check.

        Parameters
        ----------
        other: AbstractComponent
            The object to compare with the current instance. It must be of type AbstractComponent or its subclass.

        Returns
        -------
        bool
            Returns True if the current instance's _id attribute is equal to the _id attribute of the other object. Otherwise, returns False.

        """
        return self._id == other.id

    def __hash__(self) -> int:
        """
        Compute the hash value of the object.

        Returns
        --------
        int
            The computed hash value.

        """
        return hash(self._id)

    @property
    def name(self) -> str:
        """
        Returns the name of the object.

        Returns
        --------
        str
            The name of the object.
        """
        return self._name

    @property
    def id(self) -> str:
        """
        Returns the id of the object.

        Returns
        --------
        str
            The id of the object.
        """
        return self._id

    @property
    def _can_disable(self) -> bool:
        """
        Checks whether the component can be disabled (ignored along with its child components).

        Returns
        --------
        bool
            True if the component can be disabled, False otherwise.
        """
        return False

    @property
    def child_components(self) -> tuple[AbstractComponent, ...]:
        """
        Returns the child components of this instance.

        Returns
        --------
        tuple[AbstractComponent, ...]
            A collection of AbstractComponent objects representing the child components.
        """
        return self._child_components

    @property
    def is_electrical(self) -> bool:
        """Check if the component is electrical.

        Returns
        --------
        bool
            True if the component is electrical, False otherwise.
        """
        return False

    @property
    def is_mechanical(self) -> bool:
        """
        Check if the component is mechanical.

        Returns
        --------
        bool
            True if the component is mechanical, False otherwise.
        """
        return False

    @property
    def ids(self) -> list[str]:
        """
        Returns the list of all IDs associated with the current object and its child components.

        Returns
        --------
        list[str]
            A list of strings representing the IDs.
        """
        ids = [self._id]

        for child_component in self._child_components:
            ids.extend(child_component.ids)

        return ids

    @property
    def mass(self) -> float:
        """
        Return the total mass of the component and all its child components.

        The total mass is the sum of the component's own mass and the mass
        of all its child components.

        Returns
        --------
        float
            The total mass of the component and all its child components.
        """
        return self._dry_mass + sum(
            child_component.mass for child_component in self.child_components
        )

    @property
    def inertia(self) -> float:
        """
        Return the total rotational inertia of the component and all its child components.

        The total inertia is the sum of the component's own inertia and the inertia
        of all its child components.

        Returns
        --------
        float
            The total inertia of the component and all its child components.
        """
        if self.is_mechanical:
            return self._inertia + sum(
                child_component.inertia for child_component in self.child_components
            )
        else:
            return 0.0

    @property
    def _zeroed_child_energy_delivered_report(self) -> dict[AbstractComponent, float]:
        """
        Create a zeroed record of delivered power by each child component.

        Returns
        --------
        dict[AbstractComponent, float]
            A dictionary where the keys are AbstractComponent objects representing child components,
            and the values are the delivered power of the child component (always zero in this case).
        """
        empty_child_energy_delivered_report = {self: 0.0}

        for child_component in self._child_components:
            empty_child_energy_delivered_report.update(
                child_component._zeroed_child_energy_delivered_report
            )

        return empty_child_energy_delivered_report

    @property
    def remaining_energy_report(self) -> dict[AbstractEnergySource, float]:
        """
        Create a report of all child AbstractEnergySources and their remaining energies.

        Returns
        --------
        dict[AbstractEnergySource, float]
            A dictionary where the keys are AbstractEnergySources objects representing child components,
            and the values are the remaining energy in that source.
        """
        remaining_energy_report = {}

        for child_component in self._child_components:
            remaining_energy_report.update(child_component.remaining_energy_report)

        return remaining_energy_report

    def _test_child_components_for_compatibility(self) -> None:
        """
        Checks the compatibility of child components with the current component.

        This method iterates through all child components and validates their compatibility with the current component.
        A child component is considered compatible if it has the same hardware type as the current component.
        If a child component is found to be incompatible, a ValueError is raised with a descriptive error message.

        Raises
        --------
        ValueError
            If a child component is incompatible with the current component.
        """
        for child_component in self._child_components:
            if not (
                self.is_electrical
                and child_component.is_electrical
                or self.is_mechanical
                and child_component.is_mechanical
            ):
                raise ValueError(
                    f"Child component {child_component.name} is incompatible with component {self.name} due to a mismatch of hardware type."
                )

    def _calculate_child_gearing_ratio(
        self, component_angular_velocity: float | None
    ) -> float:
        """
        Returns the gearing ratio between the component's output and the child's input.

        Parameters
        ----------
        component_angular_velocity : float | None
            The angular velocity of the component. If the component doesn't spin (because it's not mechanical), this is not required.

        Returns
        -------
        float
            Returns the gearing ratio.
        """
        return self._gearing_ratio

    def _calculate_minimum_power_generation(
        self, component_angular_velocity: float | None
    ) -> float:
        """
        Returns the minimum power output.

        Parameters
        ----------
        component_angular_velocity : float | None
            The angular velocity of the component. If the component doesn't spin (because it's not mechanical), this is not required.

        Returns
        -------
        float
            Returns the minimum power output.
        """
        return self._minimum_power_generation

    def _calculate_maximum_power_generation(
        self, component_angular_velocity: float | None
    ) -> float:
        """
        Returns the maximum power output.

        Parameters
        ----------
        component_angular_velocity : float | None
            The angular velocity of the component. If the component doesn't spin (because it's not mechanical), this is not required.

        Returns
        -------
        float
            Returns the maximum power output.
        """
        return self._maximum_power_generation

    def calculate_energy_delivered(
        self,
        energy_demand: float,
        delta_time: float,
        component_angular_velocity: float | None,
    ) -> tuple[float, dict[AbstractComponent, float]]:
        """
        Returns the energy delivered power of the current component for a given energy demand.

        Parameters
        ----------
        energy_demand : float
            The total energy demand for the current component.
        delta_time : float
            The time interval over which the energy is being delivered.
        component_angular_velocity : float
            The rpm of the parent component.

        Returns
        -------
        tuple[float, dict[AbstractComponent, float]]
            A tuple containing the total energy delivered and the energy delivered record as a dictionary of child components and their delivered energy.
        """
        if self._can_disable and energy_demand == 0:
            return 0, self._zeroed_child_energy_delivered_report
        else:
            if self.is_mechanical:
                if self._fixed_angular_velocity is not None:
                    if component_angular_velocity is not None:
                        raise ValueError(
                            "You cannot pass a variable rpm to a component with a fixed rpm."
                        )

                    component_angular_velocity = self._fixed_angular_velocity

                child_angular_velocity = (
                    self._calculate_child_gearing_ratio(component_angular_velocity)
                    * component_angular_velocity
                )
            else:
                component_angular_velocity = None
                child_angular_velocity = None

            power_limited_energy_demand = float(
                np.clip(
                    energy_demand,
                    self._calculate_minimum_power_generation(component_angular_velocity)
                    * delta_time,
                    self._calculate_maximum_power_generation(component_angular_velocity)
                    * delta_time,
                )
            )

            target_energy_required = (
                self._efficiency_definition.calculate_energy_required(
                    power_limited_energy_demand, component_angular_velocity
                )
            )

            current_delta_to_energy_target = inf
            previous_delta_to_energy_target = -inf

            energy_delivered_report = self._zeroed_child_energy_delivered_report
            immediate_child_energy_delivered_report = {
                child_component: 0.0 for child_component in self.child_components
            }

            while not (
                abs(current_delta_to_energy_target) < 1e0
                or abs(current_delta_to_energy_target - previous_delta_to_energy_target)
                < 1e0
            ):
                previous_delta_to_energy_target = current_delta_to_energy_target

                for child_component in self.child_components:
                    energy_delivered_excluding_child_component = (
                        sum(immediate_child_energy_delivered_report.values())
                        - immediate_child_energy_delivered_report[child_component]
                    )
                    remaining_energy_required = (
                        target_energy_required
                        - energy_delivered_excluding_child_component
                    )

                    child_energy_delivered, child_energy_delivered_report = (
                        child_component.calculate_energy_delivered(
                            remaining_energy_required,
                            delta_time,
                            child_angular_velocity,
                        )
                    )

                    energy_delivered_report.update(child_energy_delivered_report)
                    immediate_child_energy_delivered_report[child_component] = (
                        child_energy_delivered
                    )

                current_delta_to_energy_target = target_energy_required - sum(
                    immediate_child_energy_delivered_report.values()
                )

            energy_delivered = self._efficiency_definition.calculate_energy_demand(
                sum(immediate_child_energy_delivered_report.values()),
                component_angular_velocity,
            )

            energy_delivered_report[self] = energy_delivered

            return energy_delivered, energy_delivered_report
