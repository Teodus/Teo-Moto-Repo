from __future__ import annotations

from abc import ABC
import numpy as np

from ithaka_powertrain_sim.components import AbstractComponent


class AbstractEnergySource(AbstractComponent, ABC):
    """
    This class represents an abstract energy source.

    Parameters
    ----------
    name : str
        The name of the object.

    energy_density : float
        The energy density of the fuel in a unit of energy per unit mass.

    dry_mass : float, optional
        The dry mass of the object without any fuel (default is 0.0).

    initial_fuel_mass : float, optional
        The initial mass of the fuel (default is 0.0).
    """

    def __init__(
        self,
        name: str,
        energy_density: float,
        dry_mass: float = 0.0,
        initial_fuel_mass: float = 0.0,
        allow_negative_fuel: bool = False,
        allow_refueling: bool = False,
    ) -> None:
        super().__init__(name, dry_mass=dry_mass)

        self._energy_density = energy_density
        self._initial_energy_capacity = initial_fuel_mass * energy_density
        self._remaining_energy_capacity = self._initial_energy_capacity

        if allow_negative_fuel and allow_refueling:
            raise ValueError(
                "The energy source allows conflicting behaviours: it is allowed to both let energy go negative, and 'magically' refuel on negative capacity. Only one of these behaviours is possible at a time."
            )

        self._allow_negative_fuel = allow_negative_fuel
        self._allow_refueling = allow_refueling

    @property
    def remaining_energy_capacity(self) -> float:
        """
        Get the remaining energy capacity.

        Returns
        --------
        float
            The remaining energy capacity.
        """
        return self._remaining_energy_capacity

    @property
    def remaining_energy_percentage(self) -> float:
        """
        Get the remaining energy percentage.

        Returns
        --------
        float
            The remaining energy percentage.
        """
        return (self.remaining_energy_capacity / self._initial_energy_capacity) * 100.0

    @property
    def remaining_fuel_mass(self) -> float:
        """
        Calculate the remaining fuel mass.

        Returns
        --------
        float
            The remaining fuel mass calculated using the remaining energy capacity and energy density.
        """
        return self.remaining_energy_capacity / self._energy_density

    @property
    def consumed_energy_capacity(self) -> float:
        """
        Get the consumed energy capacity.

        Returns
        --------
        float
            The consumed energy capacity.
        """
        return self._initial_energy_capacity - self._remaining_energy_capacity

    @property
    def consumed_energy_percentage(self) -> float:
        """
        Get the consumed energy percentage.

        Returns
        --------
        float
            The consumed energy percentage.
        """
        return (self.consumed_energy_capacity / self._initial_energy_capacity) * 100.0

    @property
    def consumed_fuel_mass(self) -> float:
        """
        Calculate the consumed fuel mass.

        Returns
        --------
        float
            The consumed fuel mass calculated using the consumed energy capacity and energy density.
        """
        return self.consumed_energy_capacity / self._energy_density

    @property
    def remaining_energy_report(self) -> dict[AbstractEnergySource, float]:
        return {self: self.remaining_energy_capacity}

    def _calculate_energy_available(self, energy_demand: float) -> float:
        """
        Parameters
        ----------
        energy_demand : float
            The amount of energy demand required.

        Returns
        -------
        float
            The calculated energy available based on the energy demand and the remaining energy capacity.
        """
        if energy_demand > self._remaining_energy_capacity and not (
            self._allow_negative_fuel or self._allow_refueling
        ):
            return self._remaining_energy_capacity
        elif energy_demand < -self.consumed_energy_capacity:
            return -self.consumed_energy_capacity
        else:
            return energy_demand

    def calculate_energy_delivered(
        self,
        energy_demand: float,
        delta_time: float,
        component_angular_velocity: float | None,
    ) -> tuple[float, dict[AbstractComponent, float]]:
        power_limited_energy_demand = float(
            np.clip(
                energy_demand,
                self._calculate_minimum_power_generation(component_angular_velocity)
                * delta_time,
                self._calculate_maximum_power_generation(component_angular_velocity)
                * delta_time,
            )
        )

        energy_required = self._efficiency_definition.calculate_energy_required(
            power_limited_energy_demand, component_angular_velocity
        )

        energy_available = self._calculate_energy_available(energy_required)
        energy_delivered = self._efficiency_definition.calculate_energy_demand(
            energy_available
        )

        return energy_delivered, {self: energy_delivered}

    def apply_energy_capacity_transaction(
        self, energy_demand: float, component_angular_velocity: float | None = None
    ) -> None:
        """
        Apply an energy and capacity transaction.

        Parameters
        ----------
        energy_demand : float
            The amount of energy demanded in the transaction.
        """
        if abs(energy_demand) > 1e0:
            energy_required = self._efficiency_definition.calculate_energy_required(
                energy_demand, component_angular_velocity
            )

            self._remaining_energy_capacity = (
                self._remaining_energy_capacity - energy_required
            )

            if self._remaining_energy_capacity < 0 and self._allow_refueling:
                self._remaining_energy_capacity = (
                    self._remaining_energy_capacity + self._initial_energy_capacity
                )

                print(f"Energy source {self.name} has done a mid-outing refuel.")
