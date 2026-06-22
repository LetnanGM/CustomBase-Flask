from pydantic import BaseModel, model_validator


class PathLabel(BaseModel):
    relative: str
    absolute: str


class Config(BaseModel):
    workspace: PathLabel
    package: str
    metadata: str

    @model_validator(mode="after")
    def resolve(self):
        abs_path = self.workspace.absolute

        self.package = self.package.replace("[ABS]", abs_path)
        self.metadata = self.metadata.replace("[ABS]", abs_path)

        return self