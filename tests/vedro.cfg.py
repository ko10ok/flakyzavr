import vedro
import vedro_valera_validator as valera_validator
from vedro.plugins.director import RichReporter


class Config(vedro.Config):
    class Plugins(vedro.Config.Plugins):
        class ValeraValidator(valera_validator.ValeraValidator):
            enabled = True

        class RichReporter(RichReporter):
            enabled = True
            scope_width = -1
            show_paths = 'failed'
