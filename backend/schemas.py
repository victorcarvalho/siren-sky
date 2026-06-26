from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class ClassificationResponse(BaseModel):
    filename: str
    classification: str
    model: str
    simulated: bool


class Base64ClassificationRequest(BaseModel):
    image: str
    filename: str = "image.jpg"
