# Gói nội dung v3

Gói nguồn: `lexiread_reading_vocab_v3_20261026.zip`, phiên bản 3.0.0 ngày 26/10/2026. Đây là nội dung luyện tập nguyên bản có AI hỗ trợ biên soạn, chưa có giáo viên độc lập kiểm định; không phải ngân hàng đề chính thức và không dùng để dự đoán band/điểm thi.

## Nội dung được tích hợp

- 486 đơn vị: 414 bài/phần luyện đọc và 72 bộ/phần TOEIC Reading.
- 3.240 câu đọc hiểu và 3.572 ngữ cảnh từ vựng, kèm 3.572 câu ôn từ. Có 1.815 mặt chữ khác nhau; số ngữ cảnh không phải số từ duy nhất.
- 486 bộ từ theo bài, dùng được với flashcard, bài tập, tra từ và lưu vào kho cá nhân. Giữ câu ví dụ tiếng Anh và nghĩa Việt gốc; không bịa bản dịch ví dụ còn thiếu.
- 12 đề Reading tổ chức theo từng phần (6 IELTS Academic, 2 IELTS General Training, 4 TOEIC); 90 bộ luyện ngắn tái sử dụng các bài đã có. Giao diện hiện luyện từng phần, chưa có phiên thi xuyên suốt cả đề.
- 146 liên kết tài liệu đọc thêm trong mục Bộ luyện Reading. Đây là danh mục từ ZIP, không phải lượt kiểm chứng web mới; không sao chép tài liệu bên ngoài.

Sau khi cộng với seed hiện có, một database mới có **354 bài general + 97 IELTS + 86 bộ TOEIC**, **516 bộ từ**. Các database có nội dung biên tập riêng có thể có số lượng khác.

## Nhập và triển khai

`entrypoint.sh` chạy migration, seed cũ, từ điển và `seed_content_v3` khi container khởi động. Render dùng entrypoint này nên sau khi merge và deploy thành công, không cần nhập thủ công.

```powershell
# Kiểm tra cấu trúc, đáp án, trích dẫn; không kết nối database
python manage.py seed_content_v3 --check --settings=config.test_settings

# Chạy trong môi trường Django đích đã được cấu hình
python manage.py migrate
python manage.py seed_content_v3
```

Migration `0014_alter_vocabularycollection_level` hỗ trợ nhãn `pre-A1`. Lệnh seed chỉ thêm slug chưa tồn tại. Không ghi đè bài đã biên tập, trạng thái xuất bản, tài khoản, từ cá nhân, lịch ôn hoặc snapshot bài đã mở. Đề trong danh mục chỉ hiển thị khi tất cả các phần vẫn đang được xuất bản.

Thư mục runtime `data/content_packs/v3` chứa JSON gốc nén (~1,44 MB), manifest/checksum và danh mục. Đáp án chỉ ở backend; các index phục vụ giao diện không chứa đáp án. Không chạy SQL hoặc script trong ZIP. `scripts/prepare_content_v3.py` kiểm tra SHA-256 theo manifest nguồn, xác nhận ID và thứ tự câu rồi tạo bundle có thể tái lập.

## Bỏ thư mục v1

Đã đối chiếu với bản v1 trong Git: đủ 60 ID và 60 phần bài đọc nguyên gốc trong v3. Các ID cũ vẫn dùng slug `pack-v1-*`, giữ đường dẫn và tiến độ. Bài mới dùng `pack-v3-*`.

Thư mục `lexiread_data_v1` không còn cần cho runtime, Docker QA, kiểm thử hay công cụ trích xuất bản dịch. Các tham chiếu hoạt động đã chuyển sang bundle v3. Xóa thư mục nguồn này không xóa bản ghi database. Bản cũ vẫn có trong lịch sử Git; ZIP v3 gốc được giữ cục bộ và không đưa lên Git.

## Database local

Bản QA trước đây dùng `tmpfs`; khi Docker tắt, dữ liệu của bản thử có thể mất. Ngày 27/10 kiểm tra database cũ đã trống (0 bảng), trước khi chuyển sang volume riêng `lexiread-qa_qa_pgdata`. Bản QA đã được nạp lại và tài khoản thử đã được tạo lại theo yêu cầu trước đó. Không truy cập hoặc thay đổi database Render.

Volume mới giữ dữ liệu qua restart/recreate container thông thường. `docker compose down -v` vẫn xóa volume; không dùng lệnh đó khi cần giữ dữ liệu QA.

## Kiểm tra

- Kiểm tra toàn bộ 486 bài, tất cả đáp án và ngữ cảnh; sửa mapping các đoạn chứa dòng trống và giữ đầy đủ nhóm nhiều văn bản TOEIC.
- Kiểm tra nhập lặp không nhân đôi, giữ chỉnh sửa biên tập và tiến độ; không gửi đáp án trước khi nộp.
- PostgreSQL: 151 kiểm thử backend đạt; 17 kiểm thử liên quan chạy lại sau sửa nhóm văn bản và ngữ cảnh đạt.
- 15 bộ Node đạt; Python unittest 112/113 đạt, 1 bỏ qua vì thiếu `reportlab` tùy chọn trên máy Windows.
- HTTP smoke và browser QA: dashboard, upload file → xem trước → chọn từ → lưu, bộ lọc/phân trang, pre-A1, TOEIC 54 câu/21 văn bản, đổi ngôn ngữ và màn hình 320/390px. Không tràn ngang tại các màn hình đã kiểm tra.

Kiểm tra cấu trúc không thay thế việc giáo viên rà soát toàn bộ nội dung học thuật. Giải thích v3 có bản gốc tiếng Việt; catalog dịch hiện tại không đảm bảo phủ toàn bộ câu giải thích mới.
