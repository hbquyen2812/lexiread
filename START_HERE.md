# LexiRead v2 — bắt đầu ở đây

**Bản mới để kiểm tra (26/10/2026):** mở `http://127.0.0.1:8766/` hoặc `preview.html`. Đã sửa font tiếng Việt, thêm kế hoạch học, 18 cẩm nang có ví dụ tương tác, bộ lọc dạng câu hỏi, đồng hồ/đánh dấu/xem câu sai TOEIC và 33 tài nguyên chính thức. [Báo cáo kiểm thử và phạm vi dữ liệu](docs/COMPLETION_REVIEW_2026_10_26.md). Chưa push/deploy bản này.

**Học ngay:** mở `preview.html`. Có 37 bài đọc (24 tổng quát A1–C1 + 13 luyện kỹ năng IELTS), 14 bộ TOEIC/192 câu/88 mục từ; giữ bộ 116 thẻ mẫu. Riêng đợt này thêm 10 bài IELTS/100 câu/60 bản dịch đoạn và 12 bộ TOEIC/168 câu. Không cần API cho nội dung cố định.

**Thêm bài không sửa code:** `/admin/` → Curated lessons / Toeic practices → Nhập file → Xem trước → Lưu nháp → Duyệt và xuất bản. [Hướng dẫn, gồm bộ 60 bài mới](docs/LESSON_AUTHORING.md). Bộ mới chưa tự xuất bản; 42 bài đọc thiếu bản dịch từng đoạn.

**Website đầy đủ:** `README_VI.md` hướng dẫn cài Windows/Docker và Python. Backend là Django + PostgreSQL; SQLite chỉ dùng cho kiểm thử cô lập. Khách chưa đăng nhập xem được danh mục và cẩm nang; đăng nhập bằng tên tài khoản hoặc email để học và lưu tiến độ. Thư viện dùng chung được nạp bằng `seed_lessons`; `seed_demo --email ...` chỉ là tùy chọn nạp bộ từ cá nhân cũ.

**Đã có LexiRead bản trước:** đọc `docs/READING_STUDIO_V2.md`, phần 6, trước khi thay code. Backup, giữ `.env`, giữ thư mục/Compose project name và volume hiện tại. Không xóa database volume.

**Muốn soạn thêm bài:** đọc `docs/LESSON_AUTHORING.md`. Bài chuẩn ở `data/lessons/*.json`, không hardcode trong giao diện. Admin có thể sửa nội dung chuẩn; snapshot của người đã học không bị tự thay thế.

**Bài tự nhập:** vào Bài đọc của tôi. Có thể tìm theo tiêu đề/nguồn/nội dung, lọc trạng thái hoặc yêu thích, sắp xếp và chuyển trang. Bôi đen từ để lưu hoặc chọn câu hỏi giải thích. AI qua backend là tùy chọn; không API thì copy prompt/dán JSON. Giải đáp biên soạn sẵn không cần AI.

**Ôn từ:** kho từ hỗ trợ tìm kiếm, lọc tag/bài nguồn/trạng thái học và sắp xếp. Một nghĩa có thể ghi nhận nhiều bài/ngữ cảnh mà vẫn dùng chung một lịch ôn. Tổng quan có mục tiêu ngày, streak và nhóm **Từ khó** cho thẻ đã quên từ 3 lần. Thẻ đến hạn cũ hơn được ưu tiên; chọn **Quên** đưa thẻ gặp lại trễ hơn trong cùng lượt, tối đa một lần.

**Kiểm thử ngày 22/10/2026:** bộ pure Python chạy 81 test, gồm 80 PASS và 1 fixture reportlab tùy chọn skip; 56 checks DOM/preview PASS. Docker Compose chạy healthy; migrations đến `0006_daily_visit` đã áp dụng; Django `check` PASS và 43/43 integration tests Django/PostgreSQL PASS. Landing page, form email và mobile đã qua Chromium smoke test. Production Compose/Caddy đã qua deployment check với domain mẫu; hai cảnh báo HSTS mặc định là chủ đích và được giải thích trong hướng dẫn. Chưa deploy domain thật. Đọc `docs/TEST_REPORT.md`, `docs/DEPLOY_FREE.md` hoặc `docs/DEPLOYMENT.md` trước khi triển khai.

**Tiến độ:** xuất backup thường xuyên. Import gộp không ghi đè lịch ôn hiện có; chuyển sang tài khoản/kho trống khi cần khôi phục chính xác tiến độ từ bản khác. Không có đồng bộ tự động giữa HTML và server.

Bộ từ cá nhân: vào **Kho từ → Tạo / nhập bộ từ** để tạo prompt AI, nhập file JSON, xem trước và ôn theo bộ. [Hướng dẫn và cấu trúc file](docs/PERSONAL_VOCABULARY_IMPORT.md).
