# Kiểm thử LexiRead Reading Studio v2 — 22/10/2026

## Đã thực thi

**Bộ pure Python chạy 81 test: 80 PASS, 1 test tùy chọn skip** bằng:

```text
python -m unittest discover -s tests -v
```

80 test PASS kiểm tra chuẩn hóa/fingerprint, lịch ôn và phân nhóm theo `last_reviewed`, streak, bộ 116 thẻ, phân tích và nhập file; toàn bộ 12 bài đọc; hai bộ TOEIC/24 câu/16 từ trọng tâm; đáp án không lộ trước khi nộp; evidence phải khớp nguồn; chấm điểm và thống kê từng Part; schema hỏi đáp và các giới hạn dữ liệu. Test còn lại tạo PDF dùng reportlab được skip vì reportlab là dependency fixture tùy chọn, không phải runtime dependency.

**56 kiểm tra DOM/luồng bản HTML PASS** qua Chromium headless/Playwright:

- Homepage/library, mục tiêu ngày và streak; bộ lọc mức/chủ đề/trạng thái/yêu thích; 12 bài, mở/resume, riêng biệt với bài import.
- TOEIC Reading có đúng hai hướng; bộ Part 5–6 hiển thị 12 câu mà không lộ key; nộp bài và lượt làm cá nhân được lưu.
- Dashboard traffic bị ẩn với tài khoản thường/bản preview; trang chủ hiển thị chỉ số đà học cá nhân.
- Bài đã lưu: tìm kiếm, trạng thái, yêu thích, sắp xếp, phân trang và lưu favorite.
- Kho từ: tìm kiếm, tag, bài nguồn, scope, sort, phân trang; một nghĩa giữ nhiều bài/ngữ cảnh; nhóm từ khó từ 3 lần quên.
- Bản dịch ẩn/hiện; dấu trang; đánh dấu hoàn thành; chọn từ bằng Range/Selection và điền sẵn nghĩa, lưu vào kho cá nhân.
- 6 từ/2 cấu trúc; bộ hiểu bài cố định, không cho nộp thiếu câu, chấm 4/4 với giải thích, nộp lặp không tính hai lần.
- FAQ soạn sẵn không API; prompt hỏi đáp có nguồn và schema; nhập JSON câu trả lời; loại quote bịa trước khi ghi.
- Snapshot read-only trong preview; snapshot/score/bookmark/history được serialize và nạp vào DOM mới.
- Bài tự nhập không có bộ câu hỏi giả, không xuất hiện ở thư viện chuẩn; chọn đoạn hỏi.
- Backup v4 có snapshot/lượt làm/câu đã hỏi/các lần xuất hiện/lượt TOEIC; import gộp không đặt lại tiến độ; bài riêng trùng tiêu đề/nội dung vẫn tách biệt và import lặp không nhân đôi.
- Flashcard và sáu chế độ bài ôn nền cũ; ưu tiên thẻ quá hạn, lịch ôn tiếp theo và **Quên** requeue trễ tối đa một lần; responsive ở 390px; không lỗi JavaScript chưa bắt và không request mạng trong luồng offline.

Fixture HTML v1 là tùy chọn. Khi cung cấp fixture đó, suite có thêm một check việc nạp dữ liệu serialize từ HTML v1 thật vào v2 mà vẫn giữ thẻ cá nhân và lịch ôn. Lần chạy 56 checks nêu trên không có fixture này.

**Giới hạn môi trường browser:** chính sách môi trường chặn điều hướng tới file/local HTTP. Không thay đổi chính sách chặn. Test sử dụng `page.set_content()` với **in-memory Storage test double**, rồi serialize/nạp lại ở DOM mới. Đây không phải thử nghiệm localStorage thật qua việc đóng/mở trình duyệt hoặc giữa các đường dẫn file khác nhau. Khi người dùng chạy bình thường, ứng dụng dùng localStorage thật.

Report máy đọc: `v2_browser_test_results.json`. Ảnh giao diện v2: `v2_home.png`, `v2_catalog.png`, `v2_quiz.png`, `v2_help.png`, `v2_mobile.png`. Đã xem trực quan các ảnh homepage, hỏi đáp và mobile; không thấy tràn ngang/cắt nội dung trong các ảnh đó.

Cú pháp Python được compile; các JS được kiểm tra bằng `node --check`. Validator chạy thành công trên cả 12 file. Kiểm tra hình thức/bằng chứng không tự chứng nhận chất lượng ngôn ngữ hoặc CEFR.

## Django/PostgreSQL đã chạy

**43/43 integration tests Django/PostgreSQL PASS** trong container bằng `docker compose exec -T web python manage.py test learning -v 1`. Bộ test gồm landing page công khai không lộ bài cá nhân, API học vẫn yêu cầu xác thực, đăng nhập email không chấp nhận username, email duy nhất trong Django Admin, proxy header chỉ được dùng trong chế độ proxy tin cậy, ownership/CSRF/idempotency, catalog/private isolation, saved-reading search/status/favorite/sort/pagination, vocabulary scopes/search/sort, nhiều occurrence cho một nghĩa, streak/buckets/từ khó, backup v4, snapshot, grading, quoted Q&A, cloud consent với mock transport, text edit, seed, TOEIC attempt riêng tư và analytics không lưu IP/chỉ admin xem tổng/giữ cùng visitor khi đăng nhập.

Docker image đã build; `db` báo healthy và `web` hoàn tất healthcheck sau khởi động. `python manage.py check` PASS, `python manage.py makemigrations --check --dry-run` báo **No changes detected**, và `showmigrations learning` xác nhận `0001`–`0006` đã áp dụng. Chưa chạy browser end-to-end nối trực tiếp UI với Django/PostgreSQL; browser suite dùng adapter offline.

Production overlay đã được render bằng domain mẫu và service `web` đạt healthcheck khi chạy đúng biến proxy/HTTPS production. `manage.py check --deploy` PASS không cảnh báo khi bật cấu hình HSTS đầy đủ; cấu hình khởi đầu mặc định cố ý giữ `includeSubDomains/preload=false` và phát hai cảnh báo `W005/W021` đã giải thích trong `DEPLOYMENT.md`. `caddy validate` báo cấu hình hợp lệ, `pip check` không thấy dependency hỏng và lệnh `pg_dump --schema-only` chạy thành công. Chưa cấp chứng chỉ/domain thật hoặc thử phục hồi dump production.

Cấu hình miễn phí Render + Neon cũng đã được thêm. Image mới build thành công; parser `DATABASE_URL` được kiểm tra với mật khẩu URL-encoded, `sslmode`, `channel_binding` và kết nối PostgreSQL thật trong Docker. `manage.py check`, 81 test lõi và 43/43 integration test tiếp tục PASS; container local khởi động lại và đạt trạng thái healthy. Chưa deploy lên tài khoản Render/Neon thật vì cần chủ tài khoản đăng nhập và tạo các tài nguyên miễn phí.

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

Bộ Playwright là công cụ dev tùy chọn, không cần cài để sử dụng website. `scripts/test_platform_preview.py` dùng Storage double có chủ đích để có thể chạy trong môi trường hạn chế. Đặt `CHROMIUM_PATH` trỏ tới Chromium/Chrome hiện có khi đường dẫn khác. Test migration HTML v1 là tùy chọn: đặt `LEXIREAD_V1_PREVIEW` trỏ tới file HTML cũ; khi không đặt, suite hiện chạy 56 checks.

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

Sau backup và nâng cấp, kiểm tra migration `0006_daily_visit` đã áp dụng, `db/web` healthy, đăng nhập và đủ 12 bài cùng 2 lựa chọn TOEIC. Mở hai bài có cùng một nghĩa, lưu từ ở cả hai và lọc theo từng nguồn; kiểm tra không lộ giữa hai tài khoản thường. Thử JSON hỏi đáp trước khi bật API. Xuất backup v4 và nhập vào tài khoản trống, đối chiếu bài/thẻ/ngữ cảnh/due/điểm/câu hỏi/lượt TOEIC; nhập lại lần hai không được nhân đôi. Đóng rồi mở trình duyệt để kiểm tra lưu trữ thật. Khi đã ổn mới cân nhắc triển khai HTTPS/public.
