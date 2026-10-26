# Mở rộng IELTS Reading trong ứng dụng — 26/10/2026

Đã bổ sung **10 bài gốc, 4.984 từ tiếng Anh, 100 câu hỏi, 70 mục từ và 60 bản dịch đoạn đầy đủ**. Mỗi bài dài 482–510 từ, gồm sáu đoạn A–F, 10 câu hỏi và 7 mục từ có cấu trúc sử dụng, ví dụ ngắn, bản dịch ví dụ, từ gần nghĩa và diễn đạt lại. Không thêm mục grammar hoặc FAQ: số mới của hai mục này đều bằng 0.

Đây là bài luyện kỹ năng riêng lẻ, **không phải đề IELTS chính thức, bài thi 40 câu đầy đủ hoặc công cụ quy đổi band**. Tất cả câu chuyện về dự án, thị trấn, thư viện và thử nghiệm là tình huống giả định; thông tin nguồn gốc ghi rõ trong từng JSON. Văn bản và câu hỏi được soạn riêng cho từng chủ đề, không chép passage từ sách hay website đề thi. Các mô tả định dạng tham khảo [trang Reading chính thức của IELTS](https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-reading); nguồn này không phải nguồn của nội dung bài đọc.

## Danh mục

| Slug | Chủ đề | Số từ | Mức ước lượng |
|---|---|---:|---|
| `ielts-repair-and-reuse` | Xưởng sửa chữa và giá trị của việc học | 482 | B2 |
| `ielts-night-trains-return` | Tàu đêm, nhu cầu và chất lượng vận hành | 485 | B2 |
| `ielts-community-noise-maps` | Bản đồ tiếng ồn, dữ liệu thiếu và riêng tư | 494 | B2 |
| `ielts-museum-touch` | Bản sao bảo tàng, xúc giác và diễn giải | 497 | B2 |
| `ielts-rooftop-water` | Thu nước, dùng nước và làm chậm thoát nước | 507 | B2 |
| `ielts-wildlife-crossings` | Hạ tầng cho động vật và theo dõi hiệu quả | 508 | B2 |
| `ielts-citizen-weather` | Nhật ký lịch sử và dữ liệu thời tiết | 500 | B2 |
| `ielts-library-of-things` | Cho mượn thiết bị và công bằng tiếp cận | 507 | B2 |
| `ielts-digital-margins` | Chú giải chung, tiếng nói và bằng chứng | 510 | C1 |
| `ielts-food-label-design` | Nhãn sản phẩm và khả năng hiểu thông tin | 494 | C1 |

Mức độ do người biên soạn ước lượng, chưa được hiệu chuẩn CEFR hoặc thử nghiệm với nhóm học viên. Từ trong tiêu đề đoạn A–F được tính bằng cách tách khoảng trắng cùng văn bản khi báo số từ.

## Kiểm tra nội dung đã thực hiện

- Mọi câu có `paragraph_index` và trích dẫn `evidence` nguyên văn. Đáp án NOT GIVEN chỉ ra thông tin thiếu, dùng trích dẫn gần nhất làm vùng kiểm tra; không xem trích dẫn đó là bằng chứng rằng điều không được nói là sai.
- TFNG kiểm tra thông tin; YNNG kiểm tra quan điểm rõ của người viết. Bộ YNNG có đủ YES, NO và NOT GIVEN.
- Heading chọn ý bao quát của một đoạn, có nhiều phương án hơn số đoạn đang hỏi. Matching information dùng A–F để chọn vị trí thông tin cụ thể. Định dạng câu hỏi đơn phù hợp giao diện hiện tại, không giả vờ là nhóm heading hoàn chỉnh của đề thi thật.
- Câu điền/đáp án ngắn ghi rõ giới hạn từ. Đáp án được chấp nhận đều xuất hiện trong đoạn gốc; trường `max_words` khớp chính xác chỉ dẫn ONE/TWO/THREE WORDS. Mạo từ chỉ được chấp nhận khi có căn cứ trong câu gốc.
- Hoán đổi vị trí phương án đúng cho câu nhiều lựa chọn để tránh toàn bộ đáp án đều là A. Nội dung distractor giữ nguyên, không dùng từ đồng nghĩa của đáp án đúng làm phương án sai tương đương.
- Bản dịch bảo toàn điều kiện, phủ định và độ chắc chắn: ví dụ `may`, `not necessarily`, `only`, `rather than`, `not automatically` được giữ đúng ý. Các lời giải tiếng Việt nêu vì sao thông tin khớp, mâu thuẫn hoặc không có trong bài.
- Một nhận định TFNG về số bộ phận thiết bị được thay bằng nhận định rõ ràng về giới hạn không gian/kỹ thuật; cách cũ có thể buộc người học suy diễn số lượng không được cho.
- Từ vựng có từ loại cụ thể, context là câu nguyên văn, ví dụ mới tối đa 20 từ và usage pattern ngắn. Ghi chú nói rõ từ gần nghĩa không thay thế được trong mọi ngữ cảnh.
- Đợt đọc chéo thứ hai đã rà toàn bộ 10 bài, 100 câu và 60 bản dịch. Câu NOT GIVEN ở bài chú giải số được đổi sang giới hạn số ghi chú chưa được nêu: nhận định cũ về tự động công khai thực ra mâu thuẫn lựa chọn chia sẻ tự nguyện. Heading bảo tàng dùng “feel” thay cho “function” để không ám chỉ bản sao có lưỡi cùn thực hiện được việc cắt thật.
- Bổ sung biến thể đáp án ngắn khi vẫn đúng nghĩa, đúng ngữ pháp và xuất hiện nguyên văn, như `diaries`, `text excerpt`, `engineer`. Không nhận `excerpt` trong chỗ trống sau mạo từ `a`, vì tạo thành `a excerpt` sai ngữ pháp.

## Kết quả máy kiểm tra

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_ielts_expansion -v
```

**4/4 tests PASS**, bao gồm kiểm tra từng bài bằng `validate_lesson`, toàn bộ đáp án trích xuất và giới hạn từ, độ đầy đủ bản dịch/từ vựng, phân bố loại câu và vị trí đáp án, cùng đường chấm bài hiện có. Mỗi bài nộp bộ đáp án chuẩn đạt 10/10. Không có truy cập mạng hoặc database trong các test này.

Các kiểm tra tự động phát hiện lỗi cấu trúc và grounding; chúng không thay thế thử nghiệm sư phạm độc lập. Bản này đã được rà ý nghĩa, logic đáp án và bản dịch trong quá trình biên soạn nhưng chưa được giám khảo IELTS độc lập hiệu chuẩn.

## Rà soát chéo sau biên soạn

Một tác nhân thứ hai đã đọc toàn bộ 10 passage, 100 câu hỏi và 60 bản dịch đoạn. Một nhận định trong `ielts-digital-margins` về tự động công khai ghi chú sau một tháng được thay bằng nhận định về hạn mức hai mươi ghi chú: nhận định cũ mâu thuẫn với quyền lựa chọn công khai nhưng lại được gán NOT GIVEN; nhận định mới hỏi thông tin thực sự không được cung cấp. Heading của đoạn B trong `ielts-museum-touch` được sửa từ tái hiện “function” sang “feel”, đúng với việc bản sao cho cảm giác cầm nhưng không cho cắt thật.

Các đáp án trích xuất được bổ sung dạng ngắn lấy nguyên văn khi vẫn đúng nghĩa, ngữ pháp và giới hạn từ, chẳng hạn `diaries` hoặc `text excerpt`. Riêng `excerpt` đứng một mình không được thêm vì câu hỏi đã có mạo từ `a`. Tất cả bản dịch được đối chiếu về phủ định, điều kiện và độ chắc chắn; không tìm thấy thay đổi ý nghĩa cần sửa thêm. Bộ bốn test IELTS tiếp tục PASS sau các chỉnh sửa. Rà soát này là kiểm tra chéo trong phiên, không phải thẩm định của giám khảo IELTS độc lập.

## Đưa vào thư viện

Dữ liệu nằm trong `data/lessons/`. Bộ dựng HTML dùng thử đọc các file này khi chạy `scripts/build_preview.py`. Bản Django cần nạp theo quy trình `seed_lessons` hoặc biên tập nội dung hiện có; không tự sửa snapshot bài mà người học đã lưu. Việc kiểm thử/import vào database do luồng QA riêng thực hiện. Không dùng những file bài mới này làm lý do xóa dữ liệu hoặc ghi đè lịch học của người dùng.
