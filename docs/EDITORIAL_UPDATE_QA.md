# Kiểm thử tài khoản, flashcard và nội dung — 26/10/2026

> Báo cáo giai đoạn trước. Kết quả mới hơn, browser QA và trạng thái bàn giao tại [REVIEW_2026_10_26.md](REVIEW_2026_10_26.md) và [RUNTIME_QA_2026_10_26.md](RUNTIME_QA_2026_10_26.md).

## Kết quả đã chạy

| Kiểm tra | Kết quả |
|---|---|
| Django trên Docker Python 3.12 + PostgreSQL 16 riêng | **78/78 PASS**, gồm migration từ database rỗng và test nhiều request tranh hạn mức |
| Django trên SQLite in-memory, Python local 3.14 | 78 tests: 77 PASS, 1 SKIP (test khóa PostgreSQL) |
| Pure Python unit tests | 81 tests: 80 PASS, 1 SKIP (reportlab tùy chọn) |
| Node logic và kiểm tra cú pháp JS | PASS |
| Django system check / migration drift | Không lỗi / không thiếu migration |
| HTTP tới server QA thật ở localhost | PASS |
| Validator dataset | 60 bài, 840 câu, 504 mục từ; 0 lỗi, 0 cảnh báo |

Không dùng `.env` hoặc database Neon/Render để chạy test.

## Những luồng được kiểm tra

- Đăng ký username, email/mật khẩu hợp lệ, chặn trùng không phân biệt hoa–thường, không nhận quyền staff từ biểu mẫu, đăng nhập bằng username hoặc email cũ.
- CSRF, giới hạn đăng ký và yêu cầu khôi phục; ngân sách dùng chung giữa worker được kiểm tra đồng thời trên PostgreSQL.
- Hồ sơ chỉ sửa trường được phép, không mất dữ liệu học; đổi username/email phải xác nhận mật khẩu hiện tại.
- Đổi mật khẩu cần mật khẩu cũ, giữ phiên hiện tại và làm phiên khác mất hiệu lực.
- Khôi phục dùng thư giả lập: hết hạn 1 giờ, chống sửa token, dùng lại không được; đổi email làm link cũ mất hiệu lực. Email trùng/khóa/không có tài khoản không được gửi. Provider failure không trả nội dung lỗi/key cho người dùng.
- Link khôi phục lấy URL chuẩn cấu hình, không dựa vào Host của người gọi. HTTPS mail adapter được mock; **không gửi thư thật**.
- Import nháp, phân quyền, CSRF, expiry, stale preview, rollback, giữ snapshot cá nhân và lịch sử TOEIC theo phiên bản.
- Xuất bản nhiều bài qua xác nhận có chữ ký; bài lỗi/đã bị sửa khiến cả đợt bị hủy. Chế độ chưa có bản dịch phải khai báo rõ, không nhận bản dịch nửa chừng.
- CSV/backup giữ cấu trúc từ; đọc được thẻ cũ. Backup bài English-only round-trip thành công, snapshot sai kiểu bị từ chối và rollback.
- Node chạy helper tạo nội dung flashcard: có cấu trúc/ví dụ/synonym/paraphrase; đoạn gốc nằm trong phần mở rộng ngoài vùng lật thẻ. Dữ liệu được escape; ví dụ quá dài không bị dùng làm đoạn dài trên mặt thẻ.
- Cài đặt người học không còn API key mẫu, Docker, `.env`, PostgreSQL/pg_dump hoặc tên model. Có liên kết hồ sơ/đổi mật khẩu. Từ điển tài khoản mới có VI/EN/FR/ZH.

## Database QA đang dùng

`scripts/prepare_qa.py --publish-pack` đã chạy trong project `lexiread-qa`:

- **69 bài đọc = 54 tổng quát + 15 IELTS**, và **20 bộ TOEIC** được xuất bản để kiểm thử.
- Gồm 27 bài đọc/2 bộ TOEIC đi kèm và 42 bài đọc/18 bộ TOEIC từ gói riêng.
- 42 bài mới không có bản dịch đoạn, hiển thị rõ nhãn. Bộ mini tự biên soạn, không phải đề chính thức và chưa được xác nhận chất lượng học thuật.
- 336 câu đọc/ngữ pháp + 504 mục từ của gói được chuyển vào luồng học. 504 câu ôn nghĩa bổ sung vẫn ở metadata, chưa có màn làm riêng.
- Dataset gốc `lexiread_data_v1` không bị sửa.
- HTTP smoke kiểm tra login/logout, trang hồ sơ/đổi mật khẩu, số bài, mở bài IELTS mới, không lộ đáp án/metadata, lưu cấu trúc từ và xuất backup.

Mở `http://127.0.0.1:8766/`. Username `qa-reader` hoặc email `qa-reader@example.test`, mật khẩu `LexiRead-QA-2026!`. Admin dùng username `qa-editor`, cùng mật khẩu QA. Không dùng tài khoản giả hoặc settings này trên website công khai.

## Lệnh chạy lại

```powershell
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa build web
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web manage.py test learning --settings=config.qa_settings --noinput
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web scripts/prepare_qa.py --publish-pack
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa up -d web
.\.venv\Scripts\python.exe scripts/smoke_qa_http.py
node scripts/test_frontend_logic.cjs
```

## Giới hạn và bước đưa lên web

- Chưa kiểm chứng trực quan desktop/mobile bằng trình duyệt cho revision này. Node/HTTP không phải kiểm thử layout. Báo cáo browser v2 cũ không phải kết quả của bản hiện tại.
- Chưa cấu hình Resend/domain, chưa gửi đến Gmail hay SMS. QA chỉ gửi mail vào console; test dùng locmem/mock.
- Chưa commit, push, deploy hoặc nhập database web thật. Không có phí SMS/AI/gửi mail phát sinh từ các kiểm thử.
- `preview.html` đã dựng lại với 27 bài đi kèm; không chứa bộ 60 bài nhập qua admin và không có tài khoản thật.
- Thẻ và snapshot đã lưu của người học không tự bị ghi đè. Thẻ cũ thiếu cấu trúc cần bổ sung trong màn sửa thẻ.
- Một số thông báo động cũ vẫn tiếng Việt; không coi bản dịch giao diện là bản dịch bài học.

Đưa lên web: sao lưu database → kiểm thử nâng cấp staging → deploy mã và migration `0008_accounts_and_word_patterns` → cấu hình gửi mail theo [ACCOUNT_SETUP.md](ACCOUNT_SETUP.md) → nhập/duyệt/xuất bản qua [LESSON_AUTHORING.md](LESSON_AUTHORING.md). Khi đã deploy code, những lần nhập bài sau không cần sửa code/deploy.

Trước phát hành, tự thử ở desktop/mobile: đăng ký → sửa tên → đổi mật khẩu → quên mật khẩu bằng email thật của bạn → mở bài và lưu từ → lật thẻ → đổi ngôn ngữ. Kiểm tra rõ nhãn bài chưa dịch và phân biệt bài tự soạn với liên kết tài liệu IELTS/ETS chính thức.
