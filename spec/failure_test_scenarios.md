# KỊCH BẢN KIỂM THỬ FAILURE PATH & CORRECTION — WONDERPATH AI

* **Owner phụ trách:** Tạ Duy Xuân (Mã học viên: `2A202600970`)
* **Vai trò:** Đảm bảo hệ thống vận hành an toàn (Safety-First), nhận biết lỗi/ngoại lệ vận hành thông minh và hỗ trợ người dùng đính chính hành vi (Human-in-the-loop).

---

## I. Môi Trường & Dữ Liệu Giả Lập (Mock Data Configuration)

Để thực hiện các kịch bản kiểm thử lỗi và ngoại lệ mà không cần đợi thời tiết xấu hay thiết bị hỏng thật, Backend và Frontend hỗ trợ cơ chế giả lập trực tiếp qua các cấu trúc tham số đầu vào trong API `/api/recommend`:

1. **Giả lập trạm quét QR (`qr_station_id` / `current_station_id`):** Xác định vị trí địa lý tức thời của du khách mà không cần GPS chập chờn (Trạm 1 đến Trạm 4).
2. **Giả lập thông tin thời tiết (`weather_override`):** Ghi đè trạng thái thời tiết thực tế thành dông bão cực đoan (`stormy`, `warning_level: red`).
3. **Giả lập trạng thái vận hành (`status_override`):** Đặt trạng thái trò chơi cụ thể sang bảo trì định kỳ (`status: maintenance`) hoặc hàng đợi quá tải (`wait_time_mins > 45`).
4. **Giả lập thông điệp đính chính (`user_message`):** Truyền trực tiếp câu thoại đính chính hoặc yêu cầu bằng ngôn ngữ tự nhiên từ người dùng vào chatbot để kiểm tra phản ứng của AI.

---

## II. Danh Sách Kịch Bản Kiểm Thử Chi Tiết

### 1. TC-01: Định vị qua QR & Thiếu thông tin phân khúc (Low-Confidence Path)
* **Mục tiêu:** Xác minh hệ thống không bị crash, đưa ra gợi ý mặc định ban đầu an toàn tại trạm quét QR và cung cấp các lựa chọn cập nhật profile phù hợp.
* **Các bước thực hiện:**
  1. Quét mã QR tại Trạm 1 (`qr_station_id` là `"qr_station_01"` - Cổng Khu Cổ Tích).
  2. Không cung cấp thông tin profile người dùng (`user_profile` bằng `null`).
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "qr_station_id": "qr_station_01",
    "scan_time": "14:00",
    "user_profile": null,
    "weather_override": {
      "condition": "sunny",
      "temperature_c": 33,
      "warning_level": "none"
    },
    "status_override": {}
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot chào mừng người dùng tại Cổng Khu Cổ Tích, gợi ý trải nghiệm Lâu Đài Huyền Bí (`att_magic_castle`) ngay gần đó và hiển thị nút cập nhật profile để cá nhân hóa lộ trình.
  * Danh sách nút bấm hiển thị trên UI:
    1. `[Cá nhân hóa lộ trình]` (action: `update_profile`, target_id: `null`)
    2. `[Đến Lâu Đài Huyền Bí]` (action: `navigate`, target_id: `"att_magic_castle"`)
    3. `[Tìm chỗ ăn uống gần đây]` (action: `suggest_dining`, target_id: `null`)

---

### 2. TC-02: Gợi ý trò chơi đang bảo trì đột xuất (Failure Path)
* **Mục tiêu:** Xác minh hệ thống phát hiện trò chơi chính tại trạm đang bảo trì và tự động tìm phương án thay thế phù hợp với nhóm tuổi/chiều cao cùng trạm ăn uống lân cận.
* **Các bước thực hiện:**
  1. Nhóm bạn trẻ quét QR tại Trạm 2 (`qr_station_id` là `"qr_station_02"` - Ngã Tư Phiêu Lưu).
  2. Thiết lập trạng thái trò chơi Tàu Lượn Siêu Tốc (`att_roller_coaster`) sang `"maintenance"`.
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "qr_station_id": "qr_station_02",
    "scan_time": "11:00",
    "user_profile": {
      "min_age": 18,
      "max_age": 25,
      "min_height_cm": 165
    },
    "weather_override": {
      "condition": "sunny",
      "temperature_c": 32,
      "warning_level": "none"
    },
    "status_override": {
      "att_roller_coaster": {
        "status": "maintenance",
        "wait_time_mins": 0,
        "crowd_level": "low"
      }
    }
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot nhận diện Tàu Lượn Siêu Tốc đang bảo trì, tự động đề xuất đổi sang Đu Quay Dây Văng (`att_swing_carousel` cách 600m) và ghé Khu Ẩm Thực Nhanh Express (`att_food_court_fast` cách 150m) nạp năng lượng.
  * Danh sách nút bấm hiển thị trên UI:
    1. `[Đến Đu Quay Dây Văng]` (action: `navigate`, target_id: `"att_swing_carousel"`)
    2. `[Đến Khu Ẩm Thực Nhanh]` (action: `navigate`, target_id: `"att_food_court_fast"`)
    3. `[Đổi phương án khác]` (action: `request_alternative`, target_id: `null`)

---

### 3. TC-03: Thời tiết thay đổi đột ngột sang dông bão (Dangerous Failure Mode / Emergency Path)
* **Mục tiêu:** Xác minh tính năng quan trọng nhất về an toàn (Safety-First) khi thời tiết chuyển dông bão cực đoan. Hệ thống lập tức ẩn tất cả các trò chơi ngoài trời và dẫn du khách tới khu vực trú ẩn an toàn có mái che gần nhất.
* **Các bước thực hiện:**
  1. Người dùng quét QR tại Trạm 3 (`qr_station_id` là `"qr_station_03"` - Bến Thuyền Hồ Trung Tâm).
  2. Thiết lập thời tiết giông bão mạnh cảnh báo đỏ (`warning_level: red`).
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "qr_station_id": "qr_station_03",
    "scan_time": "15:00",
    "user_profile": {
      "min_age": 4,
      "max_age": 68,
      "min_height_cm": 95
    },
    "weather_override": {
      "condition": "stormy",
      "temperature_c": 24,
      "warning_level": "red"
    },
    "status_override": {}
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot hiển thị cảnh báo thời tiết nguy hiểm ngoài trời, ẩn toàn bộ trò chơi ngoài trời. Đề xuất trú mưa khẩn cấp tại Chòi Nghỉ Mát Ven Hồ (`att_lakeside_gazebo` cách 30m) hoặc di chuyển vào Khu Vui Chơi Trong Nhà KidZone (`att_indoor_playground` cách 250m).
  * Danh sách nút bấm hiển thị trên UI:
    1. `[Trú mưa tại Chòi Ven Hồ (30m)]` (action: `navigate`, target_id: `"att_lakeside_gazebo"`)
    2. `[Đến Khu Trong Nhà KidZone (250m)]` (action: `navigate`, target_id: `"att_indoor_playground"`)

---

### 4. TC-04: Trò chơi chính quá tải hàng đợi (Queue Overload Path)
* **Mục tiêu:** Xác minh hệ thống tự động phát hiện trò chơi đề xuất chính bị quá tải (thời gian chờ xếp hàng $> 45$ phút), ẩn trò chơi đó và hướng người dùng sang khu vực ăn uống nghỉ ngơi lân cận để tránh kiệt sức và giãn đám đông.
* **Các bước thực hiện:**
  1. Nhóm bạn trẻ quét QR tại Trạm 4 (`qr_station_id` là `"qr_station_04"` - Cổng Công Viên Nước).
  2. Thiết lập thời gian chờ của Đường Trượt Nước Lốc Xoáy (`att_water_slide`) là 50 phút.
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "qr_station_id": "qr_station_04",
    "scan_time": "14:30",
    "user_profile": {
      "min_age": 16,
      "max_age": 28,
      "min_height_cm": 155
    },
    "weather_override": {
      "condition": "sunny",
      "temperature_c": 35,
      "warning_level": "none"
    },
    "status_override": {
      "att_water_slide": {
        "status": "active",
        "wait_time_mins": 50,
        "crowd_level": "high"
      }
    }
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot thông báo Đường Trượt Nước Lốc Xoáy đang quá tải (chờ 50 phút). Gợi ý nhóm ghé qua Khu Ẩm Thực Nhanh Express (`att_food_court_fast` cách 220m) để uống nước giải nhiệt và nghỉ ngơi chờ hạ nhiệt đám đông.
  * Danh sách nút bấm hiển thị trên UI:
    1. `[Đến Khu Ẩm Thực Express]` (action: `navigate`, target_id: `"att_food_court_fast"`)
    2. `[Đổi phương án khác]` (action: `request_alternative`, target_id: `null`)

---

### 5. TC-05: Người dùng chủ động đính chính gợi ý (Correction Path)
* **Mục tiêu:** Xác minh hệ thống ghi nhận phản hồi bằng ngôn ngữ tự nhiên từ người dùng khi họ không hài lòng với gợi ý hiện tại, thực hiện cập nhật lại bộ lọc và đưa ra đề xuất thay thế nhẹ nhàng hơn.
* **Các bước thực hiện:**
  1. Chatbot đang gợi ý trò chơi cảm giác mạnh Tàu Lượn Siêu Tốc (`att_roller_coaster`).
  2. Người dùng đính chính qua khung nhập chatbox với nội dung: *"Trò này không phù hợp cho trẻ em dưới 1m"*.
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "qr_station_id": "qr_station_01",
    "scan_time": "10:00",
    "user_profile": {
      "min_age": 5,
      "max_age": 35,
      "min_height_cm": 105
    },
    "user_message": "Trò này không phù hợp cho trẻ em dưới 1m"
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot ghi nhận phản hồi đính chính, loại bỏ các trò cảm giác mạnh cao hơn 1m và đề xuất thay thế bằng trò chơi trong nhà nhẹ nhàng Lâu Đài Huyền Bí (`att_magic_castle`).
  * Danh sách nút bấm hiển thị trên UI:
    1. `[Chơi Lâu Đài Huyền Bí]` (action: `navigate`, target_id: `"att_magic_castle"`)
    2. `[Tìm nhà hàng ăn trưa gần đây]` (action: `suggest_dining`, target_id: `null`)

---

## III. Ma Trận Đánh Giá Kết Quả (Pass/Fail Criteria)

| Mã TC | Trọng tâm kiểm thử | Tiêu chí ĐẠT (Pass) | Tiêu chí HỎNG (Fail) |
|---|---|---|---|
| **TC-01** | Low-Confidence | Chatbot hiển thị lời chào, nút cập nhật profile và nút gợi ý Lâu Đài Huyền Bí, không bị crash giao diện. | App quay tròn không phản hồi hoặc hiện mã lỗi thô từ API. |
| **TC-02** | Trò chơi bảo trì | Nhận diện trạng thái bảo trì của Tàu Lượn, tự động đề xuất Đu Quay Dây Văng và Khu Ẩm Thực Express. | Vẫn hiển thị nút chỉ đường đến trò chơi đang bảo trì. |
| **TC-03** | Giông bão cực đoan | Ẩn toàn bộ trò chơi ngoài trời, hiển thị cảnh báo đỏ và 2 nút chỉ đường trú mưa KidZone & Chòi Ven Hồ. | Vẫn tiếp tục gợi ý hoặc chỉ đường đến trò ngoài trời nguy hiểm. |
| **TC-04** | Trò chơi quá tải | Tự động phát hiện hàng đợi > 45 phút, ẩn trò đó, đề xuất sang Khu Ẩm Thực Express để giải nhiệt. | Vẫn đề xuất trò chơi đang quá tải bắt khách xếp hàng lâu dưới trời nắng. |
| **TC-05** | Người dùng đính chính | Chatbot phản hồi hiểu ý kiến, không gợi ý lại trò cảm giác mạnh bị từ chối và đề xuất Lâu Đài Huyền Bí. | Không tiếp thu phản hồi, tiếp tục gợi ý trùng lặp trò chơi cảm giác mạnh. |
