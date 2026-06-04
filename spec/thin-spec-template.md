
# Template — Thin SPEC Cuối Day 05 (WonderPath AI)

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

## 1. Track, product/app và user

* **Track:** Travel & Hospitality (Khu vui chơi phức hợp / Theme Parks)
* **Product/app thật:** WonderPath AI — Trợ lý dẫn đường ngữ cảnh (Context-Aware Micro-Itinerary / Zero-UI)
* **User cụ thể:** Du khách tham quan công viên phức hợp (ví dụ: VinWonders, Sun World), đi cùng gia đình (có trẻ em, người già) hoặc nhóm bạn trẻ, ngại sử dụng các ứng dụng lập kế hoạch dài dòng từ trước và muốn có các gợi ý giải quyết nhu cầu di chuyển/vui chơi tức thời trong 1-2 tiếng tiếp theo mà không cần tải app (Zero-Install).
* **Nhóm có phải user thật không? Nếu không, khác ở đâu?:** Có, các thành viên trong nhóm đều từng đi du lịch tự túc tại các khu vui chơi phức hợp và từng gặp các điểm gãy về định vị, xếp hàng chờ quá lâu, hoặc kế hoạch bị vỡ do mưa bão/bảo trì. Điểm khác biệt duy nhất là nhóm có nền tảng công nghệ nên dễ định hình giải pháp AI hơn.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Giao diện lập lịch trình trên các app du lịch bắt buộc người dùng tự thêm hoạt động, sắp xếp giờ giấc phức tạp. | Trải nghiệm thực tế (Self-use) | User lười tự tay sắp xếp lộ trình tĩnh từ trước, muốn có giải pháp đề xuất nhanh khi đang ở khuôn viên công viên. | Loại bỏ giao diện lập lịch trình phức tạp. Dùng AI gợi ý lịch trình vi mô 1-2 tiếng tiếp theo thông qua hội thoại siêu ngắn quét QR. |
| Bản đồ và thông tin ứng dụng thực tế mô tả trò chơi rất sơ sài (chỉ có tên và 1 dòng tóm tắt chung chung, không ghi rõ mức độ cảm giác mạnh). | Trải nghiệm thực tế (Self-use) & Phỏng vấn du khách | Phụ huynh hoặc nhóm bạn trẻ thiếu thông tin tin cậy để quyết định có xếp hàng chơi hay không (rủi ro an toàn hoặc phí thời gian). | AI Bot phải tóm tắt thông tin trò chơi thông minh, đánh giá độ phù hợp (nhóm có trẻ nhỏ, người già) ngay trong chatbox hỗ trợ ra quyết định nhanh. |
| Lịch trình cố định lập từ nhà bị vỡ hoàn toàn khi trò chơi bảo trì đột xuất hoặc thời tiết thay đổi bất ngờ (như mưa giông show nhạc nước bị hủy). | Group Facebook du lịch & Trải nghiệm thực tế | Lịch trình tĩnh cả ngày cực kỳ mong manh. Trải nghiệm vui chơi cần được cập nhật linh hoạt theo thời gian thực (real-time). | Chuyển sang lịch trình vi mô (micro-itinerary) cập nhật động dựa trên dữ liệu vận hành thời gian thực (Wait Times, thời tiết, trạng thái bảo trì). |
| Khách đứng ở ngã tư ngơ ngác không biết đi hướng nào tiếp, mở GPS thì app xoay mòng mòng chỉ sai hướng. | Phỏng vấn tại công viên | Định vị và bản đồ số truyền thống thiếu sự kết hợp ngữ cảnh vật lý và hành vi thực tế của khách hàng tại chỗ. | Sử dụng mã QR vật lý gắn tại các trạm để xác định tức thời vị trí hiện tại (Zero-Input) và đưa ra câu chào thông minh theo ngữ cảnh vị trí. |

## 3. Pain statement

```text
User là khách tham quan công viên phức hợp (đặc biệt là phụ huynh đi cùng con nhỏ hoặc nhóm bạn trẻ) đang gặp khó ở bước lựa chọn điểm vui chơi tiếp theo và lập lịch trình linh hoạt khi ở trong khuôn viên công viên,
vì các ứng dụng hiện tại bắt buộc phải lập lịch trình tĩnh phức tạp từ trước, mô tả trò chơi sơ sài và không cập nhật động trước các biến số (thời tiết, bảo trì, xếp hàng dài),
dẫn tới user mệt mỏi, tốn thời gian di chuyển lòng vòng, xếp hàng vô ích hoặc bỏ lỡ các show diễn ưa thích.
Bằng chứng chính là các review phàn nàn trên Google Play/App Store về việc "lên lịch xem Show nhạc nước nhưng trời mưa hủy show mà app vẫn chỉ đường ra hồ" và việc du khách "xoay mòng mòng mở app chỉ sai hướng dưới trời nắng gắt".
```

## 4. Build slice

```text
Cho du khách tại công viên phức hợp đang muốn tìm địa điểm vui chơi tiếp theo trong 1-2 tiếng tới,
prototype sẽ dùng AI (Gemini API) để phân tích ngữ cảnh (vị trí quét QR, thời gian hiện tại, thời tiết, tình trạng hàng đợi thực tế) và tạo ra một lịch trình vi mô ngắn gọn (Micro-Itinerary),
tạo ra cuộc trò chuyện siêu ngắn (Conversational UI) chào đón và đề xuất 2-3 lựa chọn phản hồi nhanh bằng nút bấm để sinh lịch trình ngắn hạn trong 1-2 tiếng tiếp theo,
và xử lý failure mode (AI gợi ý trò chơi đang bảo trì/hàng đợi quá tải hoặc trời mưa trò chơi ngoài trời dừng hoạt động) bằng việc tự động truy xuất API trạng thái công viên thời gian thực để cập nhật phương án thay thế ngay trong chatbox và hiển thị nút [Đổi phương án khác].
```

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:** Du lịch vui chơi giải trí là trải nghiệm mang tính tận hưởng cá nhân cao. Việc tự động hóa hoàn toàn lịch trình (AI tự quyết) sẽ ép buộc người dùng và không tạo cảm giác tự do. AI đóng vai trò làm trợ lý gợi ý (Augmentation) giúp người dùng giảm thiểu gánh nặng phân tích thông tin nhưng vẫn giữ quyền quyết định tối cao qua các nút bấm tương tác đơn giản.  
**Human role:** reviewer / decider / trainer / rescuer / none
- **decider**: Người dùng bấm chọn các option lịch trình do AI gợi ý.
- **rescuer**: Bấm nút `[Đổi phương án khác]` khi không thích hoặc khi thực tế tại chỗ không khớp.

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| **Happy** | User quét mã QR tại trạm vật lý (Cổng Khu Cổ Tích lúc 10:00 sáng). Trợ lý WonderPath lập tức mở cuộc trò chuyện: *"Chào bạn! Bạn đang ở Khu Cổ Tích. Thời tiết lúc này nắng ấm (31°C). Moni gợi ý lịch trình 1-2 tiếng tới cho bạn: 1. Xem Show Rồng lửa lúc 10:15 (cách 50m) hoặc 2. Chơi Lâu đài huyền bí (chờ 10 phút)."* User bấm chọn option 1 -> Hiển thị sơ đồ chỉ đường ngắn và đếm ngược giờ show diễn. |
| **Low-confidence** | Hệ thống không định vị chính xác vị trí hoặc mất kết nối thời tiết hiện tại. WonderPath sẽ hỏi lại nhanh bằng nút bấm: *"Chào bạn! Bạn vừa quét mã tại Trạm 3 nhưng định vị GPS đang không rõ ràng. Bạn đang đi cùng nhóm nào để mình gợi ý nhé?"* kèm các nút chọn nhanh: `[Gia đình có bé nhỏ]`, `[Nhóm bạn trẻ thích mạo hiểm]`, `[Đi thong thả nghỉ dưỡng]`. |
| **Failure** | AI gợi ý trò chơi "Tàu lượn siêu tốc" nhưng trò này vừa vào trạng thái bảo trì đột xuất cách đây 2 phút hoặc hàng đợi đột ngột tăng lên 60 phút. Khi user đi đến nơi thấy biển báo bảo trì, user mở chatbox thấy thông báo cập nhật: *"Rất tiếc, trò Tàu lượn vừa tạm dừng bảo trì. Bạn có muốn đổi sang trò Đu quay dây văng (chờ 5 phút, cách 100m) không?"* kèm nút `[Đồng ý cập nhật]` và `[Tìm trò mát mẻ khác]`. |
| **Correction** | Khi user bấm nút `[Tìm trò mát mẻ khác]` hoặc phản hồi *"Trò này không phù hợp cho trẻ em dưới 1m"*, WonderPath lập tức thay đổi gợi ý, ghi nhận phản hồi vào profile tạm thời của phiên chơi hiện tại để không gợi ý các trò cảm giác mạnh cho nhóm này trong ngày hôm đó nữa. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user quét QR định vị tại một điểm ngoài trời lúc thời tiết thay đổi đột ngột (trời đổ mưa to giông lốc),
AI có thể tiếp tục gợi ý các trò chơi ngoài trời hoặc show diễn đã bị hủy do thời tiết xấu,
hậu quả là du khách bị ướt, mệt mỏi, hoặc nguy hiểm hơn là di chuyển vào khu vực trơn trượt/không an toàn.
Prototype sẽ xử lý bằng việc tích hợp API thời tiết thời gian thực và trạng thái hoạt động của công viên. Khi phát hiện chỉ số thời tiết xấu (mưa/sét), AI sẽ lập tức chuyển sang chế độ khẩn cấp: tự động ẩn toàn bộ gợi ý ngoài trời, hiển thị cảnh báo đỏ và đưa ra lộ trình di chuyển nhanh đến các khu vực trú mưa trong nhà gần nhất kèm nút bấm [Chỉ đường trú mưa].
Owner kiểm thử path này là Tạ Duy Xuân.
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách (Day 06) | Bằng chứng cần có trong repo |
|---|---|---|
| **Nguyễn Huy Bảo** - 2A202600997 | **Đầu việc 1**: Thiết kế Kịch bản & Dữ liệu giả lập | Dữ liệu giả lập các trò chơi, vị trí trạm QR, và trạng thái xếp hàng/thời tiết trong repo. |
| **Nguyễn Văn Đoan** - 2A202600795 | **Đầu việc 2**: Lập trình Giao diện di động | Code Frontend Web/Zalo Mini App hiển thị Chatbot và Toast thông báo có nút [Undo]. |
| **Lê Duy Hùng** - 2A202600718 | **Đầu việc 3**: Thiết lập Prompt & AI Logic | System Prompt cho Gemini và định nghĩa cấu trúc JSON đầu vào/đầu ra trong SPEC. |
| **Phạm Ngọc Vinh** - 2A202600563 | **Đầu việc 4**: Xây dựng Backend & Kết nối API | API Server kết nối Gemini API và Mock API trạng thái công viên. |
| **Tạ Duy Xuân** - 2A202600970 | **Đầu việc 5**: Kiểm thử kịch bản lỗi & Chuẩn bị Demo | Video demo 3 phút + Script thuyết trình + Slide nhóm + Kịch bản kiểm thử Failure Path. |
