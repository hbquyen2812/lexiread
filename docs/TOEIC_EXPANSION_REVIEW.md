# TOEIC trong ứng dụng — mở rộng ngày 26/10/2026

Đã bổ sung **12 bộ luyện gốc, 168 câu hỏi, 36 văn bản và 72 mục từ**. Toàn bộ nội dung nằm trong `data/toeic/`, có thể làm và chấm ngay bằng luồng TOEIC hiện có; đây không phải danh mục liên kết ngoài. Cộng với hai bộ cũ, thư viện đóng gói có **14 bộ, 192 câu và 88 mục từ**. Các bộ nhập từ gói biên tập riêng không được cộng vào số đóng gói này.

Đây là bài luyện kỹ năng do LexiRead tự biên soạn, **không phải đề ETS chính thức, đề thi thử đầy đủ hoặc căn cứ quy đổi điểm TOEIC**. Tình huống, doanh nghiệp và trao đổi được viết cho bài tập. Mức B1–B2 và thời lượng gợi ý chưa được hiệu chuẩn với nhóm người học.

Định dạng được đối chiếu với [trang TOEIC của ETS](https://www.ets.org/content/ets-org/ca/en/toeic/test-takers/about/listening-reading.html) và [mô tả Part 5–7 của IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html). Chỉ tham khảo loại nhiệm vụ; không chép câu hỏi, văn bản hoặc đáp án của các đơn vị này.

## Danh mục và độ bao phủ

| Bộ | Part | Câu | Văn bản | Nội dung chính |
| --- | --- | ---: | ---: | --- |
| `p5-people-and-workplace-word-forms` | 5 | 20 | 0 | Từ loại, đại từ, so sánh, lượng từ; tuyển dụng và phối hợp nhân sự |
| `p5-operations-and-verb-patterns` | 5 | 20 | 0 | Thì, bị động, V-ing/to-infinitive, hòa hợp, quan hệ; vận hành và bảo trì |
| `p5-business-connections-and-collocations` | 5 | 20 | 0 | Điều kiện, nhượng bộ, giới từ, kết hợp từ; giao dịch và tài chính |
| `p6-office-changes-and-staff-updates` | 6 | 16 | 4 | Chuyển văn phòng, cập nhật hệ thống, hoàn chi phí xe đạp, đặt phòng lưu trữ |
| `p6-customers-orders-and-service` | 6 | 16 | 4 | Đổi hàng lỗi, sửa máy, nhận đơn tại cửa hàng, thay lịch giao hàng |
| `p6-events-projects-and-community` | 6 | 16 | 4 | Hội chợ, khảo sát dịch vụ thử nghiệm, vườn cộng đồng, đào tạo trực tuyến |
| `p7-single-workspaces-and-repair-services` | 7 | 10 | 2 | Quy định không gian làm việc chung, sự kiện sửa đồ |
| `p7-single-recruitment-and-transport` | 7 | 10 | 2 | Tuyển điều phối viên bảo tàng, đánh giá tuyến xe đưa đón |
| `p7-double-travel-and-purchasing` | 7 | 10 | 4 | Lịch tàu và thư đổi chuyến; báo giá và yêu cầu mua máy in |
| `p7-double-events-and-expense-policies` | 7 | 10 | 4 | Phân ca và thư tình nguyện; quy định chi phí và hồ sơ cụ thể |
| `p7-triple-event-catering-and-accommodation` | 7 | 10 | 6 | Yêu cầu sự kiện/báo giá/xác nhận; giá phòng/đặt phòng/thay đổi |
| `p7-triple-returns-and-building-work` | 7 | 10 | 6 | Chính sách/hóa đơn/hàng lỗi; thông báo/lịch họp/cập nhật thi công |

Mỗi bộ có sáu mục từ với nghĩa Việt, từ loại, cấu trúc sử dụng, ví dụ mới, bản dịch ví dụ và diễn đạt lại. Từ gần nghĩa chỉ hỗ trợ hiểu trong ngữ cảnh; không mặc định thay thế được ở mọi vị trí. Từ gốc được gắn `verified: false`, không giả danh người học đã xác nhận hoặc chuyên gia đã thẩm định.

## Rà soát nội dung

- **Part 5:** 60 câu thuộc ba nhóm kỹ năng khác nhau. Rà soát chéo đã thêm ngữ cảnh để phân biệt `unless` với `although`, đại từ phản thân với tân ngữ thường, phạm vi bảo hành, phối hợp cùng nhau và mốc thời gian của `since`. Sửa kết hợp từ thành `responsibility for` và loại các phương án sai được tạo bằng từ không tồn tại khi có thể dùng dạng thật rõ ràng hơn.
- **Part 6:** 12 văn bản hoàn chỉnh, mỗi văn bản bốn chỗ trống có đánh số và một câu cần điền cả câu. Đủ 48 câu khớp chỗ trống; câu chèn dựa vào tham chiếu, mục đích, điều kiện hoặc quan hệ giữa các câu xung quanh. Không có câu hỏi trống rời khỏi văn bản của nó.
- **Part 7:** 12 cụm, mỗi cụm năm câu; bốn cụm một văn bản, bốn cụm hai văn bản và bốn cụm ba văn bản. Tất cả câu trong cùng cụm chia sẻ toàn bộ `document_ids`, để giao diện luôn cho thấy đầy đủ ngữ cảnh. Mỗi câu có bằng chứng nguyên văn từ một tài liệu thuộc cụm; lời giải chỉ rõ thông tin bổ sung phải đối chiếu khi cần.
- Rà riêng các phép tính: chi phí máy in **$915**, hoàn công tác phí **$64**, hóa đơn suất ăn gồm đặt cọc **$648**, đặt phòng sửa đổi **$600**, hoàn một tai nghe **$75**, taxi đến lúc **10:57**. Kiểm tra cả ngoại lệ về phí, thời hạn và thông tin mới thay thế thông tin cũ.
- Lời giải Việt giải thích đáp án và bẫy tiêu biểu; chuẩn hóa cách ghi giờ, tiền và phép tính để dễ đọc. Không suy diễn thành quyền lợi, điều kiện hoặc hành động không được tài liệu nêu.

Rà soát chéo được thực hiện bởi hai lượt tác nhân riêng trong phiên làm việc; đây không phải xác nhận của giám khảo TOEIC hoặc nghiên cứu tâm trắc độc lập.

## Kiểm tra đã chạy

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_toeic_expansion_content -v
```

**3/3 PASS**: khớp số chỗ trống Part 6; giữ toàn bộ ngữ cảnh và bằng chứng của từng cụm Part 7; số câu/văn bản/mục từ đúng cam kết. Ngoài ra, cả 12 JSON đều qua `validate_toeic_set`; nộp bộ đáp án chuẩn qua `grade_toeic` đạt **168/168**. Các bước này không dùng mạng hoặc database. Việc đúng cấu trúc và chấm được đáp án chuẩn không thay thế đánh giá độ khó với người học thật.

Bộ dựng HTML dùng thử sẽ lấy các JSON khi chạy lại `scripts/build_preview.py`; bản server cần nạp bằng `seed_toeic`. Lệnh seed thông thường thêm bộ mới, giữ nội dung biên tập đã tồn tại. Không xóa hoặc thay snapshot/lịch sử của người đã làm bài để cập nhật nội dung.
