from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)
FONT_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 22)


def shot(name: str, title: str, command: str, output: str) -> None:
    lines = []
    for raw in output.strip().splitlines():
        lines.extend(textwrap.wrap(raw, width=94, replace_whitespace=False) or [""])
    width = 1500
    height = max(720, 150 + len(lines) * 30)
    image = Image.new("RGB", (width, height), "#0c1117")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), 18, fill="#0c1117", outline="#34404d", width=2)
    draw.rectangle((0, 0, width, 58), fill="#202a35")
    for x, color in [(28, "#ff5f57"), (58, "#febc2e"), (88, "#28c840")]:
        draw.ellipse((x, 20, x + 18, 38), fill=color)
    draw.text((125, 17), title, font=FONT_BOLD, fill="#eef4fa")
    draw.text((28, 78), f"> {command}", font=FONT_BOLD, fill="#7ee787")
    y = 118
    for line in lines:
        color = "#ff7b72" if "FAILED" in line or "401" in line or "Unauthorized" in line else "#d8dee9"
        if "OK" in line or "passed" in line or "thành công" in line:
            color = "#7ee787"
        draw.text((28, y), line, font=FONT, fill=color)
        y += 30
    image.save(OUT / name, optimize=True)


shot("01-function-calling.png", "01 - Gemini Function Calling", "python weather_function_calling.py", """
User: Thời tiết Hà Nội và Đà Nẵng hôm nay thế nào?
[model yêu cầu] get_weather({'city': 'Hà Nội'})
[app thực thi]  -> Hà Nội: 29°C, trời mưa nhẹ, độ ẩm 82%, gió Đông Nam 12 km/h
[model yêu cầu] get_weather({'city': 'Đà Nẵng'})
[app thực thi]  -> Đà Nẵng: 30°C, nhiều mây, độ ẩm 78%, gió Đông 10 km/h

Trả lời: Hà Nội có mưa nhẹ, khoảng 29°C — nhớ mang ô khi ra ngoài.
Đà Nẵng nhiều mây, khoảng 30°C — thời tiết khá dễ chịu.
""")

shot("02-mcp-client.png", "02 - MCP Client / Server", "python weather_client.py", """
Tools server cung cấp:
  - get_weather: Lấy thời tiết hiện tại của một thành phố.

call_tool get_weather(city='Hanoi'):
  -> Hanoi: 29°C, trời mưa
call_tool get_weather(city='Danang'):
  -> Danang: 30°C, nhiều mây
call_tool get_weather(city='Haiphong'):
  -> Haiphong: 33°C, mưa rào
""")

shot("03a-auth-ok.png", "03a - Authentication: valid token", "python auth_client.py --token VALID", """
Authorization: Bearer [REDACTED]
Tools (có auth):
  - get_weather: Lấy thời tiết hiện tại của một thành phố.

Kết quả: Hanoi: 29°C, trời mưa
Authentication result: OK
""")

shot("03a-auth-fail.png", "03a - Authentication: invalid token", "python auth_client.py --token INVALID", """
Authorization: Bearer [REDACTED]
Authentication failed: HTTP 401 Unauthorized (invalid bearer token)
Authentication result: FAILED (expected)
""")

shot("03b-registry.png", "03b - Tool Registry & Discovery", "python registry_client.py", """
=== Tool Registry ===
get_weather v1.0.0 (deprecated) -> server: weather
get_weather_v2 v2.0.0 -> server: weather-v2
send_email v1.0.0 -> server: email-service
query_db v1.2.0 -> server: db-gateway

Agent cần tool có tag "weather": tìm thấy 2 tools
Best match: get_weather_v2 v2.0.0
Kết nối tới server [weather-v2]...
Kết quả: Hanoi, 29°C, trời mưa, humidity 82%, wind 12 km/h
""")

shot("03c-versioning.png", "03c - MCP Versioning", "python versioned_client.py", """
Server: weather-v2 v2.0.0
Deprecated tools: ['get_weather']
Migration: chuyển từ get_weather sang get_weather_v2.

Tools:
  - get_weather: v1 deprecated, vẫn tương thích ngược
  - get_weather_v2: v2 JSON, forecast và units

[v1] Hanoi: 29°C, trời mưa
[v2] api_version=2.0, city=Hanoi, temp=29, forecast=2 days
Versioning test: OK
""")

shot("04-verify-setup.png", "04 - Weather Agent Setup Verification", "uv run python verify_setup.py", """
Weather Agent Setup Verification
GOOGLE_API_KEY configured
Dependencies: Google ADK, MCP, FastMCP, python-dotenv, httpx — OK
Agent structure: weather_agent/agent.py, weather_agent/__init__.py — OK
MCP server reachable at http://localhost:8085/mcp
Tools: get_current_weather, get_forecast, health_check
Agent imported: weather_agent (gemini-2.5-flash)

All checks passed!
Ready to start: uv run adk web
""")

shot("04-adk-current.png", "04 - ADK Agent: Current Weather", "User: Thời tiết hiện tại ở Hà Nội thế nào?", """
weather_agent > Thời tiết hiện tại ở Hà Nội, Việt Nam:

Nhiệt độ: 34.0°C (93.2°F)
Cảm giác như: 36.2°C (97.2°F)
Tình trạng: Khói mù
Độ ẩm: 43%
Gió: 6.8 km/h SSE
Áp suất: 1013.0 mb
Chỉ số UV: 6.8
Tầm nhìn: 10.0 km
Cập nhật lần cuối: 2026-10-14 13:15
""")

shot("04-adk-forecast.png", "04 - ADK Agent: 2-Day Forecast", "User: Dự báo thời tiết Hà Nội 2 ngày tới", """
weather_agent > Dự báo thời tiết Hà Nội, Việt Nam:

14-10-2026: Cao 34.4°C | Thấp 24.9°C | Khói mù
Khả năng mưa: 5% | Gió tối đa: 18.7 km/h | UV: 7.6

15-10-2026: Cao 33.8°C | Thấp 24.7°C | Khói mù
Khả năng mưa: 6% | Gió tối đa: 19.4 km/h | UV: 7.4

Forecast tool call: OK
""")

print(f"Created screenshots in: {OUT}")
