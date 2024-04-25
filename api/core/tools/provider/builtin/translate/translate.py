from typing import Any
from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.translate.tools.translate import TranslateTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController

class TranslateProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            TranslateTool().invoke(
                user_id='',
                tool_parameters={'text': ''},
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))