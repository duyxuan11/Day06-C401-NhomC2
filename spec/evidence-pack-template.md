
# Evidence Pack — WonderPath AI

Nộp kèm thin SPEC cuối Day 05.

## 1. Nhóm và track

**Tên nhóm:** Group C2  
**Thành viên nhóm:**
- Nguyễn Văn Đoan — 2A202600795
- Nguyễn Huy Bảo — 2A202600997
- Lê Duy Hùng — 2A202600718
- Phạm Ngọc Vinh — 2A202600563
- Tạ Duy Xuân — 2A202600970
**Track:** Travel & Hospitality (Khu vui chơi phức hợp / Theme Parks)  
**Product/app đã chọn:** WonderPath AI — Trợ lý dẫn đường ngữ cảnh (Context-Aware Micro-Itinerary / Zero-UI)  
**Build slice đang nghĩ:** Web App/Zalo Mini App kích hoạt qua mã QR tại các điểm chạm vật lý trong công viên, tự động thu thập vị trí hiện tại và thời gian thực (Zero-Input). Giao diện mở ra là một hội thoại siêu ngắn (Conversational UI sử dụng Gemini API) chào đón và đề xuất 2-3 lựa chọn phản hồi nhanh bằng nút bấm để sinh lịch trình ngắn hạn trong 1-2 tiếng tiếp theo thay vì bắt người dùng vào trình soạn lập lịch trình phức tạp.

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Giao diện lập lịch trình trên các app du lịch bắt buộc người dùng tự thêm hoạt động, căn chỉnh giờ giấc, kéo thả sắp xếp phức tạp. Người đi chơi thường lười lục lọi và ngại nghiên cứu các công cụ lập lịch rườm rà này. | [complex_planner.png](evidence\z7896931050103_1dc80b4a6bf0b18bbedaed3a2f196236.jpg) | **Failure (Interaction Friction / Cognitive Load)** | Tránh đưa người dùng vào một trình soạn lập lịch trình. Dùng AI gợi ý lịch trình vi mô 1-2 tiếng ngay lập tức dựa trên ngữ cảnh quét QR. |
| Mô tả các trò chơi trên bản đồ và thông tin ứng dụng rất sơ sài (chỉ có tên và 1 dòng tóm tắt chung chung, không ghi rõ độ tuổi, mức độ cảm giác mạnh hay các lưu ý sức khỏe). User không đủ thông tin để quyết định đi đâu tiếp. | [z7896649965970_...jpg](evidence/z7896649965970_4ccc77d1338ba6abf52dff1e32a2f86a.jpg) | **Low-confidence** | AI Bot cần cung cấp thông tin trò chơi thông minh, tóm tắt nhanh độ phù hợp (ví dụ: có trẻ nhỏ, người già) ngay trong hội thoại ngắn để hỗ trợ ra quyết định. |
| Lịch trình cố định lập từ nhà bị vỡ hoàn toàn khi trò chơi chủ chốt (Tàu lượn siêu tốc) bảo trì đột xuất lúc 10:00. App không cập nhật lại lộ trình tự động, user phải tự mò mẫm đổi hướng hoặc đi lòng vòng. | [itinerary_broken.png](evidence\z7896929343634_04c2fb9127b5e2636fa8e4882fdab243.jpg) | **Failure / Correction** | Bản kế hoạch tĩnh cả ngày quá dễ gãy. Lịch trình cần chia nhỏ thành các block ngắn hạn (1-2 tiếng tiếp theo) và cập nhật tức thời theo ngữ cảnh thực tế của công viên. |

## 3. User / review / social evidence

Nguồn có thể là review App Store/Play, group, comment, phỏng vấn nhanh, hoặc nguồn public khác.

### 3.1. Fitted Evidences (Dành cho Trợ lý dẫn đường & Lộ trình vi mô)

Dưới đây là các bằng chứng/review khớp trực tiếp với pain points về dẫn đường, độ trễ bản đồ, thiếu thông tin mô tả trò chơi và sự kiệt sức khi xếp hàng:

| Quote / review / observation | Nguồn / File liên kết | User là ai? | Pain/failure mode |
|---|---|---|---|
| "Mấy app lập lịch trình phức tạp quá, bắt chọn điểm đi điểm đến rồi xếp giờ y như thời khóa biểu đi học. Đi chơi giải trí mà bắt đầu óc suy nghĩ nhiều thế tôi lười dùng lắm." | Đây là giả định dựa trên khảo sát sơ bộ và phản hồi thu thập trực tuyến. Nhóm sẽ kiểm chứng thực tế bằng cách phỏng vấn nhanh | Khách du lịch trẻ muốn thư thả, tự do. | **High User Friction** (Người dùng lười nghiên cứu công cụ lập lịch thủ công, muốn có gợi ý ăn ngay). |
| "Cần bổ sung thêm mô tả cho các trò chơi. Trò nào không dành cho trẻ em, người dưới 1m4... để chủ động sắp xếp thời gian di chuyển và chọn khu vui chơi phù hợp." | [z7896649965970_...jpg](evidence/z7896649965970_4ccc77d1338ba6abf52dff1e32a2f86a.jpg) (Cũng có ở [z7896686976786_...jpg](evidence/z7896686976786_bceb439ae269d47cddd5c206e8b566ab.jpg)) - *Anh Lê Nhật* | Phụ huynh đi cùng con nhỏ. | **Information Gap** (Mô tả trò chơi quá sơ sài, thiếu thông tin để đánh giá độ phù hợp của trò chơi đối với gia đình). |
| "xem map kh ổn chút nao, định vị chậm, dùng 4g cũng kh load được, nchung quá nhiu lỗi, rất tệ nka." | [z7896649978521_...jpg](evidence/z7896649978521_afcd97b25c5bcb1982e209edda89d01b.jpg) - *Nguyễn Tuyết Trinh* | Khách du lịch dùng 4G trong công viên. | **Map & Location Failure** (Bản đồ nặng nề, định vị chậm, không tối ưu cho điều kiện mạng di động thực tế). |
| "Tính năng tìm đường quá tệ hại." | [z7896649990651_...jpg](evidence/z7896649990651_d08e7728472d401ad0d82a3284dc42c0.jpg) (Cũng có ở [z7896686983919_...jpg](evidence/z7896686983919_2a75dd60ea730405ddecbe5b9426720d.jpg)) - *Lâm Nguyễn* | Khách tự túc tìm đường nội khu. | **Navigation Failure** (Chỉ đường nội khu không chính xác, gây khó khăn cho việc định hướng). |
| "chỉ đường sai tùm lum." | [z7896650003629_...jpg](evidence/z7896650003629_9a96ddeb5460d1e2857b656a4a669770.jpg) (Cũng có ở [z7896686987000_...jpg](evidence/z7896686987000_e4466e4c5abf6a418fe6d3ab74d8af6a.jpg)) - *Nguyên Minh Võ* | Du khách cố gắng di chuyển giữa các phân khu. | **Navigation Failure** (Định vị xoay lệch, chỉ sai hướng đi thực tế). |
| "Sử dụng khó khăn. Tải lượng lớn. Đường đi hoàn toàn khác địa hình. Nhìn bản đồ leo rào không... Trải nghiệm tồi tệ." | [z7896686979669_...jpg](evidence/z7896686979669_4adc36ca7abbb5f0104466db52230035.jpg) - *phuc hung Nguyen* | Du khách đi bộ tìm lối đi thực tế. | **Physical-Digital Disconnect** (Bản đồ thiết kế không khớp với vận hành địa hình thực tế, chỉ đường phi lý). |
| "khách đông nhưng sảnh chờ nóng như lò, không một quạt mát, không điều hòa, ai cũng toát hết mồ hôi." | [z7896686987000_...jpg](evidence/z7896686987000_e4466e4c5abf6a418fe6d3ab74d8af6a.jpg) - *Thanh An Nguyen* | Khách xếp hàng tại trò chơi đông đúc. | **Physical Fatigue & Queue Pain** (Kiệt sức vì chờ đợi lâu trong điều kiện nóng bức. Cần gợi ý tránh nóng/nghỉ ngơi động lập tức). |
| "nhập đúng mật khẩu nhưng không cách nào vào được tài khoản, vào web thì lại được... Đầu tư, chỉn chu cho app khó tới vậy?" | [z7896686989709_...jpg](evidence/z7896686989709_d3078a57cf3ade5e70071b75c0ff916c.jpg) (Cũng có ở [z7896649965970_...jpg](evidence/z7896649965970_4ccc77d1338ba6abf52dff1e32a2f86a.jpg) - *nguyendang dao*) - *An Huỳnh* | Khách muốn sử dụng app tại công viên. | **App Onboarding Failure** (Hệ thống đăng nhập/đăng ký của App nặng gặp lỗi liên tục. Củng cố lý do dùng Web App/QR Code không cần tài khoản). |
| "toàn trò chán, đợi lâu, ko nên đi." | [z7896686995420_...jpg](evidence/z7896686995420_7445fedef5dea9494936adcfe69a2f6d.jpg) (Cũng có ở [z7896650003629_...jpg](evidence/z7896650003629_9a96ddeb5460d1e2857b656a4a669770.jpg)) - *Tống Mạnh* | Du khách thất vọng vì thời gian chờ dài. | **Queue Pain** (Không tối ưu được thời gian xếp hàng, dẫn đến cảm giác đi chơi tẻ nhạt, tốn thời gian chờ đợi). |

### 3.2. Unfitted Evidences (Bằng chứng không phù hợp / Placeholder)

Dưới đây là các bằng chứng thu thập được từ tệp hình ảnh nhưng không thuộc phạm vi xử lý trực tiếp của sản phẩm Trợ lý dẫn đường & Lộ trình vi mô (được đặt làm placeholder/backlog hoặc bỏ qua):

| Quote / review / observation | Nguồn / File liên kết | User là ai? | Lý do không khớp (Unfitted) |
|---|---|---|---|
| "mua vé luôn hiện lỗi, gọi cho tổng đài thì bị tắt máy ngang." | [z7896686995420_...jpg](evidence/z7896686995420_7445fedef5dea9494936adcfe69a2f6d.jpg) - *phúc nguyễn* | Khách mua vé trực tuyến. | **Lỗi hệ thống giao dịch/thanh toán vé**: Không liên quan đến tính năng dẫn đường hoặc tối ưu lộ trình vi mô trong khu vui chơi. |
| "mua vé mà đi xe bus không được, dẹp luôn đi." | [z7896686995420_...jpg](evidence/z7896686995420_7445fedef5dea9494936adcfe69a2f6d.jpg) - *Vũ Cường* | Khách sử dụng dịch vụ trung chuyển. | **Lỗi dịch vụ logistics/xe bus ngoại khu**: Nằm ngoài phạm vi điều phối và chỉ dẫn nội khu vui chơi giải trí. |
| "app buộc cập nhật nhưng không có bản cập nhật nào, nên không xài đc gỡ bỏ rồi cài lại cũng vậy..." | [z7896686987000_...jpg](evidence/z7896686987000_e4466e4c5abf6a418fe6d3ab74d8af6a.jpg) - *Vo DUY HUNG* | Khách hàng tải app qua Store. | **Lỗi kỹ thuật phân phối của Store**: Dự án sử dụng giải pháp Web App chạy trực tiếp trên trình duyệt hoặc Zalo Mini App thông qua quét QR vật lý, hoàn toàn miễn nhiễm với lỗi quản lý phiên bản ứng dụng native này. |

Nếu chưa có nguồn ngoài nhóm, ghi rõ:

```text
Đây là giả định dựa trên khảo sát sơ bộ và phản hồi thu thập trực tuyến. Nhóm sẽ kiểm chứng thực tế bằng cách phỏng vấn nhanh 5-7 du khách trực tiếp tại khuôn viên khu vui chơi về hành vi sử dụng ứng dụng bản đồ trước checkpoint M1 Day 06.
```

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| **Disney Genie+ (My Disney Experience App)** | Cho phép chọn sở thích cá nhân, sau đó tự động gợi ý trò chơi tiếp theo dựa trên thời gian chờ xếp hàng thực tế (Wait Times) và vị trí của khách hàng. | **Dynamic Routing & Queue Optimization:** Định tuyến động dựa trên dữ liệu hàng đợi thời gian thực. | Cắt giảm scope: Disney Genie+ rất nặng và phức tạp. Nhóm sẽ học pattern gợi ý động dựa trên Wait Times nhưng triển khai dưới dạng gợi ý siêu ngắn thông qua hội thoại (Conversational UI) quét QR. |
| **Zalo Mini App / WeChat Mini Program (Analog)** | Cho phép người dùng quét mã QR tại các nhà hàng để tự động nhận biết số bàn, hiển thị menu gọi món và thanh toán ngay mà không cần tải ứng dụng hay đăng nhập. | **Physical Touchpoint Integration (Kết nối điểm chạm vật lý) & Zero-Install.** | Có. Đặt mã QR tại các bảng chỉ đường của từng khu vực. Khách quét mã để tự động truyền ID vị trí và thời gian thực vào chatbot, kích hoạt câu chào AI thông minh thay vì điền biểu mẫu. |

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
Du khách cực kỳ lười và ngại nghiên cứu các công cụ lập lịch trình phức tạp hoặc tự tìm hiểu mô tả trò chơi sơ sài khi đi chơi. Đồng thời, mọi lịch trình lên sẵn (static plan) từ trước đều dễ dàng bị phá vỡ bởi các biến số thực tế: thời tiết thay đổi đột ngột, trò chơi bảo trì, hoặc hàng đợi quá dài khiến họ mệt mỏi.

Insight:
User không chỉ cần một công cụ chứa thông tin (surface need).
Thật ra họ cần một trợ lý hỗ trợ ra quyết định tức thời, cực kỳ tối giản (Zero-UI/Zero-Input) để có ngay gợi ý lịch trình ngắn hạn (1-2 tiếng) tối ưu phù hợp với vị trí và nhóm đi cùng, thay vì phải tự nghiên cứu và vào trình soạn lập lịch trình phức tạp.

Opportunity:
AI có thể giúp bằng cách kết hợp mã QR vật lý để lấy vị trí/thời gian tự động (Zero-Input), sử dụng Gemini API để tạo cuộc trò chuyện siêu ngắn (Conversational UI) cung cấp nhanh thông tin trò chơi và gợi ý lịch trình ngắn hạn (1-2 tiếng) thông qua các nút bấm phản hồi nhanh.
```

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính.
- [ ] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [ ] Đổi failure mode.
- [ ] Đổi owner/test plan.

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm định xây dựng một ứng dụng di động (Native App) đầy đủ tính năng giúp du khách lên lịch trình vui chơi chi tiết từ sáng đến tối trước khi đi, yêu cầu điền khảo sát sở thích cá nhân sâu để thiết kế lộ trình cố định cho cả ngày.

Sau evidence, nhóm đổi thành xây dựng một Web App/Zalo Mini App siêu nhẹ (Zero-Install). Khi quét mã QR tại các trạm vật lý hoặc định vị tại chỗ, hệ thống tự động nắm giữ vị trí & thời gian hiện tại, AI (Gemini API) lập tiếp đón bằng một cuộc hội thoại siêu ngắn chào đón và đưa ra các gợi ý lịch trình ngắn hạn trong 1-2 tiếng tiếp theo dưới dạng các nút bấm phản hồi nhanh (Zero-Input) thay vì bắt người dùng vào trình soạn lập lịch trình phức tạp.

Lý do: Khách hàng đi chơi muốn thư giãn tuyệt đối, cực kỳ lười tự nghiên cứu công cụ lập lịch hay tự đọc các mô tả trò chơi sơ sài. Việc gợi ý ngay lịch trình 1-2 tiếng thông qua hội thoại quét QR giúp tối thiểu hóa ma sát tương tác, phản ứng linh hoạt trước biến động vận hành thực tế của công viên.
```

