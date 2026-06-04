# KỊCH BẢN KIỂM THỬ FAILURE PATH — WONDERPATH AI

* **Owner phụ trách:** Tạ Duy Xuân (Mã học viên: `2A202600970`)
* **Vai trò:** Đảm bảo hệ thống vận hành an toàn (Safety-First), nhận biết lỗi thông minh và cho phép người dùng đính chính hành vi (Human-in-the-loop).

---

## I. Môi Trường & Dữ Liệu Giả Lập (Mock Data Configuration)

Để thực hiện các kịch bản kiểm thử lỗi mà không cần đợi thời tiết xấu hay thiết bị hỏng thật, Backend và Frontend cần hỗ trợ cơ chế giả lập qua API Params hoặc Database Flags:

1. **Giả lập vị trí/GPS yếu (`gps_precision`):** Lực định vị GPS có độ lệch $> 50m$ hoặc mất tín hiệu.
2. **Giả lập dữ liệu thời tiết (`weather_status`):** Chuyển từ `sunny` (nắng) sang `storm` (mưa giông dữ dội).
3. **Giả lập trạng thái vận hành (`ride_status`):** Đặt trạng thái trò chơi cụ thể sang `maintenance` (bảo trì) hoặc `wait_time > 60` (quá tải).

---

## II. Danh Sách Kịch Bản Kiểm Thử Chi Tiết

### 1. TC-01: Định vị yếu & Thiếu thông tin phân khúc (Low-Confidence Path)
* **Mục tiêu:** Xác minh hệ thống không bị crash hoặc đưa ra gợi ý rác khi thiếu dữ liệu định vị/người dùng.
* **Các bước thực hiện:**
  1. Sử dụng thiết bị test, truy cập ứng dụng thông qua URL trạm QR 3 nhưng giả lập tham số GPS yếu (`gps_precision=low`).
  2. Không truyền thông tin Profile người dùng (khách truy cập ẩn danh mới).
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "qr_station_id": "STATION_03",
    "gps": { "latitude": 0, "longitude": 0, "accuracy": 150 },
    "user_profile": null
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot hiển thị câu hỏi làm rõ thân thiện: *"Chào bạn! Bạn vừa quét mã tại Trạm 3 nhưng định vị GPS đang không rõ ràng. Bạn đang đi cùng nhóm nào để mình gợi ý nhé?"*
  * Hiển thị 3 nút bấm phản hồi nhanh: `[Gia đình có bé nhỏ]`, `[Nhóm bạn trẻ thích mạo hiểm]`, `[Đi thong thả nghỉ dưỡng]`.
  * Sau khi người dùng click một nút bấm, Gemini API cập nhật ngay gợi ý tương ứng mà không cần tải lại trang.

---

### 2. TC-02: Gợi ý trò chơi đang bảo trì đột xuất (Failure Path)
* **Mục tiêu:** Xác minh hệ thống tự động phát hiện trò chơi được đề xuất đã đổi trạng thái và đưa ra phương án thay thế tức thời.
* **Các bước thực hiện:**
  1. Người dùng quét QR tại *Khu Cổ Tích*, hệ thống gợi ý trò chơi *"Tàu lượn siêu tốc"*.
  2. Trên Dashboard quản trị công viên (hoặc Mock API), đổi trạng thái *"Tàu lượn siêu tốc"* thành `maintenance` (bảo trì).
  3. Người dùng di chuyển tới điểm chơi và mở lại khung Chatbot.
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "ride_id": "roller_coaster_01",
    "status": "maintenance"
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Chatbot lập tức đẩy thông báo cập nhật (Toast/Message): *"Rất tiếc, trò Tàu lượn siêu tốc vừa tạm dừng bảo trì. Bạn có muốn đổi sang trò Đu quay dây văng (chờ 5 phút, cách 100m) không?"*
  * Hiển thị 2 nút bấm: `[Đồng ý cập nhật]`, `[Tìm trò mát mẻ khác]`.
  * Bản đồ di chuyển tự động cập nhật lại lộ trình sang trò chơi thay thế sau khi người dùng bấm đồng ý.

---

### 3. TC-03: Thời tiết thay đổi đột ngột sang giông bão (Dangerous Failure Mode)
* **Mục tiêu:** Xác minh tính năng quan trọng nhất về an toàn (Safety-First) khi thời tiết chuyển biến xấu đột ngột.
* **Các bước thực hiện:**
  1. Người dùng đang ở trạng thái Happy Path (đang xem sơ đồ chỉ đường ngoài trời).
  2. Giả lập API thời tiết đẩy trạng thái thiên tai giông bão (`weather_status=storm`, `rain_intensity=high`).
* **Dữ liệu đầu vào (Mock Input):**
  ```json
  {
    "weather": {
      "status": "storm",
      "temp": 24,
      "wind_speed": 45
    }
  }
  ```
* **Kết quả mong đợi (Expected Output):**
  * Giao diện Web App lập tức kích hoạt **Chế độ Khẩn cấp (Emergency Mode)**:
    * Đổi background sang màu cảnh báo đỏ/tối.
    * Ẩn ngay lập tức toàn bộ các gợi ý ngoài trời hoặc các trò cảm giác mạnh trên cao.
    * Đẩy thông báo khẩn: *"Cảnh báo: Thời tiết có giông lốc lớn. Xin vui lòng di chuyển ngay vào khu vực an toàn."*
    * Tự động hiển thị sơ đồ chỉ đường đến điểm trú mưa gần nhất (Nhà hàng Đại Dương - cách 40m) kèm nút bấm nổi bật: `[Chỉ đường trú mưa]`.

---

### 4. TC-04: Người dùng chủ động đính chính gợi ý (Correction Path)
* **Mục tiêu:** Xác minh hệ thống ghi nhận phản hồi phủ định của người dùng và cập nhật cấu trúc gợi ý trong suốt phiên sử dụng (Session).
* **Các bước thực hiện:**
  1. Chatbot gợi ý trò chơi cảm giác mạnh *"Vòng quay vũ trụ"*.
  2. Người dùng nhấn nút `[Đổi phương án khác]` hoặc nhập text: *"Trò này không phù hợp cho trẻ em dưới 1m"*.
* **Kết quả mong đợi (Expected Output):**
  * Chatbot ghi nhận phản hồi và đưa ra gợi ý thay thế nhẹ nhàng hơn (ví dụ: *Đu quay thú nhún*).
  * Profile tạm thời của Session được cập nhật tham số loại trừ: `{ "exclude_categories": ["thrill_rides", "height_under_1m"] }`.
  * Trong tất cả các lượt gợi ý sau đó của phiên chơi này, AI không được phép đề xuất bất kỳ trò chơi cảm giác mạnh nào có giới hạn chiều cao trên 1m.

---

## III. Ma Trận Đánh Giá Kết Quả (Pass/Fail Criteria)

| Mã TC | Trọng tâm kiểm thử | Tiêu chí ĐẠT (Pass) | Tiêu chí HỎNG (Fail) |
|---|---|---|---|
| **TC-01** | Low-Confidence | Chatbot hiển thị nút chọn phân khúc, không crash giao diện. | App quay tròn không phản hồi hoặc hiện mã lỗi thô từ API. |
| **TC-02** | Trò chơi bảo trì | Nhận biết trạng thái từ Mock API và hiển thị lựa chọn thay thế trong 2 giây. | Vẫn chỉ đường đến trò chơi đã bảo trì, bắt người dùng đi bộ vô ích. |
| **TC-03** | Giông bão đột ngột | Ẩn trò ngoài trời, hiện cảnh báo đỏ, chỉ đường trú mưa trong vòng 1.5 giây. | Tiếp tục gợi ý trò ngoài trời dưới trời mưa bão nguy hiểm. |
| **TC-04** | Đính chính (Correction) | Không gợi ý lại danh mục đã bị loại trừ trong suốt Session. | Trùng lặp gợi ý trò chơi bị từ chối ở các lượt quét QR tiếp theo. |
