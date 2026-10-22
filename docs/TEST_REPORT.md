# Kiểm thử LexiRead Reading Studio v2 — 22/10/2026

## Đã thực thi

**Bộ pure Python chạy 76 test: 75 PASS, 1 test tùy chọn skip** bằng:

```text
python -m unittest discover -s tests -v
```

75 test PASS kiểm tra chuẩn hóa/fingerprint, lịch ôn và phân nhóm theo `last_reviewed`, streak, bộ 116 thẻ, phân tích và nhập file; kiểm tra toàn bộ 12 bài/72 mục từ/48 câu hỏi/24 cấu trúc/24 FAQ; bắt trích dẫn bịa, sai đoạn, thiếu bản dịch, ID và phương án trùng, answer index sai; chấm điểm; lọc dữ liệu điểm không được phép trong cập nhật dấu trang; schema hỏi đáp, nguồn câu chọn, độ dài, hash và sự phân biệt khớp trích dẫn với đúng ý nghĩa. Test còn lại tạo PDF dùng reportlab được skip vì reportlab là dependency fixture tùy chọn, không phải runtime dependency.

**49 kiểm tra DOM/luồng bản HTML PASS** qua Chromium headless/Playwright, không dùng fixture v1 cũ:

- Homepage/library, mục tiêu ngày và streak; bộ lọc mức/chủ đề/trạng thái/yêu thích; 12 bài, mở/resume, riêng biệt với bài import.
- Bài đã lưu: tìm kiếm, trạng thái, yêu thích, sắp xếp, phân trang và lưu favorite.
- Kho từ: tìm kiếm, tag, bài nguồn, scope, sort, phân trang và liên kết về bài nguồn.
- Bản dịch ẩn/hiện; dấu trang; đánh dấu hoàn thành; chọn từ bằng Range/Selection và điền sẵn nghĩa, lưu vào kho cá nhân.
- 6 từ/2 cấu trúc; bộ hiểu bài cố định, không cho nộp thiếu câu, chấm 4/4 với giải thích, nộp lặp không tính hai lần.
- FAQ soạn sẵn không API; prompt hỏi đáp có nguồn và schema; nhập JSON câu trả lời; loại quote bịa trước khi ghi.
- Snapshot read-only trong preview; snapshot/score/bookmark/history được serialize và nạp vào DOM mới.
- Bài tự nhập không có bộ câu hỏi giả, không xuất hiện ở thư viện chuẩn; chọn đoạn hỏi.
- Backup v2 có snapshot/lượt làm/câu đã hỏi; import gộp không đặt lại tiến độ.
- Flashcard và sáu chế độ bài ôn nền cũ; ưu tiên thẻ quá hạn, lịch ôn tiếp theo và **Quên** requeue trễ tối đa một lần; responsive ở 390px; không lỗi JavaScript chưa bắt và không request mạng trong luồng offline.

Fixture HTML v1 là tùy chọn. Khi cung cấp fixture đó, suite có **50 checks** và kiểm thêm việc nạp dữ liệu serialize từ HTML v1 thật vào v2 mà vẫn giữ thẻ cá nhân và lịch ôn. Lần chạy 49 checks nêu trên không có fixture này nên không tuyên bố ca thứ 50 đã chạy.

**Giới hạn môi trường browser:** chính sách môi trường chặn điều hướng tới file/local HTTP. Không thay đổi chính sách chặn. Test sử dụng `page.set_content()` với **in-memory Storage test double**, rồi serialize/nạp lại ở DOM mới. Đây không phải thử nghiệm localStorage thật qua việc đóng/mở trình duyệt hoặc giữa các đường dẫn file khác nhau. Khi người dùng chạy bình thường, ứng dụng dùng localStorage thật.

Report máy đọc: `v2_browser_test_results.json`. Ảnh giao diện v2: `v2_home.png`, `v2_catalog.png`, `v2_quiz.png`, `v2_help.png`, `v2_mobile.png`. Đã xem trực quan các ảnh homepage, hỏi đáp và mobile; không thấy tràn ngang/cắt nội dung trong các ảnh đó.

Cú pháp Python được compile; các JS được kiểm tra bằng `node --check`. Validator chạy thành công trên cả 12 file. Kiểm tra hình thức/bằng chứng không tự chứng nhận chất lượng ngôn ngữ hoặc CEFR.

## Chuẩn bị nhưng chưa chạy

**35 integration tests Django/PostgreSQL đã chuẩn bị nhưng chưa chạy**: 16 trong `learning/tests.py`, 19 trong `learning/test_platform.py`. Có ca ownership/CSRF/idempotency, catalog/private isolation, saved-reading search/status/favorite/sort/pagination, vocabulary scopes/search/sort, streak/buckets, snapshot, grading, quoted Q&A, cloud consent với mock transport, text edit, backup và seed. Không gọi đây là test đã pass vì môi trường không có PostgreSQL listener để tạo test database.

Trong môi trường xác nhận tạm, `python manage.py check` đã PASS và `python manage.py makemigrations --check --dry-run` báo **No changes detected**. Hai lệnh này không thay thế integration test trên PostgreSQL. Chưa chạy migrations/constraints/row locks/auth/templates trên một test database PostgreSQL đầy đủ, Docker build/healthchecks hoặc full-stack browser test nối Django với database.

Chưa gọi OpenAI API thật, chưa kiểm tra quyền model/key/hạn mức/chi phí/chất lượng trả lời trên nội dung mới. Không có key trong gói.

Chưa có kiểm thử tải lớn, kiểm thử thâm nhập, mở public, đồng bộ đa thiết bị, trình duyệt mobile thật, backup/restore PostgreSQL production. Không có OCR hoặc hàng đợi background trong phạm vi v2.

## Cách chạy lại

```powershell
python -m unittest discover -s tests -v
python scripts/validate_lessons.py
python scripts/build_preview.py
node --check static/app.js
node --check static/reading_platform.js
node --check scripts/preview_adapter.js
```

Bộ Playwright là công cụ dev tùy chọn, không cần cài để sử dụng website. `scripts/test_platform_preview.py` dùng Storage double có chủ đích để có thể chạy trong môi trường hạn chế. Đặt `CHROMIUM_PATH` trỏ tới Chromium/Chrome hiện có khi đường dẫn khác. Test migration HTML v1 là tùy chọn: đặt `LEXIREAD_V1_PREVIEW` trỏ tới file HTML cũ. Không đặt biến này, suite chạy 49 checks; có fixture hợp lệ thì chạy 50 checks. Không được báo ca migration v1 đã thực thi khi fixture không có.

```powershell
$env:CHROMIUM_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:LEXIREAD_V1_PREVIEW = 'D:\backups\LexiRead_Preview.html'
python scripts/test_platform_preview.py
```

Sau khi cài backend với database phát triển, chạy:

```powershell
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web python manage.py test learning -v 2
```

Django tạo test DB riêng theo cấu hình, cần tài khoản DB có quyền phù hợp. Không cấu hình thử nghiệm vào database production.

## Kiểm tra chấp nhận trên máy thật

Sau backup và nâng cấp, kiểm tra migration `0002` đã áp dụng, `db/web` healthy, đăng nhập và đủ 12 bài. Mở bài, làm câu hỏi, lưu từ, reload thật; thử một bài import riêng; kiểm tra không lộ giữa hai tài khoản thường. Thử JSON hỏi đáp trước khi bật API. Xuất backup và nhập vào tài khoản trống, đối chiếu bài/thẻ/due/điểm/câu hỏi. Đóng rồi mở trình duyệt để kiểm tra lưu trữ thật. Khi đã ổn mới cân nhắc triển khai HTTPS/public.
