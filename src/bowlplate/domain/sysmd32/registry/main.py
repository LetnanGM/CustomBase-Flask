import json

from pydantic import BaseModel, field_validator

from share.shared.handler.decorator import validate_parameter
from share.support.file.FileHandling import File

from .config import REGISTRY_CONFIG


class state:
    from share.shared.logger.print import Logger
    log = Logger()

class pathlabel(BaseModel):
    relative : str
    absolute : str
    
class ConfigConf(BaseModel):
    workspace : pathlabel
    package : str
    metadata : str
    
    
    #bentar, gmn sih :(
    @field_validator("package")
    def package_resolve(package) -> str:
        return package.replace("[ABS]", self.workspace.absolute)
    
    @field_validator("metadata")
    def metadata_resolve(metadata) -> str:
        return metadata.replace("[ABS]", self.workspace.absolute)

class parser:
    def __init__(self) -> None:
        self.handler_workspace()
    
    def handler_workspace(self) -> json.dumps:
        def sign_path(value: dict) -> json.dumps:
            from pathlib import Path
            
            relative, absolute = __file__, Path(__file__).resolve
            
            file = File(REGISTRY_CONFIG)
            value["config"]["workspace"]["relative"] = relative
            value["config"]["workspace"]["absolute"] = absolute
            
            return file.Write(value).to_json
        
        file = File(REGISTRY_CONFIG)
        response = file.Read().json
        
        if not response:
            state.log.debug(f"[REGISTRY][parser:local:workspace]: '{response}' must be valuable, not empty!")
            print("[ERROR]: For details, check logs..")
            exit(1)
            
        workspace = response["config"]["workspace"]
        
        relative = workspace["relative"]
        absolute = workspace["absolute"]
        
        if relative and absolute:
            return True
        
        return sign_path(value=response)
    
    def config(self) -> ConfigConf:
        pass

class registryHandler:
    def __init__(self) -> None:
        pass
    
    @validate_parameter({"title": str, "value": str})
    def create(self, title: str, value: str) -> None:
        """
        Params:
            title: your name configuration.
            value: must object json schema.
            
        Return:
            it will True if file and value builded.
        """
        
        File("")
        