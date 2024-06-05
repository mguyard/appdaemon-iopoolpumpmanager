from datetime import time, timedelta
from typing import Dict

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    RootModel,
    field_validator,
    model_validator,
)
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated, Self

import src.utils as Utils


class SlotConfig(BaseModel):
    name: str | None = None
    start: time
    duration_percent: int = Field(gt=0, le=100)


class SlotName(RootModel):
    root: Dict[Annotated[str, AfterValidator(Utils.isSlotNameFormat)], SlotConfig]


class FiltrationSummerConfig(BaseModel):
    recommanded_duration: Annotated[str, AfterValidator(Utils.isSensorEntityFormat)]
    elapsed_today: Annotated[str, AfterValidator(Utils.isSensorEntityFormat)]
    min_duration: PositiveInt | None = None
    max_duration: PositiveInt = Field(lt=1440)
    slots: SlotName

    @model_validator(mode="after")
    def checks(self) -> Self:
        if self.min_duration is not None and self.max_duration is not None:
            if self.min_duration > self.max_duration:
                raise ValueError("The min_duration must be less than the max_duration")
        return self


class FiltrationWinterConfig(BaseModel):
    name: str | None = None
    duration: timedelta | None = None
    start: time | None = None


class BoostConfig(BaseModel):
    selector: Annotated[str, AfterValidator(Utils.isInputSelectEntityFormat)] | None = None
    timer: Annotated[str, AfterValidator(Utils.isTimerEntityFormat)] | None = None

    @model_validator(mode="after")
    def checks(self) -> Self:
        if (self.selector is None and self.timer is not None) or (self.selector is not None and self.timer is None):
            raise ValueError("Both selector and timer must be set or unset")
        return self


class Config(BaseModel):
    dryrun: bool = False
    pump_switch: Annotated[str, AfterValidator(Utils.isSwitchEntityFormat)]
    filtration_mode: Annotated[str, AfterValidator(Utils.isInputSelectEntityFormat)]
    filtration_summer: FiltrationSummerConfig
    filtration_winter: FiltrationWinterConfig = FiltrationWinterConfig()
    boost: BoostConfig = BoostConfig()

    @field_validator("boost", mode="before")
    def boost_none_default_values(cls, value):
        if value is None:
            return BoostConfig()
        return value

    @field_validator("filtration_winter", mode="before")
    def filtration_winter_none_default_values(cls, value):
        if value is None:
            return FiltrationWinterConfig()
        return value

    @model_validator(mode="after")
    def checks(self) -> Self:
        percent_total = 0
        for slot in self.filtration_summer.slots.dict().keys():
            percent_total += self.filtration_summer.slots.root[slot].duration_percent
        if percent_total != 100:
            raise ValueError(f"The sum of all slot durations must be equal to 100%. Configured : {percent_total}%")

        return self
