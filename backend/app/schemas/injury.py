from pydantic import BaseModel, ConfigDict


class InjuryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class InjuryWithEffectiveness(InjuryRead):
    """InjuryRead plus the effectiveness rating for one specific exercise --
    used when returning injuries in the context of "injuries this exercise helps with"."""

    effectiveness: int
