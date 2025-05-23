"""Models that capture topology types."""

from typing import Annotated

from pydantic import Field, NonNegativeFloat, PositiveInt

from r2x.enums import ACBusTypes
from r2x.models.core import BaseComponent
from r2x.models.named_tuples import MinMax
from r2x.units import Voltage, ureg


class Topology(BaseComponent):
    """Abstract type to represent the structure and interconnectedness of the system."""


class AggregationTopology(Topology):
    """Base class for area-type components."""


class Area(AggregationTopology):
    """Collection of buses in a given region."""

    peak_active_power: Annotated[NonNegativeFloat, Field(description="Peak active power in the area")] = 0.0
    peak_reactive_power: Annotated[NonNegativeFloat, Field(description="Peak reactive power in the area")] = (
        0.0
    )
    load_response: Annotated[
        float,
        Field(
            description=(
                "Load-frequency damping parameter modeling how much the load in the area changes "
                "due to changes in frequency (MW/Hz)."
            )
        ),
    ] = 0.0

    @classmethod
    def example(cls) -> "Area":
        return Area(name="New York")


class LoadZone(AggregationTopology):
    """Collection of buses for electricity price analysis."""

    peak_active_power: Annotated[NonNegativeFloat, Field(description="Peak active power in the area")] = 0.0
    peak_reactive_power: Annotated[NonNegativeFloat, Field(description="Peak reactive power in the area")] = (
        0.0
    )

    @classmethod
    def example(cls) -> "LoadZone":
        return LoadZone(name="ExampleLoadZone")


class Bus(Topology):
    """Abstract class for a bus."""

    number: Annotated[PositiveInt, Field(description="A unique bus identification number.")]
    bustype: Annotated[ACBusTypes, Field(description="Type of category of bus,")] | None = None
    area: Annotated[Area, Field(description="Area containing the bus.")] | None = None
    load_zone: Annotated[LoadZone, Field(description="the load zone containing the DC bus.")] | None = None
    voltage_limits: Annotated[MinMax, Field(description="the voltage limits")] | None = None
    base_voltage: (
        Annotated[Voltage, Field(gt=0, description="Base voltage in kV. Unit compatible with voltage.")]
        | None
    ) = None
    magnitude: (
        Annotated[NonNegativeFloat, Field(description="Voltage as a multiple of base_voltage.")] | None
    ) = None


class DCBus(Bus):
    """Power-system DC Bus."""

    @classmethod
    def example(cls) -> "DCBus":
        return DCBus(
            number=1,
            name="ExampleBus",
            load_zone=LoadZone.example(),
            area=Area.example(),
            base_voltage=20 * ureg.kV,
            bustype=ACBusTypes.PV,
        )


class ACBus(Bus):
    """Power-system AC bus."""

    angle: Annotated[float | None, Field(description="Angle of the bus in radians.", gt=-1.571, lt=1.571)] = (
        None
    )

    @classmethod
    def example(cls) -> "ACBus":
        return ACBus(
            number=1,
            name="ExampleBus",
            load_zone=LoadZone.example(),
            area=Area.example(),
            base_voltage=13 * ureg.kV,
            voltage_limits=MinMax(min=0.9, max=1.1),
            bustype=ACBusTypes.PV,
        )


class Arc(Topology):
    """Topological directed edge connecting two buses"""

    name: Annotated[str, Field(frozen=True, exclude=True)] = ""
    from_to: Annotated[Bus, Field(description="The initial bus", alias="from")]
    to_from: Annotated[Bus, Field(description="The terminal bus", alias="to")]
