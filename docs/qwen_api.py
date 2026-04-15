import json
import os
from dashscope import MultiModalConversation
import dashscope

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

messages = [
    {
        "role": "user",
        "content": [
            {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/thtclx/input1.png"},
            {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/iclsnx/input2.png"},
            {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/gborgw/input3.png"},
            {"text": "Make the girl from Image 1 wear the black dress from Image 2 and sit in the pose from Image 3."}
        ]
    }
]

# If you have not configured the environment variable, replace the following line with your Model Studio API Key: api_key="sk-xxx"
api_key = os.getenv("DASHSCOPE_API_KEY")

response = MultiModalConversation.call(
    api_key=api_key,
    model="qwen-image-2.0",
    messages=messages,
    result_format='message',
    stream=False,
    n=2,
    watermark=True,
    negative_prompt=""
)

print(json.dumps(response, ensure_ascii=False))