from abc import ABC, abstractmethod


class AbstractEfficiencyDefinition(ABC):
    """
    The AbstractEfficiencyDefinition class represents an abstract efficiency definition.

    This class provides a blueprint for efficiency definitions. Subclasses must implement
    the methods `calculate_energy_required` and `calculate_energy_demand`.
    """

    @abstractmethod
    def calculate_energy_required(
        self, energy_demand: float, component_angular_velocity: float | None = None
    ) -> float:
        """
        Returns the amount of energy required from the component's children, given the demand from the parent component.

        The inverse calculation of calculate_energy_demand().

        Parameters
        ----------
        energy_demand : float
            The amount of energy demanded by the parent component.

        Returns
        -------
        float
            The amount of energy required from the component's children.
        """
        ...

    @abstractmethod
    def calculate_energy_demand(
        self, energy_required: float, component_angular_velocity: float | None = None
    ) -> float:
        """
        Returns the amount of energy demanded from the parent component, given the energy provided by the component's children.

        The inverse calculation of calculate_energy_required().

        Parameters
        ----------
        energy_required : float
            The amount of energy provided by the component's children.

        Returns
        -------
        float
            The amount of energy demanded from the parent component.
        """
        ...
