from pydantic import BaseModel, Field


class TrafficFlow(BaseModel):
    duration: float | None = Field(default=None, ge=0)
    protocol: str | None = Field(default=None, max_length=20)
    source_port: str | float | int | None = None
    direction: str | None = Field(default=None, max_length=10)
    destination_port: str | float | int | None = None
    connection_state: str | None = Field(default=None, max_length=20)
    source_tos: float | None = Field(default=None, ge=0)
    destination_tos: float | None = Field(default=None, ge=0)
    total_packets: float | None = Field(default=None, ge=0)
    total_bytes: float | None = Field(default=None, ge=0)
    source_bytes: float | None = Field(default=None, ge=0)


class PredictionResponse(BaseModel):
    prediction: str
    is_botnet: bool
    botnet_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)