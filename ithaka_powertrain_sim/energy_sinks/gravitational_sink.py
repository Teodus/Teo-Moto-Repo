from ithaka_powertrain_sim.energy_sinks import AbstractEnergySink


class GravitationalSink(AbstractEnergySink):
    """
    An energy sink capturing gravitational potential energy.
    """

    def calculate_energy_required(
        self,
        current_mass: float,
        current_speed: float,
        target_next_speed: float,
        delta_distance: float,
        delta_elevation: float,
    ) -> float:
        return current_mass * delta_elevation * 9.81
