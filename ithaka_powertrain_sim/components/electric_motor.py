from .mechanical_component import MechanicalComponent
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractElectricalComponent,
)


class ElectricMotor(AbstractElectricalComponent, MechanicalComponent):
    """
    The ElectricMotor class represents an electric motor.
    It inherits from the AbstractElectricalComponent, AbstractMechanicalComponent and AbstractComponent classes.
    """

    @property
    def _can_disable(self) -> bool:
        return True
