# Bản hoàn thiện để kiểm tra — 26/10/2026

Website thử nghiệm: **http://127.0.0.1:8766/**. Các thay đổi đã được triển khai vào Docker QA cục bộ; chưa push hoặc deploy lên domain thật. Không thay `.env`, database production hoặc dữ liệu học thật.

Tài khoản thử: `qa-reader` / `LexiRead-QA-2026!`. Tài khoản quản trị QA: `qa-editor`, cùng mật khẩu thử. Chỉ dùng hai tài khoản này ở localhost. Database QA dùng tmpfs; việc xóa container database sẽ làm mất dữ liệu thử.

## Những gì đã thay đổi

- Sửa chữ tiếng Việt bị tách dấu/giãn bất thường ở tiêu đề. Noto Sans và Noto Serif có đủ glyph tiếng Việt được lưu tại website, kèm giấy phép OFL. Không cần tải font từ dịch vụ ngoài lúc học. Điều chỉnh tracking, line-height, kích thước mobile và ô chọn ngôn ngữ của trang tài khoản.
- Giữ hình thỏ tai lá riêng và bảng màu kem/xanh; bổ sung các thẻ học, cẩm nang và khu kế hoạch cùng hệ thiết kế. Tài nguyên frontend có phiên bản để trình duyệt nhận bản sửa mới; production vẫn dùng manifest/hash của WhiteNoise.
- Kế hoạch 15/30/45 phút cho đọc hằng ngày, IELTS hoặc TOEIC: hướng dẫn → bài luyện chưa hoàn thành → ôn từ. Chọn bài theo ngày Việt Nam và tiến độ thật; không phải đánh giá năng lực thích ứng. Khi trình duyệt từ chối lưu, lựa chọn vẫn áp dụng trong màn hình hiện tại và có thông báo rõ.
- 18 cẩm nang: 12 IELTS, 6 TOEIC; 55 bước, 36 bẫy, 18 ví dụ tự biên soạn. Có tìm kiếm không dấu, lọc kỳ thi, thử trả lời, mở giải thích, đánh dấu đã đọc và liên kết sang loại bài phù hợp. Có thể đọc cẩm nang công khai trước khi đăng nhập.
- IELTS có lọc dạng câu hỏi, phân trang 12 bài và thời gian đọc ước lượng. Bộ lọc chạy ở API; không gửi đáp án hoặc bản nháp cho người học.
- TOEIC có tìm kiếm, lọc Part/thời lượng/tiến độ, xem thêm, đồng hồ có tạm dừng, số câu đã trả lời, đánh dấu và nhảy tới câu còn trống. Văn bản được đặt cạnh đúng nhóm câu hỏi của Part 6/7. Sau khi nộp có lọc riêng câu sai. Đồng hồ không tự nộp bài. Đáp án trong lượt làm được giữ khi chuyển trang trong cùng phiên; tải lại trang bắt đầu lại, đã ghi rõ trên màn hình.
- Tổng quan hiển thị đúng tổng số bài đọc; trang giới thiệu hiển thị số bộ TOEIC thật thay cho số hướng luyện.

Ý tưởng được chọn từ cách British Council LearnEnglish tổ chức chuẩn bị–đọc–kiểm tra và cách ReadTheory giới thiệu mục tiêu/tiến độ. Đây là điều chỉnh sản phẩm cho LexiRead, không sao chép giao diện hoặc passage của nguồn. Nguồn và lập luận: [nghiên cứu trải nghiệm học](LEARNING_EXPERIENCE_RESEARCH.md).

## Bộ từ cá nhân và lời văn

- Kho từ → **Tạo / nhập bộ từ**: tạo prompt theo chủ đề, trình độ và số từ; tải mẫu JSON hoặc dán kết quả AI; xem trước, bỏ chọn, lưu và ôn riêng theo bộ. Hỗ trợ file 2 MB / 500 mục.
- Nhập trùng giữ nội dung và lịch ôn; cùng từ khác nghĩa thành thẻ riêng. Nhập cả file trong giao dịch; dữ liệu tài khoản, ID, lịch ôn và cờ duyệt từ file ngoài không được áp dụng. Xuất riêng bộ từ để chia sẻ hoặc nhập lại.
- Có 9 kiểm thử Django cho nhập/xuất, phân quyền, CSRF, giới hạn, gộp trùng và bảo toàn dữ liệu; bộ Node kiểm tra bản offline tương ứng. Trình duyệt đã thử file thật, JSON sai, bỏ chọn một mục, ôn flashcard, nhập lại và tải file xuất hợp lệ.
- Hướng dẫn và mẫu: [cách tạo bộ từ](PERSONAL_VOCABULARY_IMPORT.md), [schema](vocabulary-import.schema.json), `static/examples/lexiread-vocabulary.json`.
- Rà tiếng Việt trong 10 bài IELTS, 12 bộ TOEIC (revision 2) và 18 cẩm nang. Giữ nội dung tiếng Anh, đáp án và bằng chứng sau lượt rà đáp án; chỉnh cách diễn đạt, không đổi ý.
- Thu gọn nguồn/thông tin bài trong mục mở rộng; ẩn tab trống, nút AI chưa bật và hướng dẫn kỹ thuật lặp lại. Chỉ hiện giải thích, từ vựng và hành động liên quan đến bài đang học.
- 22 bài trong QA đã được cập nhật qua script có kiểm tra database QA và nhật ký quản trị. Bài đọc cá nhân đã mở ở revision 1 vẫn giữ bản học cũ để bảo toàn tiến độ.

## Dữ liệu thực sự có trong từng bản

| Phạm vi | Bài đọc tổng quát | Bài IELTS | Bộ TOEIC | Câu TOEIC |
|---|---:|---:|---:|---:|
| File đi kèm và `preview.html` | 24 | 13 | 14 | 192 |
| Website QA có thêm bộ dữ liệu v1 đã nhập từ trước | 54 | 25 | 32 | 282 |

Website QA có **79 bài đọc + 32 bộ TOEIC**. Đây là bài luyện kỹ năng, không phải 111 đề thi đầy đủ.

Riêng đợt này thêm **10 bài IELTS / 100 câu / 70 mục từ / 60 bản dịch đoạn**, dài 482–510 từ mỗi bài; và **12 bộ TOEIC / 168 câu / 72 mục từ / 36 văn bản**. Tổng cộng **268 câu hỏi mới làm ngay trong ứng dụng**. Tất cả bài IELTS mới có bản dịch từng đoạn đầy đủ. Các bài tiếng Anh cũ chưa có bản dịch vẫn được gắn nhãn đúng, không dùng tóm tắt thay bản dịch.

Các bài mới là nội dung gốc với tình huống giả định, đã rà chéo đáp án và lời giải. Đã sửa câu NOT GIVEN mâu thuẫn với passage, một heading chưa chính xác, vài distractor/điểm ngữ pháp mơ hồ và các biến thể trả lời ngắn hợp lệ. Không có hiệu chuẩn độc lập của giám khảo hoặc giáo viên; mức CEFR chỉ là ước lượng, không quy đổi band/điểm. Xem [IELTS](IELTS_EXPANSION_REVIEW.md) và [TOEIC](TOEIC_EXPANSION_REVIEW.md).

Danh mục ngoài ứng dụng có **33 tài nguyên chính thức**: 28 IELTS, 5 TOEIC, 28 tài nguyên có liên kết đáp án. Bao gồm worksheet, tuyển tập và sổ tay; không gọi tất cả là đề mới. Crawler kiểm tra 50 URL: 41 OK, 9 PDF British Council được bỏ qua vì không lấy được robots; các PDF mới liên quan được kiểm tra riêng bằng công cụ web. Không vượt chặn truy cập, không sao chép toàn bộ đề vào kho gốc. Xem [nguồn công khai](PUBLIC_RESOURCES.md).

## Kết quả kiểm thử

| Kiểm tra | Kết quả |
|---|---|
| Python thuần, toàn bộ `tests/` | 105 test: 104 đạt, 1 bỏ qua do fixture PDF cần reportlab tùy chọn |
| Django / PostgreSQL QA | 104/104 đạt, gồm kiểm thử giao dịch/concurrency |
| Django / SQLite cô lập | 104 test: 103 đạt, 1 kiểm thử dành riêng PostgreSQL bỏ qua |
| Logic frontend cũ | Đạt: catalog, phân trang, chấm đáp án ngắn, i18n, XSS, thẻ từ và tài khoản |
| Nhập bộ từ cá nhân | 9 kiểm thử Django và luồng Node đạt; kiểm tra file, xem trước, lịch ôn, xuất/nhập, owner và CSRF |
| Logic learning hub mới | 5 nhóm đạt: storage lỗi, ngày Việt Nam, tìm/lọc/phân trang, escaping, đáp án hợp lệ, đồng hồ, đánh dấu, điều hướng và lọc câu sai |
| API cho toàn bộ nội dung mới | Mở và chấm đủ 10 IELTS + 12 TOEIC; không lộ khóa trước khi nộp, giữ idempotency |
| HTTP tại localhost | Đạt: login/logout, trang tài khoản, backup, số lượng, nguồn, cẩm nang, lọc dạng và các asset/font |
| Migration | Không thiếu migration; Django system check không phát hiện lỗi |
| Production static build trong container bỏ đi | Đạt: 165 file, 481 thao tác post-process, gồm font và nén/hash |
| Dữ liệu trong image QA | SHA-256 của cả 51 file bài đi kèm khớp repo sau rà chéo |
| JavaScript | Tất cả file `static/*.js` qua kiểm tra cú pháp |

Kiểm thử trình duyệt được thực hiện bằng công cụ điều khiển trình duyệt trên bản Django đang chạy, không chỉ kiểm tra HTML:

- Trang chủ và TOEIC ba văn bản: chiều rộng 320, 390, 768, 1024, 1440px, không tràn ngang. Đã nhìn ảnh desktop/mobile để kiểm tra dấu tiếng Việt và bố cục.
- Tài khoản/đổi mật khẩu: xem form ở 320/390px, sửa ô ngôn ngữ bị cắt chữ. Không đổi thông tin đăng nhập qua UI.
- Cẩm nang: lọc IELTS/TOEIC, tìm không có kết quả, đáp án trống/sai/đúng, lưu trạng thái và tải lại; biến thể `courtyard` được chấp nhận. Link luyện tập mở đúng bộ lọc IELTS TFNG.
- Kế hoạch học: đổi mục tiêu/thời lượng, tải lại và giữ lựa chọn. Trạng thái storage lỗi được kiểm tra bằng Node.
- IELTS mới: hiện/ẩn đủ sáu bản dịch, trả lời mười câu gồm nhập từ và chọn đáp án, nhận 10/10; lưu `diagnosis` vào kho thành công.
- TOEIC: bộ lọc, trạng thái rỗng, câu chưa làm, đánh dấu, đồng hồ chạy/dừng, giữ câu trả lời qua điều hướng, nộp 3/4 và chỉ xem một câu sai. Bộ mới ba văn bản có hai nhóm, mỗi nhóm ba văn bản/năm câu.
- Mở tất cả trang chính: tổng quan, thư viện, IELTS, TOEIC, bài riêng, kho từ, ôn từ, cài đặt, tài liệu chính thức, cẩm nang. Không có warning/error console trong lượt kiểm tra cuối.
- Đăng nhập/đăng xuất đã xác nhận cả UI lẫn HTTP. Các thao tác quản trị nội dung, quyền sở hữu, CSRF, tài khoản, reset mật khẩu và backup/restore được bao phủ bởi bộ Django hiện có.

Luồng bộ từ mới cũng được kiểm tra chiều rộng 320/390/768/1024/1440px, không tràn ngang. Ảnh: [tạo bộ từ desktop](qa/personal-deck-desktop.jpg), [xem trước trên điện thoại](qa/personal-deck-mobile.jpg).

Ảnh kiểm tra: [trang chủ desktop](qa/typography-fixed-desktop.jpg), [trang chủ mobile](qa/hero-mobile-390.jpg), [kế hoạch học](qa/daily-plan-desktop.jpg), [cẩm nang desktop](qa/guide-desktop.jpg), [cẩm nang mobile](qa/guide-mobile.jpg), [IELTS mới](qa/ielts-new-reading-desktop.jpg), [TOEIC mới](qa/toeic-new-practice-desktop.jpg), [kết quả mobile](qa/toeic-result-mobile.jpg).

Chưa kiểm tra Safari/Firefox trên thiết bị thật, gửi email khôi phục thật, domain/HTTPS production hoặc độ chính xác sư phạm với nhóm học viên. Không xem kiểm thử cục bộ là đảm bảo website không còn lỗi. Script browser cũ dùng đường dẫn Chromium Linux không được dùng làm bằng chứng cho đợt này.

## Chạy lại và bàn giao

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe manage.py test learning --settings=config.test_settings --noinput
node scripts/test_frontend_logic.cjs
node scripts/test_learning_hub_logic.cjs
node scripts/test_personal_decks.cjs
.\.venv\Scripts\python.exe scripts/build_preview.py
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa build web
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web manage.py test learning --settings=config.qa_settings --noinput
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web scripts/prepare_qa.py --publish-pack
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web scripts/update_qa_expansion.py
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa up -d web
.\.venv\Scripts\python.exe scripts/smoke_qa_http.py
```

QA mount static/template ở chế độ chỉ đọc. Sau khi thay template, khởi động lại web vì Django có cache template và QA dùng `--noreload`; sau thay Python/data cần rebuild. `seed_lessons`/`seed_toeic` chỉ thêm bài chưa có, giữ nội dung đã biên tập và snapshot người học. Không chạy quy trình QA lên production. Việc đưa bản mới lên website thật chờ người dùng kiểm tra trước khi push.
