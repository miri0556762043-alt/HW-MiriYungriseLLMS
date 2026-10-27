from openai import OpenAI
import httpx

API_KEY_SAFEAI = "sk-safeai-dfa2d649b8d1b5c974a5f72e9757e3d6b604d5f7ade2ce1"
BASE_URL = "https://safeai613.com/v1"

httpx_client = httpx.Client(http2=True, verify=False)

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY_SAFEAI,
    http_client=httpx_client
)

response = client.responses.create(
    model="gpt-5.4-nano",
    input="תיצור לי דף בית לאתר עם עיצוב בסגנון css tailwind"
)

print(response.output_text)