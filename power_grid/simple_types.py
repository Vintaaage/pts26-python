from dataclasses import dataclass
from enum import Enum
from typing import Union, TypeVar

T = TypeVar("T")


class Resource(Enum):
    COAL = 1
    OIL = 2
    GARBAGE = 3
    URANIUM = 4


class PlayerColor(Enum):
    RED = 1
    YELLOW = 2
    BLUE = 3
    GREEN = 4
    PURPLE = 5
    BLACK = 6


class PhaseStatus(Enum):
    PHASE_CONTINUES = 1
    PHASE_ENDS = 2
    GAME_ENDS = 3


class GamePhase(Enum):
    AUCTION_POWER_PLANTS = 1
    BUY_RESOURCES = 2
    BUY_HOUSES = 3
    BUREAUCRACY = 4
    GAME_END = 5


@dataclass(frozen=True)
class RequestError:
    description: str


@dataclass(frozen=True)
class SerializedGameState:
    state: str


@dataclass(frozen=True)
class PowerPlantNumber:
    number: int


@dataclass(frozen=True)
class PowerPlant:
    number: PowerPlantNumber
    accepted_resources: tuple[Resource, ...]
    resource_amount: int
    number_of_cities: int


Result = Union[T, RequestError]
