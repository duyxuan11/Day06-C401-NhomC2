# KỊCH BẢN THUYẾT TRÌNH DEMO WONDERPATH AI (THỜI LƯỢNG: 3 PHÚT)

* **Người trình bày:** Tạ Duy Xuân (hoặc đại diện nhóm)
* **Vai trò:** Thuyết minh kịch bản tương tác trực quan & chứng minh năng lực phục hồi lỗi/ứng phó khẩn cấp của AI.
* **Thiết bị hỗ trợ:** Điện thoại hiển thị giao diện Web App/Zalo Mini App quét mã QR, màn hình lớn chiếu slide/hội thoại AI thời gian thực.

---

### PHẦN 1: MỞ ĐẦU & NÊU VẤN ĐỀ (0:00 - 0:30)

| Thời gian | Nội dung thuyết trình | Hành động / Slide hiển thị |
| :--- | :--- | :--- |
| **0:00 - 0:15** | Kính chào các thầy cô ban giám khảo và các bạn học viên! Đi chơi ở các công viên lớn như VinWonders, ai cũng muốn thư giãn tuyệt đối. Nhưng thực tế du khách lại rất vất vả: phải tải app nặng 100MB, đăng nhập lỗi liên tục, rồi cắm đầu vào kéo thả một lịch trình tĩnh phức tạp như thời khóa biểu đi học. | **[SLIDE 1]** Slide tiêu đề: **WonderPath AI — Trợ lý dẫn đường ngữ cảnh (Zero-UI / Zero-Install)**.<br>Hình ảnh minh họa app du lịch phức tạp và review phàn nàn của du khách. |
| **0:15 - 0:30** | Lịch trình cứng lập từ nhà rất dễ bị vỡ vụn khi trời đổ mưa dông hoặc trò chơi bảo trì. Từ điểm gãy đó, nhóm C2 mang đến **WonderPath AI** – Giải pháp quét QR vật lý tại chỗ, cung cấp ngay lịch trình vi mô 1-2 tiếng tiếp theo. Không cần cài đặt, không cần đăng ký tài khoản, tất cả phản hồi động theo ngữ cảnh thời gian thực. | **[SLIDE 2]** Tóm tắt Nỗi đau (Pain points) & Giải pháp cốt lõi: *"Quét QR tại chỗ - Có ngay lịch trình vi mô 1-2 tiếng".* |

---

### PHẦN 2: HAPPY PATH & LOW-CONFIDENCE (0:30 - 1:20)

| Thời gian | Nội dung thuyết trình | Hành động / Slide hiển thị |
| :--- | :--- | :--- |
| **0:30 - 0:55** | **[Happy Path]** Tôi đang đứng tại Cổng Khu Cổ Tích lúc 10h sáng dưới thời tiết nắng ấm 31°C, đi cùng gia đình có bé nhỏ. Tôi quét mã QR trên bảng chỉ đường. Lập tức, WonderPath chào mừng và đề xuất ngay: Xem Show Rồng lửa lúc 10:15 hoặc chơi Lâu đài huyền bí phù hợp chiều cao của bé. Tôi nhấn chọn xem Show Rồng Lửa, hệ thống lập tức hiển thị bản đồ định hướng nhanh gọn và đếm ngược giờ show diễn. | **[Hành động Demo]** Trình chiếu màn hình điện thoại thật: Quét QR tại trạm **qr_station_01**.<br>Màn hình hiện chatbox chào mừng và hiển thị các nút: `[Xem Show Rồng Lửa (10:15)]`, `[Chơi Lâu Đài Huyền Bí]`. Click chọn Show Rồng Lửa. |
| **0:55 - 1:20** | **[Low-Confidence]** Nhưng nếu hệ thống chưa biết tôi đi cùng ai (Profile trống)? WonderPath không đứng im hay báo lỗi. Thay vào đó, AI chào đón và hiện 3 nút bấm phân loại nhanh nhóm đi cùng. Chỉ cần một cú chạm vào `[Nhóm bạn trẻ thích cảm giác mạnh 🎢]`, Gemini API lập tức cập nhật lại profile tạm thời của phiên quét và hiển thị các đề xuất trò chơi cảm giác mạnh phù hợp với chúng tôi. | **[Hành động Demo]** Giả lập quét QR không có profile (`user_profile` bằng null).<br>Màn hình hiển thị câu hỏi và 3 nút cập nhật profile nhanh: Nhóm có bé nhỏ, Nhóm bạn trẻ, Gia đình thong thả. Nhấp chọn "Nhóm bạn trẻ". |

---

### PHẦN 3: FAILURE MODE – BẢO TRÌ & QUÁ TẢI & THỜI TIẾT (1:20 - 2:30)

| Thời gian | Nội dung thuyết trình | Hành động / Slide hiển thị |
| :--- | :--- | :--- |
| **1:20 - 1:45** | **[Bảo trì & Quá tải]** Đây là điểm đắt giá nhất của WonderPath: tự động phục hồi lỗi. Khi nhóm bạn trẻ quét QR tại trạm 2 muốn chơi Tàu lượn siêu tốc, nhưng trò này đột ngột bảo trì. AI nhận diện trạng thái bảo trì trong `realtime_status`, lập tức ẩn Tàu Lượn và chủ động đề xuất Đu quay dây văng thay thế cùng quầy ăn nhanh Express gần đó, kèm nút `[Đổi phương án khác]` để du khách luôn giữ quyền chủ động. | **[Hành động Demo]** Giả lập quét QR tại **qr_station_02** với status_override: `att_roller_coaster` bảo trì.<br>Chatbot hiển thị thông báo lỗi bảo trì, gợi ý Đu quay dây văng và nút `[Đổi phương án khác]`. |
| **1:45 - 2:05** | Tương tự, nếu Đường Trượt Nước Lốc Xoáy đang quá tải với hàng đợi lên tới 50 phút, AI cũng tự động lọc bỏ và hướng nhóm bạn trẻ ghé Khu Ẩm Thực Express uống nước giải nhiệt để chờ đám đông hạ nhiệt, tránh việc du khách phải đứng xếp hàng mệt mỏi dưới nắng nóng 35°C. | **[Hành động Demo]** Giả lập quét QR tại **qr_station_04** với status_override: `att_water_slide` hàng đợi 50 phút.<br>Màn hình hiển thị lời khuyên tránh nóng và nút dẫn đến Khu Ẩm Thực Express. |
| **2:05 - 2:30** | **[Cảnh báo khẩn cấp]** Kịch bản lỗi nguy hiểm nhất là khi trời bất ngờ đổ dông bão cực đoan. AI lập tức chuyển sang **Chế độ Khẩn cấp (Emergency Mode)**. Bản đồ đổi sang màu cảnh báo đỏ, ẩn toàn bộ trò chơi ngoài trời và ưu tiên hiển thị nút **[🚨 Chỉ đường trú mưa KidZone]** và **[Chỉ đường tới Chòi Nghỉ Ven Hồ]** để dẫn gia đình vào vùng an toàn trong vòng dưới 1.5 giây. | **[Hành động Demo]** Giả lập thời tiết chuyển dông bão (`warning_level: red`).<br>Giao diện đổi màu đỏ cảnh báo khẩn cấp, hiển thị các nút định vị trú ẩn an toàn nhất. |

---

### PHẦN 4: KẾT LUẬN & BÀI HỌC (2:30 - 3:00)

| Thời gian | Nội dung thuyết trình | Hành động / Slide hiển thị |
| :--- | :--- | :--- |
| **2:30 - 3:00** | **WonderPath AI** định nghĩa lại cách du khách tương tác với công viên giải trí: Không chuẩn bị trước phức tạp, mọi thứ phản hồi động và an toàn theo thời gian thực.<br><br>Chúng tôi đã triển khai thành công 6 kịch bản kiểm thử tự động đạt độ chính xác 100% trên mô hình Gemini 1.5 Flash. Xin cảm ơn thầy cô đã lắng nghe và rất mong nhận được câu hỏi từ mọi người! | **[SLIDE 3]** Tổng kết giá trị cốt lõi:<br>- **Zero-Install / Zero-UI**<br>- **Dynamic Micro-Itinerary**<br>- **Safety-First (Emergency Mode)**<br>- **Độ chính xác 100% (6/6 kịch bản kiểm thử)**. |

---

### 💡 Gợi ý của nhóm khi thuyết trình trước Hội đồng:
1. **Quét QR trực quan:** Cầm một tấm bìa cứng in mã QR mẫu của nhóm đưa lên camera điện thoại để thực hiện quét live trực tiếp trên sân khấu.
2. **Nhấn mạnh vai trò Augmentation:** Nhấn mạnh AI đóng vai trò gợi ý, hỗ trợ ra quyết định (du khách bấm nút chạm để chọn), chứ không tự ý quyết định thay du khách để bảo đảm tính tự do trải nghiệm.
