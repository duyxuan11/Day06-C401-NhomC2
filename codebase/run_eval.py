import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

# Force UTF-8 encoding for stdout/stderr to avoid UnicodeEncodeError on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 1. Load Environment Variables
load_dotenv(Path(__file__).resolve().parent / "backend" / ".env")

# 2. Define Pydantic Models for Structured Output
class UIButton(BaseModel):
    label: str = Field(description="Nhãn hiển thị trên nút bấm (ví dụ: 'Xem Show Rồng Lửa (10:15)', '🚨 Chỉ đường trú mưa')")
    action: str = Field(description="Loại hành động: 'navigate' | 'update_profile' | 'suggest_dining' | 'request_alternative'")
    target_id: Optional[str] = Field(default=None, description="Mã attraction_id tương ứng nếu action là 'navigate', ngược lại là null")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Dữ liệu bổ sung nếu cần (ví dụ: thông tin profile cập nhật)")

class WonderPathResponse(BaseModel):
    message: str = Field(description="Câu chào mừng và đề xuất lịch trình vi mô siêu ngắn gọn (tối đa 3 câu văn), tiếng Việt tự nhiên.")
    ui_buttons: List[UIButton] = Field(description="Danh sách các nút bấm phản hồi nhanh để hiển thị trên UI card.")

# Pydantic sinh JSON Schema co cac field nhu `default`/`anyOf` ma SDK
# google.generativeai cu khong chap nhan. Schema thu cong nay chi dung
# cac field duoc Gemini ho tro: type, properties, required, nullable.
GEMINI_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description": "Câu chào mừng và đề xuất lịch trình vi mô siêu ngắn gọn bằng tiếng Việt."
        },
        "ui_buttons": {
            "type": "array",
            "description": "Danh sách các nút bấm phản hồi nhanh để hiển thị trên UI card.",
            "items": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "Nhãn hiển thị trên nút bấm."
                    },
                    "action": {
                        "type": "string",
                        "description": "Loại hành động.",
                        "enum": [
                            "navigate",
                            "update_profile",
                            "suggest_dining",
                            "request_alternative"
                        ]
                    },
                    "target_id": {
                        "type": "string",
                        "nullable": True,
                        "description": "Mã attraction_id nếu action là navigate, ngược lại là null."
                    },
                    "data": {
                        "type": "object",
                        "nullable": True,
                        "description": "Dữ liệu bổ sung nếu cần, ví dụ thông tin profile cập nhật."
                    }
                },
                "required": ["label", "action"]
            }
        }
    },
    "required": ["message", "ui_buttons"]
}

# 3. Import services from codebase
sys.path.append(str(Path(__file__).resolve().parent / "backend"))
from server.services.context_builder import build_wonder_path_context
from server.ai.prompt import build_wonder_path_prompt


def run_evaluation(
    model_name: str, 
    scenarios_path: Path, 
    mock_data_dir: Path, 
    dry_run: bool
) -> None:
    # Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and not dry_run:
        print("\n[ERROR] GEMINI_API_KEY không được tìm thấy trong biến môi trường hoặc file .env.")
        print("Vui lòng thiết lập biến môi trường hoặc chạy với cờ --dry-run để chạy kiểm tra cấu trúc prompt.\n")
        return

    if not dry_run:
        genai.configure(api_key=api_key)

    # Load static data
    print("Loading mock data...")
    attractions = json.loads((mock_data_dir / "attractions.json").read_text(encoding="utf-8"))
    stations = json.loads((mock_data_dir / "stations.json").read_text(encoding="utf-8"))
    base_realtime = json.loads((mock_data_dir / "realtime_status.json").read_text(encoding="utf-8"))
    base_weather = json.loads((mock_data_dir / "weather.json").read_text(encoding="utf-8"))
    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))

    results = []
    print(f"\nBắt đầu chạy đánh giá trên {len(scenarios)} kịch bản...\n")

    for idx, sc in enumerate(scenarios, 1):
        sc_id = sc["id"]
        sc_name = sc["name"]
        print(f"[{idx}/{len(scenarios)}] Đang chạy: {sc_name}")

        ctx = sc["input_context"]
        qr_station_id = ctx["qr_station_id"]
        scan_time = ctx["scan_time"]
        user_profile = ctx["user_profile"]

        # Build input data structure with overrides
        input_data = {
            "qr_station_id": qr_station_id,
            "scan_time": scan_time,
            "user_profile": user_profile,
            "weather_override": ctx.get("weather_override"),
            "status_override": ctx.get("status_override")
        }

        # Build context using context_builder
        context = build_wonder_path_context(input_data, mock_data={
            "attractions": attractions,
            "stations": stations,
            "realtime_status": base_realtime,
            "weather": base_weather
        })

        # Build prompt using the prompt builder
        prompt = build_wonder_path_prompt(context)

        if dry_run:
            print(f"  [DRY RUN] Prompt được render thành công cho {sc_id} (Độ dài: {len(prompt)} ký tự).")
            results.append({
                "id": sc_id,
                "name": sc_name,
                "passed": True,
                "mismatch_reason": "Dry run (Bypass API Call)",
                "latency_seconds": 0.0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "actual": None
            })
            continue
        # Call Gemini API
        try:
            if idx > 1:
                print("Đang nghỉ 12 giây để tránh rate limit (Free Tier)...")
                time.sleep(12)
            model = genai.GenerativeModel(model_name)
            start_time = time.time()
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=GEMINI_RESPONSE_SCHEMA,
                    temperature=0.0
                ),
                request_options={"timeout": 30}
            )
            latency_seconds = time.time() - start_time

            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
                total_tokens = getattr(response.usage_metadata, "total_token_count", 0)

            actual_data = json.loads(response.text)
            actual_buttons = actual_data.get("ui_buttons", [])
            actual_message = actual_data.get("message", "")

            # Evaluate against expected behavior
            expected_behavior = sc["expected_behavior"]
            expected_buttons = expected_behavior.get("ui_buttons", [])

            failures = []
            
            # Check if message is empty
            if not actual_message.strip():
                failures.append("Câu chào/thông báo trả về rỗng.")

            # Match buttons.
            # If expected has no target_id, action match is enough. This lets generic
            # actions like suggest_dining carry optional metadata without failing.
            for exp_btn in expected_buttons:
                exp_action = exp_btn["action"]
                exp_target = exp_btn.get("target_id")
                
                # Try to find a match in actual buttons
                matched = False
                for act_btn in actual_buttons:
                    act_action = act_btn.get("action")
                    act_target = act_btn.get("target_id")
                    
                    action_matches = act_action == exp_action
                    target_matches = not exp_target or act_target == exp_target
                    dining_destination_matches = (
                        exp_action == "navigate"
                        and act_action == "suggest_dining"
                        and exp_target
                        and act_target == exp_target
                    )

                    if target_matches and (action_matches or dining_destination_matches):
                        matched = True
                        break
                
                if not matched:
                    target_str = f" với target_id '{exp_target}'" if exp_target else ""
                    failures.append(f"Thiếu nút bấm với hành động '{exp_action}'{target_str} (Kỳ vọng nhãn: '{exp_btn['label']}')")

            passed = len(failures) == 0
            mismatch_reason = "; ".join(failures) if not passed else "Khớp hoàn toàn hành động nút bấm."
            
            print(f"  Result: {'PASS' if passed else 'FAIL'} (Latency: {latency_seconds:.2f}s, Tokens: {total_tokens})")
            if not passed:
                print(f"  Mismatches: {mismatch_reason}")
                print(f"  Actual response message: {actual_message}")
                print(f"  Actual buttons: {json.dumps(actual_buttons, ensure_ascii=False)}")

            results.append({
                "id": sc_id,
                "name": sc_name,
                "passed": passed,
                "mismatch_reason": mismatch_reason,
                "latency_seconds": round(latency_seconds, 3),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "actual": actual_data
            })

        except Exception as e:
            latency_seconds = time.time() - start_time if 'start_time' in locals() else 0.0
            print(f"  [ERROR] Lỗi khi gọi hoặc parse kết quả từ API: {e}")
            results.append({
                "id": sc_id,
                "name": sc_name,
                "passed": False,
                "mismatch_reason": f"API Error: {e}",
                "latency_seconds": round(latency_seconds, 3),
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "actual": None
            })

    # Print summary table
    print("\n" + "="*120)
    print(f"{'KỊCH BẢN KIỂM THỬ':<40} | {'TRẠNG THÁI':<10} | {'THỜI GIAN (S)':<12} | {'TOKENS (P/C/T)':<16} | {'CHI TIẾT ĐỐI SOÁT'}")
    print("="*120)
    passed_count = 0
    total_lat = 0.0
    total_p_tok = 0
    total_c_tok = 0
    total_t_tok = 0

    for r in results:
        status_str = "PASS" if r["passed"] else "FAIL"
        latency_str = f"{r.get('latency_seconds', 0.0):.3f}"
        tokens_str = f"{r.get('prompt_tokens', 0)}/{r.get('completion_tokens', 0)}/{r.get('total_tokens', 0)}"
        print(f"{r['name'][:38]:<40} | {status_str:<10} | {latency_str:<12} | {tokens_str:<16} | {r['mismatch_reason']}")
        if r["passed"]:
            passed_count += 1
        total_lat += r.get("latency_seconds", 0.0)
        total_p_tok += r.get("prompt_tokens", 0)
        total_c_tok += r.get("completion_tokens", 0)
        total_t_tok += r.get("total_tokens", 0)

    print("="*120)
    print(f"Tổng số: {passed_count}/{len(scenarios)} kịch bản ĐẠT ({round(passed_count/len(scenarios)*100, 2)}%).")
    if not dry_run and len(scenarios) > 0:
        avg_lat = total_lat / len(scenarios)
        print(f"Hiệu năng trung bình: Latency = {avg_lat:.3f}s | Tổng Tokens tiêu thụ = {total_t_tok} (Prompt: {total_p_tok}, Output: {total_c_tok})\n")

    # Save run report
    runs_dir = mock_data_dir.parent / "runs"
    runs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    report_file = runs_dir / f"eval_run_{timestamp}.json"
    
    report_payload = {
        "timestamp": datetime.now().isoformat(),
        "model_name": model_name,
        "dry_run": dry_run,
        "summary": {
            "total": len(scenarios),
            "passed": passed_count,
            "failed": len(scenarios) - passed_count,
            "accuracy": passed_count / len(scenarios),
            "total_latency_seconds": round(total_lat, 3),
            "avg_latency_seconds": round(total_lat / len(scenarios), 3) if len(scenarios) > 0 else 0.0,
            "total_prompt_tokens": total_p_tok,
            "total_completion_tokens": total_c_tok,
            "total_tokens": total_t_tok,
            "avg_tokens_per_call": round(total_t_tok / len(scenarios), 1) if len(scenarios) > 0 else 0.0
        },
        "details": results
    }
    
    report_file.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã lưu báo cáo chạy eval chi tiết tại: {report_file}\n")


def main():
    parser = argparse.ArgumentParser(description="Chương trình chạy đánh giá tự động (Eval) cho mô hình WonderPath AI.")
    parser.add_argument("--model", type=str, default="gemini-1.5-flash", help="Tên model Gemini sử dụng (mặc định: gemini-1.5-flash)")
    parser.add_argument("--scenarios", type=str, default="mock-data/test_scenarios.json", help="Đường dẫn đến file test scenarios (mặc định: mock-data/test_scenarios.json)")
    parser.add_argument("--mock-data-dir", type=str, default="mock-data", help="Thư mục chứa mock data (mặc định: mock-data)")
    parser.add_argument("--dry-run", action="store_true", help="Nếu bật, chỉ kiểm tra logic sinh prompt mà không gọi Gemini API thực tế")
    args = parser.parse_args()

    scenarios_path = Path(args.scenarios)
    mock_data_dir = Path(args.mock_data_dir)
    
    run_evaluation(args.model, scenarios_path, mock_data_dir, args.dry_run)

if __name__ == "__main__":
    main()
