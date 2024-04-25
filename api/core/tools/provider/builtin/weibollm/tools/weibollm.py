from typing import Any, Union
import requests
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from datetime import datetime
import random
import string
import json
import time


# todo 待抽取工具类，配置类
def gen_task_id():
    time_str = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-2]
    rand = random.randint(100000, 999999)
    return time_str + str(rand)


def build_llm_json(text):
    new_json = {"task_id": gen_task_id()}
    prompt_template = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": text}]}
    task_content_json = {"prompt": json.dumps(prompt_template)}
    new_json["task_content"] = task_content_json
    print(f'build_llm_json: {new_json}')
    return (new_json)


def generate_req_id():
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(32))


# todo 配置类
AIGC_GATE_WAY_HOST = 'http://aigcplugin-gateway-test.weibo.com'


class LLMTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[
        ToolInvokeMessage, list[ToolInvokeMessage]]:
        text = tool_parameters.get('text', '')
        if not text:
            return self.create_text_message('Text parameter is required for translation.')

        task_id = self.send_llm_task(text)
        if task_id:
            try:
                return self.poll_for_results(task_id)
            except Exception as e:
                return self.create_text_message(f'Error polling results: {str(e)}')
        else:
            return self.create_text_message('Failed to submit translation task.')

    def send_llm_task(self, text: str) -> Any | None:
        try:
            llm_header = {"X-Task_Type": "llm_gpt", "X-Token": "8325F0E801C247FF828B8320EFC7586B",
                          "SN-REQID": generate_req_id()}
            response = requests.post(f'{AIGC_GATE_WAY_HOST}/task/add',
                                     json=build_llm_json(text), headers=llm_header)
            response.raise_for_status()
            response_json = response.json()
            if response_json['code'] == 0:
                return response_json['data']['task_id']
            else:
                print(f'Error submitting task: {response_json["msg"]}')
        except Exception as e:
            print(f'Exception submitting task: {str(e)}')
        return None

    def poll_for_results(self, task_id: str):
        url = f'{AIGC_GATE_WAY_HOST}/task/progress'
        headers = {"X-Task_Type": "llm_gpt_progress", 'X-Token': '8325F0E801C247FF828B8320EFC7586B',
                   'Content-Type': 'application/json; charset=utf-8', "SN-REQID": generate_req_id()}
        max_attempts = 60
        for attempt in range(max_attempts):
            response = requests.post(url, json={"task_id": task_id}, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            print(f'Polling attempt {attempt}: {response_data}')
            if response_data['data']['progress'] == 1.0:
                return self.create_text_message(
                    response_data['data']['task_result'].get('content', 'No content available'))
            time.sleep(1)
        return self.create_text_message('llm task did not complete within the expected time.')
