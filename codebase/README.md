# WonderPath AI — Prototype Frontend (Day 06)

Thư mục này chứa mã nguồn giao diện (Frontend) của prototype **WonderPath AI** - trợ lý dẫn đường ngữ cảnh tại công viên phức hợp giải trí.

---

## 1. Thành phần giao diện
*   **Bảng giả lập ngữ cảnh (Simulator Control Panel):** Nằm ở phía bên trái, cho phép lựa chọn và thay đổi các tham số thực tế:
    *   **Trạm quét QR:** Vị trí du khách quét mã QR (Trạm 1 - Cổng Cổ Tích, Trạm 2 - Ngã Tư Phiêu Lưu, v.v.).
    *   **Thời gian quét:** Giả lập các mốc thời gian khác nhau (10:00 sáng, 19:00 tối, v.v.) để thay đổi đề xuất lộ trình dựa trên lịch sự kiện (ví dụ: Show Rồng Lửa, Show Nhạc Nước).
    *   **Nhóm du khách (User Profile):** Gia đình có trẻ nhỏ, Nhóm bạn trẻ thích cảm giác mạnh, Khách đi thong thả nghỉ dưỡng, hoặc Chưa xác định (yêu cầu phân loại).
    *   **Thời tiết:** Nắng ấm, Mưa rào, Dông bão (Cảnh báo Đỏ khẩn cấp), Nắng nóng cực đoan.
    *   **Trạng thái vận hành:** Trò chơi bảo trì (Tàu lượn siêu tốc bảo trì) hoặc Đu quay dây văng quá tải.
*   **Khung hiển thị thiết bị di động (Mobile Mockup Frame):** Nằm ở phía bên phải, hiển thị giao diện giống như một ứng dụng di động thực tế (Zalo Mini App / Web App) nhận thông tin phản hồi từ WonderPath AI.
*   **Chức năng Hoàn tác (Undo):** Nút Toast hiển thị sau mỗi thao tác có nút "Hoàn tác" để quay lại trạng thái trước đó.

---

## 2. Hướng dẫn chạy giao diện

Vì toàn bộ logic xử lý ngữ cảnh, giao diện và các kịch bản kiểm thử đã được tích hợp chạy trực tiếp ở phía client-side (Client-side Simulation), bạn **không cần cài đặt bất kỳ thư viện nào** và **không cần chạy backend server**.

Có 2 cách để chạy giao diện cực kỳ đơn giản:

### Cách 1: Mở trực tiếp file HTML (Khuyên dùng nếu chạy nhanh)
1. Mở thư mục `codebase/frontend/` trên máy tính của bạn.
2. Click đúp chuột vào file `index.html` (hoặc click chuột phải chọn **Open with** -> chọn trình duyệt **Google Chrome**, **Microsoft Edge** hoặc **Firefox**).
3. Giao diện bảng điều khiển giả lập và màn hình di động sẽ hiển thị ngay lập tức.

### Cách 2: Sử dụng extension "Live Server" trên VS Code (Khuyên dùng khi lập trình)
1. Mở thư mục dự án trong VS Code.
2. Cài đặt extension **Live Server** (nếu chưa có).
3. Click chuột phải vào file `codebase/frontend/index.html` và chọn **Open with Live Server**.
4. Trình duyệt sẽ tự động mở trang web tại địa chỉ `http://127.0.0.1:5500/codebase/frontend/index.html` và tự động tải lại trang khi bạn chỉnh sửa code.

---

## 3. Các kịch bản giả lập có thể kiểm thử trực tiếp trên giao diện

Bạn có thể thay đổi các giá trị ở bảng điều khiển bên trái rồi nhấn nút **"Kích hoạt quét mã QR"** để thấy giao diện di động cập nhật tương ứng:

1.  **Kịch bản 1 (Happy Path - Gia đình có bé quét QR):**
    *   *Cấu hình:* Trạm 1 - Cổng Cổ Tích, Nhóm du khách: Gia đình có trẻ nhỏ, Thời tiết: Nắng ấm, Không tích chọn bảo trì.
    *   *Kết quả hiển thị:* Giao diện gợi ý xem Show Rồng Lửa lúc 10:15 (cách 350m) hoặc chơi Lâu Đài Huyền Bí (chờ 15 phút, trò chơi trong nhà mát mẻ cho bé).
2.  **Kịch bản 2 (Low-confidence Path - Quét QR thiếu thông tin loại nhóm):**
    *   *Cấu hình:* Nhóm du khách: Chưa xác định.
    *   *Kết quả hiển thị:* Giao diện di động đưa ra câu hỏi khảo sát nhanh với 3 nút lựa chọn loại nhóm đi cùng để cập nhật profile. Khi click chọn nút, hệ thống sẽ tự động cập nhật profile và tải lại lộ trình phù hợp.
3.  **Kịch bản 3 (Failure Path - Trò chơi chính bảo trì):**
    *   *Cấu hình:* Trạm 2 - Ngã Tư Phiêu Lưu, Nhóm du khách: Nhóm bạn trẻ thích cảm giác mạnh, Tích chọn **"Tàu Lượn Siêu Tốc bảo trì"**.
    *   *Kết quả hiển thị:* Gợi ý chuyển hướng sang chơi Đu Quay Dây Văng (chờ 10 phút) hoặc ăn nhẹ tại Khu Ẩm Thực Nhanh Express cách 150m.
4.  **Kịch bản 4 (Emergency Path - Thời tiết dông bão khẩn cấp):**
    *   *Cấu hình:* Thời tiết: Dông bão dông sét (stormy).
    *   *Kết quả hiển thị:* Hệ thống hiển thị Cảnh báo Đỏ nguy hiểm khẩn cấp, hướng dẫn di chuyển ngay vào khu vực trú ẩn trong nhà gần nhất (KidZone trong nhà hoặc Chòi nghỉ ven hồ).
