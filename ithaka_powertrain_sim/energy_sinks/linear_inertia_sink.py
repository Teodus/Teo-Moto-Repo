from .abstract_inertia_sink import AbstractInertiaSink


class LinearInertiaSink(AbstractInertiaSink):
    """
    An energy sink capturing linear kinetic energy of the motorbike.
    """

    def calculate_kinetic_energy_coefficient(
        self,
        current_mass: float,
    ) -> float:
        return 0.5 * current_mass
