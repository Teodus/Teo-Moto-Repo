from .mechanical_component import MechanicalComponent


class CombustionEngine(MechanicalComponent):
    """
    The CombustionEngine class represents a combustion engine.
    It inherits from the AbstractMechanicalComponent and AbstractComponent classes.
    """

    @property
    def _can_disable(self) -> bool:
        return True
