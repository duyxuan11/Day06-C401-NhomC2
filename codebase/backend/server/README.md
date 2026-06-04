# WonderPath AI Python server helpers

Thu muc nay gom phan Python lien quan den AI logic cua WonderPath.

## Phan cua Le Duy Hung

- `ai/prompt.py`: tao prompt gui sang Gemini.
- `ai/response_schema.py`: dinh nghia JSON output ma Gemini phai tra ve va normalize response.
- `ai/gemini_client.py`: ham goi Gemini API va parse JSON response.
- `services/context_builder.py`: ghep QR station, weather, realtime status, attractions va user profile thanh context day du.
- `services/mock_data_service.py`: doc du lieu tu `codebase/mock-data`.
- `utils/safety_rules.py`: rule an toan de loc tro bao tri, hang doi qua lau, tro ngoai troi khi thoi tiet xau, va tro khong phu hop profile.

Backend Python cua nhom co the goi flow:

```python
from server.services.context_builder import build_wonder_path_context
from server.ai.gemini_client import generate_itinerary_with_gemini

context = build_wonder_path_context(request_json)
result = generate_itinerary_with_gemini(context)
return result
```
