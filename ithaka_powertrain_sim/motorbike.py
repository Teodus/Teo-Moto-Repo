from collections.abc import Collection, Mapping
import pandas as pd

from ithaka_powertrain_sim.energy_sinks import (
    AbstractEnergySink,
    AbstractInertiaSink,
    LinearInertiaSink,
    AngularInertiaSink,
    GravitationalSink,
    AerodynamicDragSink,
    RollingResistanceSink,
)

from ithaka_powertrain_sim.energy_sources import ChemicalSource, ElectricalSource
from ithaka_powertrain_sim.components import AbstractComponent
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractElectricalComponent,
    AbstractMechanicalComponent,
)


class Motorbike(
    AbstractElectricalComponent,
    AbstractMechanicalComponent,
    AbstractComponent,
    AbstractEnergySink,
):
    """
    The top level parent class encapsulating an entire motorbike.
    
    Parameters
    ----------
    name : str
        The name of the component.
    dry_mass_excluding_components : float
        The dry mass of the component excluding its child components.
    front_mass_ratio : float
        The ratio of the front mass to the total mass of the component.
    front_wheel_inertia : float
        The rotational inertia of the front wheel.
    front_wheel_radius : float
        The radius of the front wheel.
    front_wheel_coefficient_of_rolling_resistance : float
        The coefficient of rolling resistance for the front wheel.
    rear_wheel_inertia : float
        The rotational inertia of the rear wheel.
    rear_wheel_radius : float
        The radius of the rear wheel.
    rear_wheel_coefficient_of_rolling_resistance : float
        The coefficient of rolling resistance for the rear wheel.
    frontal_area : float
        The frontal area of the component.
    coefficient_of_aerodynamic_drag : float
        The coefficient of aerodynamic drag for the component.
    child_components : Collection[AbstractComponent]
        The collection of child components.
    """

    def __init__(
        self,
        name: str,
        dry_mass_excluding_components: float,
        front_mass_ratio: float,
        front_wheel_inertia: float,
        front_wheel_radius: float,
        front_wheel_coefficient_of_rolling_resistance: float,
        rear_wheel_inertia: float,
        rear_wheel_radius: float,
        rear_wheel_coefficient_of_rolling_resistance: float,
        frontal_area: float,
        coefficient_of_aerodynamic_drag: float,
        child_components: Collection[AbstractComponent],
    ) -> None:
        super().__init__(
            name,
            dry_mass=dry_mass_excluding_components,
            child_components=child_components,
        )

        self.test_unique_ids()

        self._linear_inertia_sink = LinearInertiaSink()
        self._front_angular_inertia_sink = AngularInertiaSink(
            front_wheel_inertia, front_wheel_radius
        )
        self._rear_angular_inertia_sink = AngularInertiaSink(
            rear_wheel_inertia, rear_wheel_radius
        )
        self._gravitational_sink = GravitationalSink()
        self._aerodynamic_drag_sink = AerodynamicDragSink(
            frontal_area, coefficient_of_aerodynamic_drag
        )
        self._front_rolling_resistance_sink = RollingResistanceSink(
            front_mass_ratio,
            front_wheel_coefficient_of_rolling_resistance,
        )
        self._rear_rolling_resistance_sink = RollingResistanceSink(
            (1 - front_mass_ratio),
            rear_wheel_coefficient_of_rolling_resistance,
        )

        # TODO make use of the component inertias in this calculation (will require a concept of RPM and gearing)

    @property
    def energy_sinks(self) -> tuple[AbstractEnergySink, ...]:
        """
        Get the energy sinks.

        This method returns a tuple of all the energy sinks in the system.

        Returns
        --------
        tuple[AbstractEnergySink, ...]
            A tuple containing all the energy sinks.
        """
        return (
            self._linear_inertia_sink,
            self._front_angular_inertia_sink,
            self._rear_angular_inertia_sink,
            self._gravitational_sink,
            self._aerodynamic_drag_sink,
            self._front_rolling_resistance_sink,
            self._rear_rolling_resistance_sink,
        )

    @property
    def _inertia_sinks(self) -> tuple[AbstractInertiaSink, ...]:
        """
        Get the energy sinks.

        This method returns a tuple of all the energy sinks in the system.

        Returns
        --------
        tuple[AbstractEnergySink, ...]
            A tuple containing all the energy sinks.
        """
        return (
            self._linear_inertia_sink,
            self._front_angular_inertia_sink,
            self._rear_angular_inertia_sink,
        )

    def test_unique_ids(self) -> None:
        """
        Checks if there is an id clash in the child chain.

        Raises
        --------
        ValueError
            If there is an id clash in the child chain.
        """
        if len(self.ids) != len(set(self.ids)):
            raise ValueError(
                "There is an id clash in the child chain. One child has multiple parents. This is not currently supported; please fix the chain."
            )

    def calculate_energy_required(
        self,
        current_mass: float,
        current_speed: float,
        target_next_speed: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> float:
        return sum(
            energy_sink.calculate_energy_required(
                current_mass,
                current_speed,
                target_next_speed,
                delta_distance,
                delta_elevation,
            )
            for energy_sink in self.energy_sinks
        )

    def calculate_achieved_speed(
        self,
        current_speed: float,
        target_next_speed: float,
        delta_time: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> tuple[float, pd.DataFrame]:
        """
        Parameters
        ----------
        current_speed : float
            The current speed of the object.
        target_next_speed : float
            The target speed for the next time step.
        delta_time : float
            The time interval between the current and next time steps.
        delta_distance : float
            The change in distance between the current and next time steps.
        delta_elevation : float
            The change in elevation between the current and next time steps.

        Returns
        -------
        float
            The achieved speed for the next time step.
        """
        total_energy_required = self.calculate_energy_required(
            self.mass,
            current_speed,
            target_next_speed,
            delta_distance,
            delta_elevation,
        )

        inertial_energy_required = sum(
            inertial_energy_sink.calculate_energy_required(
                self.mass,
                current_speed,
                target_next_speed,
                delta_distance,
                delta_elevation,
            )
            for inertial_energy_sink in self._inertia_sinks
        )

        current_angular_velocity = (
            current_speed / self._rear_angular_inertia_sink.nominal_radius
        )

        total_energy_delivered, energy_delivered_report = (
            self.calculate_energy_delivered(
                total_energy_required, delta_time, current_angular_velocity
            )
        )
        apply_energy_capacity_transaction(energy_delivered_report)

        power_delivered_report = {
            f"{key.name} Power Delivered": value / delta_time
            for key, value in energy_delivered_report.items()
        }
        remaining_energy_report = {
            f"{key.name} Capacity Remaining": value
            for key, value in self.remaining_energy_report.items()
        }

        reporting_dataframe_row = pd.DataFrame(
            power_delivered_report | remaining_energy_report, index=[0]
        )

        inertial_energy_delivered = inertial_energy_required - (
            total_energy_required - total_energy_delivered
        )

        achieved_speed = self.calculate_next_speed(
            self.mass,
            current_speed,
            inertial_energy_delivered,
            inertial_energy_required,
        )

        return achieved_speed, reporting_dataframe_row

    def calculate_next_speed(
        self,
        current_mass: float,
        current_speed: float,
        available_energy: float,
        demanded_energy: float,
    ) -> float:
        """
        Parameters
        ----------
        current_mass : float
            The current mass of the object.
        current_speed : float
            The current speed of the object.
        available_energy : float
            The available energy for the object.
        demanded_energy : float
            The demanded energy for the object.

        Returns
        -------
        float
            The next speed of the object.

        Raises
        ------
        ValueError
            If the next speed is <= 0 and demanded_energy > 0, indicating that the object is unable to meet the necessary power demand and has come to a halt.
        """
        kinetic_energy_coefficient = sum(
            abstract_inertia_sink.calculate_kinetic_energy_coefficient(
                current_mass,
            )
            for abstract_inertia_sink in self._inertia_sinks
        )

        delta_speed_squared = available_energy / kinetic_energy_coefficient

        if (current_speed**2 + delta_speed_squared) >= 0:
            next_speed = (current_speed**2 + delta_speed_squared) ** 0.5
        else:
            next_speed = -((-(current_speed**2 + delta_speed_squared)) ** 0.5)

        if next_speed <= 0 and demanded_energy > 0:
            raise ValueError(
                "You are unable to need the necessary power demand and the bike has come to a halt."
            )
        else:
            return next_speed


def apply_energy_capacity_transaction(
    energy_delivered_report: Mapping[AbstractComponent, float]
):
    """
    Parameters
    ----------
    energy_delivered_report : Mapping[AbstractComponent, float]
        A mapping of child components to the amount of energy delivered to each component.
    """
    for child_component, energy_delivered in energy_delivered_report.items():
        if isinstance(child_component, ChemicalSource):
            child_component.apply_energy_capacity_transaction(energy_delivered)
        elif isinstance(child_component, ElectricalSource):
            child_component.apply_energy_capacity_transaction(energy_delivered)
