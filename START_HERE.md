# LexiRead v2 — bắt đầu ở đây

**Học ngay:** mở `preview.html`. Có 12 bài biên soạn theo chủ đề/mức khó, bản dịch, từ gợi ý, cấu trúc, bài hiểu bài và giải đáp; giữ bộ 116 thẻ mẫu. Không cần API để dùng nội dung cố định.

**Website đầy đủ:** `README_VI.md` hướng dẫn cài Windows/Docker và Python. Backend là Django + PostgreSQL, không dùng SQLite. Thư viện dùng chung được nạp bằng `seed_lessons`; `seed_demo --username ...` chỉ là tùy chọn nạp bộ từ cá nhân cũ.

**Đã có LexiRead bản trước:** đọc `docs/READING_STUDIO_V2.md`, phần 6, trước khi thay code. Backup, giữ `.env`, giữ thư mục/Compose project name và volume hiện tại. Không xóa database volume.

**Muốn soạn thêm bài:** đọc `docs/LESSON_AUTHORING.md`. Bài chuẩn ở `data/lessons/*.json`, không hardcode trong giao diện. Admin có thể sửa nội dung chuẩn; snapshot của người đã học không bị tự thay thế.

**Bài tự nhập:** vào Bài đọc của tôi. Có thể tìm theo tiêu đề/nguồn/nội dung, lọc trạng thái hoặc yêu thích, sắp xếp và chuyển trang. Bôi đen từ để lưu hoặc chọn câu hỏi giải thích. AI qua backend là tùy chọn; không API thì copy prompt/dán JSON. Giải đáp biên soạn sẵn không cần AI.

**Ôn từ:** kho từ hỗ trợ tìm kiếm, lọc tag/bài nguồn/trạng thái học và sắp xếp. Tổng quan có mục tiêu ngày, streak và các nhóm mới/đang học/đã ghi nhớ. Thẻ đến hạn cũ hơn được ưu tiên; chọn **Quên** đưa thẻ gặp lại trễ hơn trong cùng lượt, tối đa một lần.

**Kiểm thử ngày 22/10/2026:** bộ pure Python chạy 76 test, gồm 75 PASS và 1 fixture reportlab tùy chọn skip; 49 checks DOM/preview PASS khi không có fixture v1 cũ (50 nếu cung cấp fixture đó). Django `check` PASS và `makemigrations --check --dry-run` không thấy thay đổi trong môi trường xác nhận tạm. 35 integration tests Django/PostgreSQL đã chuẩn bị nhưng chưa chạy vì không có PostgreSQL listener; Docker/full DB và API thật cũng chưa chạy. Đọc `docs/TEST_REPORT.md` trước khi triển khai rộng.

**Tiến độ:** xuất backup thường xuyên. Import gộp không ghi đè lịch ôn hiện có; chuyển sang tài khoản/kho trống khi cần khôi phục chính xác tiến độ từ bản khác. Không có đồng bộ tự động giữa HTML và server.
