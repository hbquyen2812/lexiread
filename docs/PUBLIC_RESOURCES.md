# Thư viện nguồn đề công khai — 26/10/2026

LexiRead có **23 tài nguyên chính thức** được biên tập từ IELTS.org, British Council, IDP IELTS và ETS. Đây là số liên kết tài nguyên, **không phải 23 đề thi đầy đủ hay 23 bộ câu hỏi không trùng nhau**. Nguồn PDF và bài tương tác có thể dùng lại cùng câu hỏi.

| Nhóm | Số tài nguyên | Cách dùng |
|---|---:|---|
| IELTS Academic, từng dạng câu hỏi | 10 | Mở bài tương tác, có liên kết đáp án PDF riêng |
| IELTS General Training, từng dạng câu hỏi | 7 | Mở bài tương tác, có liên kết đáp án PDF riêng |
| IELTS Academic, trải nghiệm thi trên máy | 1 | Ba bài đọc / 40 câu; bản trải nghiệm không bấm giờ như thi thật |
| IELTS Reading, tuyển tập PDF | 2 | Academic 46 trang; General Training 33 trang, đáp án trong tài liệu |
| ETS TOEIC / TOEIC Bridge | 2 | Mỗi PDF 34 trang, chứa cả Listening và Reading; Bridge là bài thi riêng |
| IDP Reading | 1 | Trang tập hợp bài luyện Reading |

Nội dung bài đọc tự biên soạn của LexiRead và các liên kết này là hai nguồn riêng. Tài nguyên ngoài mở trên website nhà xuất bản; không lưu điểm hay tiến độ vào LexiRead và không hoạt động ngoại tuyến. Không dùng mức điểm của bài mẫu để hứa hẹn band/điểm thật.

## Dữ liệu và tích hợp

- `data/public_sources/catalog.json`: danh mục đã duyệt, có nguồn, loại kỳ thi, dạng câu hỏi, định dạng, URL tài liệu/đáp án, ngày kiểm tra và trạng thái quyền sử dụng.
- `learning.services.public_resources.public_resources(exam=None)`: đọc dữ liệu local, không truy cập mạng/database; nhận bộ lọc `ielts` hoặc `toeic`, trả bản sao độc lập để dùng trong template hoặc JSON.
- `data/public_sources/crawl_report.json`: kết quả tìm liên kết tự động từ sáu trang nguồn. Chỉ gồm nhãn liên kết, URL, tiêu đề mục, mã HTTP và hash của trang; không lưu HTML hoặc nội dung đề.
- `data/public_sources/link_health.json`: kết quả kiểm tra URL tài liệu và đáp án. Chỉ đọc tối đa 4 KB mỗi tài nguyên để xác nhận loại nội dung; không ghi phần nội dung đó ra file.

`verification=publisher_page_checked` nghĩa là đã tìm thấy liên kết trên trang chính thức. `target_checked` nghĩa là đã kiểm tra trực tiếp tài nguyên (HTTP/MIME hoặc trình đọc PDF). Hai trạng thái này không phải kiểm thử toàn bộ giao diện làm bài của bên thứ ba. Ứng dụng Inspera cần JavaScript, cookie và kết nối mạng.

## Phạm vi thu thập và quyền sử dụng

Nguồn gốc chính:

- [IELTS Academic samples](https://ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test)
- [IELTS General Training samples](https://ielts.org/take-a-test/preparation-resources/sample-test-questions/general-training-test)
- [British Council Academic Reading](https://takeielts.britishcouncil.org/prepare/ielts-free-practice-mock-tests/academic/reading)
- [British Council General Training Reading](https://takeielts.britishcouncil.org/prepare/ielts-free-practice-mock-tests/general-training/reading)
- [ETS TOEIC preparation](https://www.ets.org/toeic/test-takers/prepare.html)
- [IDP Reading preparation](https://ielts.idp.com/prepare/all-test-types/reading)

Các bài mẫu được cho xem/tải công khai, nhưng chưa xác nhận quyền tái phân phối trên website khác. Tập Academic còn chứa trích đoạn có bản quyền của bên thứ ba. Vì vậy đợt cập nhật này **thu thập metadata và liên kết, không nhập nguyên văn passage/câu hỏi/đáp án vào database bài học**. PDF tiếp tục nằm trên máy chủ nhà xuất bản. Không gỡ paywall, vượt đăng nhập, né robots hoặc dùng bản scan sách thương mại. Muốn nhập nội dung đầy đủ cần tài liệu cho phép tái phân phối hoặc giấy phép phù hợp, kèm attribution và kiểm tra biên tập.

Kiểm tra chất lượng đã loại liên kết Listening bị đặt nhầm trong mục Reading trên trang General Training của British Council, và tránh dùng nhãn bài IDP không khớp URL Table Completion. Các bài General Training được lấy từ trang IELTS.org rõ loại bài.

## Chạy lại và mở rộng

Từ thư mục dự án, không cần `.env` hay quyền truy cập database:

```powershell
.\.venv\Scripts\python.exe scripts/crawl_public_resources.py
.\.venv\Scripts\python.exe scripts/crawl_public_resources.py --check-links
.\.venv\Scripts\python.exe -m unittest tests.test_public_resources -v
```

Có thể giới hạn một nguồn, ví dụ `--source ielts-academic`, hoặc lưu báo cáo riêng bằng `--output <path>`. Mặc định crawler chỉ đọc sáu trang cấu hình, đợi tối thiểu 1,5 giây giữa request, timeout 20 giây, tối đa 2 MB/trang và 100 liên kết/trang. HTTPS, hostname và mọi redirect phải nằm trong allowlist. Trước khi đọc mỗi nguồn, crawler kiểm tra `robots.txt`; thiếu file (404) được tiếp tục, lỗi/403/từ chối thì bỏ qua. Không thử né lỗi.

Crawler xuất báo cáo để duyệt, **không tự thay danh mục đang phục vụ**. Khi bổ sung: xác minh nguồn chính thức → kiểm tra quyền sử dụng → kiểm tra URL/dạng bài/đáp án → thêm metadata vào `catalog.json` → chạy validator/tests → review diff → triển khai code. Không cần migration. Sau khi thay catalog, khởi động lại worker để xóa cache đọc file. Cập nhật ngày `last_checked` chỉ khi thực sự kiểm tra, không thay ngày hàng loạt để che liên kết cũ.

Lần discovery ngày 26/10/2026: IELTS Academic, General Training, ETS và IDP đều trả HTTP 200; crawler bỏ qua hai trang British Council vì không lấy được robots cho client đó. Hai PDF British Council được kiểm tra độc lập bằng công cụ đọc web, không được ghi là crawler đã lấy thành công. Báo cáo health giữ nguyên cả trạng thái bị chặn/lỗi, không chuyển thành PASS.

Lần kiểm tra URL: **40 URL khác nhau**, gồm tài liệu và đáp án; **38 trả HTTP 200 với MIME phù hợp** (có kiểm tra `%PDF-` với PDF), **2 PDF British Council bỏ qua do robots của client crawler** và đã mở được độc lập qua công cụ web. HTTP của các bài tương tác chỉ xác nhận tải được ứng dụng HTML, chưa xác nhận thao tác làm/nộp bài trong Inspera. Mã thoát của crawler health là 1 để phản ánh hai URL bị bỏ qua; không có URL 404 trong các URL được phép kiểm tra.

## Kiểm thử

9 unit tests xác nhận số tài nguyên/lọc, dữ liệu trả về không sửa cache, không cho URL ngoài allowlist/javascript/localhost/port lạ, phát hiện trùng/thiếu provenance/nội dung đề bị chép, parser loại prose và trùng, chặn redirect ra ngoài, tuân thủ robots và nhận diện trang HTML giả PDF. Các test không truy cập Internet.
