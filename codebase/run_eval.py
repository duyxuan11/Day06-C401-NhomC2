import os
import sys
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
load_dotenv()

# 2. Define Pydantic Models for Structured Output
class UIButton(BaseModel):
    label: str = Field(description="Nhãn hiển thị trên nút bấm (ví dụ: 'Xem Show Rồng Lửa (10:15)', '🚨 Chỉ đường trú mưa')")
    action: str = Field(description="Loại hành động: 'navigate' | 'update_profile' | 'suggest_dining' | 'request_alternative'")
    target_id: Optional[str] = Field(default=None, description="Mã attraction_id tương ứng nếu action là 'navigate', ngược lại là null")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Dữ liệu bổ sung nếu cần (ví dụ: thông tin profile cập nhật)")

class WonderPathResponse(BaseModel):
    message: str = Field(description="Câu chào mừng và đề xuất lịch trình vi mô siêu ngắn gọn (tối đa 3 câu văn), tiếng Việt tự nhiên.")
    ui_buttons: List[UIButton] = Field(description="Danh sách các nút bấm phản hồi nhanh để hiển thị trên UI card.")

# 3. System Prompt Template
SYSTEM_PROMPT_TEMPLATE = """Bạn là WonderPath AI - Trợ lý dẫn đường ngữ cảnh thông minh tại công viên phức hợp giải trí lớn. 
Nhiệm vụ của bạn là phân tích ngữ cảnh hiện tại của du khách và đề xuất lịch trình vi mô (1-2 tiếng tiếp theo) tối ưu, an toàn và cá nhân hóa nhất.

Dữ liệu hệ thống cung cấp cho bạn gồm:
1. Danh sách trò chơi tĩnh (attractions):
{attractions}

2. Bản đồ các trạm QR (stations):
{stations}

3. Trạng thái vận hành & hàng đợi thời gian thực (realtime_status):
{realtime_status}

4. Thời tiết hiện tại (weather):
{weather}

Ngữ cảnh hiện tại của du khách quét QR:
- Mã trạm quét QR hiện tại: {current_station_id}
- Thời gian quét: {current_time}
- Thông tin nhóm du khách (user_profile): {user_profile} (nếu null tức là chưa có thông tin phân loại nhóm du khách).

QUY TẮC XỬ LÝ LỊCH TRÌNH VÀ RỦI RO (FAILURE MODES):
1. [QUY TẮC THỜI TIẾT]: Nếu weather.warning_level là "red" (dông bão cực đoan), lập tức ẨN mọi gợi ý ngoài trời (outdoor). Đưa ra cảnh báo đỏ và gợi ý 1-2 điểm trú ẩn hoặc vui chơi trong nhà (indoor) an toàn và gần trạm quét nhất.
2. [QUY TẮC BẢO TRÌ/QUÁ TẢI]: Đối chiếu trạng thái các trò chơi lân cận trong `realtime_status`. Nếu trò chơi định gợi ý đang có trạng thái "maintenance" hoặc thời gian xếp hàng > 45 phút, KHÔNG gợi ý trò đó nữa. Hãy chủ động gợi ý trò chơi thay thế gần nhất có hàng đợi ngắn (< 20 phút) hoặc khu ẩm thực/nghỉ ngơi lân cận.
3. [QUY TẮC PROFILE]:
   - Nếu user_profile là null: Đưa ra câu chào ngắn gọn và hỏi lại thông tin nhóm du khách để phân loại thông qua các nút bấm. Không tự tiện gợi ý lịch trình chi tiết khi chưa biết đối tượng.
   - Nếu user_profile có trẻ nhỏ/người già: Lọc bỏ toàn bộ trò chơi có thrill_level là "high" hoặc vi phạm giới hạn chiều cao (min_height_cm). Gợi ý các trò nhẹ nhàng (thrill_level: "low"), có tính chất gia đình, hoặc khu vui chơi trong nhà (KidZone).
   - Nếu user_profile là nhóm bạn trẻ (thrill_seekers): Ưu tiên gợi ý các trò cảm giác mạnh (thrill_level: "high" hoặc "medium"), các show diễn hấp dẫn và đồ ăn nhanh.
4. [QUY TẮC LỊCH TRÌNH VI MÔ]: Gợi ý tối đa 2 hoạt động/trò chơi tiếp theo trong vòng 1-2 tiếng tới, nêu rõ lý do lựa chọn ngắn gọn (ví dụ: khoảng cách gần bao nhiêu mét, thời gian chờ bao nhiêu phút, hoặc sắp đến giờ show diễn).

YÊU CẦU ĐẦU RA (OUTPUT FORMAT):
Bạn PHẢI trả về cấu trúc dữ liệu JSON chính xác theo Schema đã định nghĩa (WonderPathResponse), chứa hai trường: 'message' và 'ui_buttons'."""

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

        # Handle overrides
        # 1. Weather
        weather = base_weather["current"]
        if ctx.get("weather_override"):
            weather = ctx["weather_override"]

        # 2. Realtime status
        realtime = base_realtime["attractions"]
        if ctx.get("status_override"):
            override_map = ctx["status_override"]
            # Clone list to avoid modifying base
            realtime = [dict(item) for item in realtime]
            for item in realtime:
                att_id = item["attraction_id"]
                if att_id in override_map:
                    item.update(override_map[att_id])

        # Render Prompt
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            attractions=json.dumps(attractions, ensure_ascii=False, indent=2),
            stations=json.dumps(stations, ensure_ascii=False, indent=2),
            realtime_status=json.dumps(realtime, ensure_ascii=False, indent=2),
            weather=json.dumps(weather, ensure_ascii=False, indent=2),
            current_station_id=qr_station_id,
            current_time=scan_time,
            user_profile=json.dumps(user_profile, ensure_ascii=False, indent=2)
        )

        if dry_run:
            print(f"  [DRY RUN] Prompt được render thành công cho {sc_id} (Độ dài: {len(prompt)} ký tự).")
            results.append({
                "id": sc_id,
                "name": sc_name,
                "passed": True,
                "mismatch_reason": "Dry run (Bypass API Call)",
                "actual": None
            })
            continue

        # Call Gemini API
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=WonderPathResponse,
                    temperature=0.1
                )
            )

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

            # Match buttons
            # We check if all expected button actions and target_ids are present in actual buttons
            for exp_btn in expected_buttons:
                exp_action = exp_btn["action"]
                exp_target = exp_btn.get("target_id")
                
                # Try to find a match in actual buttons
                matched = False
                for act_btn in actual_buttons:
                    act_action = act_btn.get("action")
                    act_target = act_btn.get("target_id")
                    
                    # Exact action match and target match (handling None/null)
                    if act_action == exp_action and (act_target == exp_target or (not act_target and not exp_target)):
                        matched = True
                        break
                
                if not matched:
                    target_str = f" với target_id '{exp_target}'" if exp_target else ""
                    failures.append(f"Thiếu nút bấm với hành động '{exp_action}'{target_str} (Kỳ vọng nhãn: '{exp_btn['label']}')")

            passed = len(failures) == 0
            mismatch_reason = "; ".join(failures) if not passed else "Khớp hoàn toàn hành động nút bấm."
            
            print(f"  Result: {'PASS' if passed else 'FAIL'}")
            if not passed:
                print(f"  Mismatches: {mismatch_reason}")
                print(f"  Actual response message: {actual_message}")
                print(f"  Actual buttons: {json.dumps(actual_buttons, ensure_ascii=False)}")

            results.append({
                "id": sc_id,
                "name": sc_name,
                "passed": passed,
                "mismatch_reason": mismatch_reason,
                "actual": actual_data
            })

        except Exception as e:
            print(f"  [ERROR] Lỗi khi gọi hoặc parse kết quả từ API: {e}")
            results.append({
                "id": sc_id,
                "name": sc_name,
                "passed": False,
                "mismatch_reason": f"API Error: {e}",
                "actual": None
            })

    # Print summary table
    print("\n" + "="*80)
    print(f"{'KỊCH BẢN KIỂM THỬ':<45} | {'TRẠNG THÁI':<10} | {'CHI TIẾT ĐỐI SOÁT'}")
    print("="*80)
    passed_count = 0
    for r in results:
        status_str = "PASS" if r["passed"] else "FAIL"
        print(f"{r['name'][:43]:<45} | {status_str:<10} | {r['mismatch_reason']}")
        if r["passed"]:
            passed_count += 1
    print("="*80)
    print(f"Tổng số: {passed_count}/{len(scenarios)} kịch bản ĐẠT ({round(passed_count/len(scenarios)*100, 2)}%).\n")

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
            "accuracy": passed_count / len(scenarios)
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
