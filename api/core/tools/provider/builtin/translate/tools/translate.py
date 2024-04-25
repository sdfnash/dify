from typing import Any, Union
import requests
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from datetime import datetime
import random
import string
import json


class TranslateTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[
        ToolInvokeMessage, list[ToolInvokeMessage]]:
        text = tool_parameters.get('text', '')
        if not text:
            return self.create_text_message('Text parameter is required for translation.')

        try:
            translate_header = {"X-Task_Type": "translate_text", "SN-REQID": self.generate_req_id()}
            response = requests.post('http://aigcplugin-gateway-test.weibo.com/task/add',
                                     json=self.build_translate_json(text), headers=translate_header)
            response.raise_for_status()
            response_json = response.json()
            print(f'获取响应数据： {response_json}')
            return self.create_text_message(self.parse_translate_result(response_json))
        except Exception as e:
            return self.create_text_message(f'Translation failed: {str(e)}')

    def gen_task_id(self):
        time_str = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-2]
        rand = random.randint(100000, 999999)
        return time_str + str(rand)

    def generate_req_id(self):
        characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return ''.join(random.choice(characters) for _ in range(32))

    def build_translate_json(self, text):
        new_json = {"task_id": self.gen_task_id()}
        task_content_json = {"text": text}
        new_json["task_content"] = task_content_json
        return new_json

    def parse_translate_result(self, response_json):
        if response_json['code'] == 0 and response_json['msg'] == "successful":
            data = response_json['data']
            if 'task_result' in data and 'translate_text' in data['task_result']:
                return data['task_result']['translate_text']
            else:
                return "Translate text not found."
        else:
            return "Error in response: " + response_json['msg'] + ', ' + response_json['code']
