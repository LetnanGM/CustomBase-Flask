from .parser import Parser, _name_file, _suffix
from bowlplate.share.builtns.handler.decorator import validate_parameter

"""
structure plugins folder:
plugins/web/csrf/manifest.json

plugins > parent
[any]   > parent 2
[any]   > child
manifest> on child folder

example :
plugins > parent
web     > parent 2
csrf    > child
manifest> csrf metadata plugin

```pseudo
plugins \
    web \
        csrf \
            manifest.json
```
"""


class Plugins:
    def __init__(self) -> None:
        self.reader = Parser()
        self.manifest = "".join([_name_file, _suffix])

    @validate_parameter({"manifest_path": str})
    def resolve_manifest(self, manifest_path: str) -> None:
        from pathlib import Path

        path = Path(manifest_path).resolve()

        if not path.is_file():
            return None

        self.reader.load_manifest(str(path))

    def load_all(self):
        from bowlplate import PLUGIN_ROOT
        import os

        @validate_parameter({"module_folder": str})
        def resolve_plugin(module_folder: str) -> None:
            module_path = os.path.join(PLUGIN_ROOT, module_folder)

            for plugin in os.listdir(module_path):
                plugin_path = os.path.join(module_path, plugin)

                files = set(os.listdir(plugin_path))

                if self.manifest in files:
                    self.resolve_manifest(
                        manifest_path=os.path.join(plugin_path, self.manifest)
                    )

        for module in os.listdir(PLUGIN_ROOT):
            module_path = os.path.join(PLUGIN_ROOT, module)

            if not os.path.isdir(module_path):
                continue

            resolve_plugin(module)
