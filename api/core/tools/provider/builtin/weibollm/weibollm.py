from typing import Any
from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.weibollm.tools.weibollm import LLMTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class WeiboLLMProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            LLMTool().invoke(
                user_id='',
                tool_parameters={'text': ''},
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
