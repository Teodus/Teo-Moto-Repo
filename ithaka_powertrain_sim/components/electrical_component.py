from ithaka_powertrain_sim.components import AbstractComponent
from ithaka_powertrain_sim.shared_abstract_classes import (
    AbstractElectricalComponent,
)


class ElectricalComponent(AbstractElectricalComponent, AbstractComponent):
    """
    The ElectricalComponent class represents an arbitrary electrical component with no special properties.
    It inherits from the AbstractElectricalComponent and AbstractComponent classes.
    """
