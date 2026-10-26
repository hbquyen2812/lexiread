# LexiRead — Reading & Vocabulary Dataset v1

Ngày biên soạn: **26/10/2026**. Ngôn ngữ bài học: tiếng Anh. Nghĩa từ và giải thích: tiếng Việt.

## Có gì trong gói?

| Nhóm | Bài | Câu đọc/ngữ pháp | Mục từ theo ngữ cảnh |
|---|---:|---:|---:|
| IELTS Academic | 12 | 96 | 120 |
| TOEIC Reading | 18 | 90 | 144 |
| Tiểu học | 10 | 50 | 80 |
| THCS | 10 | 50 | 80 |
| THPT | 10 | 50 | 80 |
| **Tổng** | **60** | **336** | **504** |

Ngoài 336 câu đọc/ngữ pháp, có **504 câu chọn nghĩa theo ngữ cảnh** được ghép từ các mục từ và distractor đã biên soạn: tổng 840 câu trong bảng questions. Có 504 flashcard theo ngữ cảnh. Kho từ gồm **468 mặt chữ khác nhau, 470 mục khi phân biệt từ loại**, được liên kết với 500 bản ghi nghĩa; những bản ghi nghĩa có thể được biên tập để hợp nhất thêm. Có 20 trang nguồn/chính sách và 59 nhãn chủ đề. Các chỉ số này được tính từ file dữ liệu, không phải số liệu của website nguồn.

## Bắt đầu ở đâu?

- **`data/lessons.json`**: dữ liệu đầy đủ dạng lồng nhau, mỗi bài có văn bản, câu hỏi, đáp án, giải thích, từ vựng và câu hỏi ôn từ. Dùng khi backend chưa có schema hoặc cần viết bộ chuyển đổi.
- **`data/lessons.jsonl`**: mỗi dòng là một bài, thuận tiện import theo lô.
- **`data/normalized.json`**: dữ liệu đã tách thành các bảng có ID và khóa liên kết.
- **`sql/seed_postgresql.sql`**: tạo schema riêng và nhập toàn bộ dữ liệu trong một transaction.
- **`data/csv/`**: mỗi bảng một CSV UTF-8, có header. Các cột mảng/đối tượng được lưu bằng JSON hợp lệ trong ô CSV.
- **`data/flashcards.json`**: thẻ từ theo ngữ cảnh; mỗi thẻ liên kết ngược về bài học và nghĩa của từ.
- **`data/sources.json`**: danh mục các nguồn giáo dục/chính sách đã khảo sát; chỉ chứa metadata và liên kết.
- **`manifest.json`**: số lượng thực tế theo nhóm, loại câu hỏi, kích thước và SHA-256 các file dữ liệu.
- **`docs/IMPORT_VI.md`**: cách import, cấu trúc, chấm điểm và cách gắn với website.
- **`docs/SOURCES_VI.md`**: nguồn tham khảo, cách sử dụng và trạng thái kiểm tra.
- **`docs/LESSON_CATALOG.md`**: mục lục đầy đủ từng bài.
- **`docs/validation_report.json`**: kết quả kiểm tra dữ liệu.

## Nội dung và nguồn gốc

Đây là bộ **bài tập mới do AI biên soạn**, dùng các trang chính thức để đối chiếu loại hoạt động, nhóm trình độ và dạng đề. Văn bản, câu hỏi, ví dụ, nghĩa và giải thích không được lấy nguyên từ đề IELTS/ETS/British Council/Cambridge. Các tình huống, tổ chức và sự kiện trong bài là nội dung học tập hư cấu; không dùng làm tài liệu factual về nghiên cứu thật.

Các bài IELTS và TOEIC là **mini practice**, phù hợp luyện đọc và học từ; không phải bài thi chính thức hoặc full mock test. Mục học sinh lớn là luyện kỹ năng đọc phổ thông, không được gắn nhãn “đề tốt nghiệp THPT chuẩn Bộ” hay “đề vào lớp 10” của một địa phương. Nhãn CEFR là **ước lượng khi biên soạn**, chưa qua chuẩn hóa thử nghiệm. Khoảng tuổi giúp chọn chủ đề phù hợp, không phải quy đổi tuổi sang trình độ.

Mọi bài được nhập ở trạng thái **`draft`**. Kiểm tra kỹ thuật và rà soát AI đã thực hiện; chưa có đánh giá độc lập của giáo viên hoặc pilot với người học. Sau khi biên tập nội dung, hệ thống của bạn có thể chuyển từng bài sang `reviewed` rồi `published`.

`source_ids` thể hiện **nguồn tham khảo cấu trúc/trình độ**, không khẳng định các tổ chức đó là tác giả hay đã thẩm định bài tự soạn. Bộ này không liên kết, được bảo trợ hoặc chứng thực bởi IELTS, ETS, British Council, Cambridge hay Oxford.

## Import nhanh vào PostgreSQL

Sau khi giải nén, mở terminal tại thư mục `lexiread_data_v1`. Cần PostgreSQL và công cụ `psql` trên máy của bạn. Tạo sẵn database phát triển, ví dụ `lexiread_dev`, rồi chạy:

```powershell
psql -U postgres -d lexiread_dev -v ON_ERROR_STOP=1 -f sql/seed_postgresql.sql
```

File seed tự tạo schema **`lexiread_seed_v1`**. Không cần chạy schema riêng trước. File không có `DROP`, `DELETE` hoặc lệnh sửa bảng hiện có của ứng dụng. ID có sẵn được bỏ qua bằng `ON CONFLICT DO NOTHING`; chạy lại cùng bản không sinh thêm bản ghi trùng. Nếu bạn đã sửa một hàng trong database, chạy lại sẽ **giữ hàng hiện có**, không cập nhật nội dung của nó.

Nếu dùng MySQL/MongoDB/Firebase hoặc models Django đã tồn tại, dùng JSON và ánh xạ sang models của bạn; SQL trong gói chỉ dành cho PostgreSQL. Chưa có thông tin schema thật của website, nên không có migration trực tiếp vào các bảng hiện tại.

## Kiểm tra / xuất lại

Python 3.10 trở lên, không cần cài package:

```powershell
python tools/validate.py data/lessons.json --sources data/sources.json
python tools/export.py
```

`export.py` đọc hai file JSON nguồn và tạo lại JSONL, dữ liệu chuẩn hóa, CSV, SQL, flashcard, manifest và báo cáo kiểm tra. Công cụ không tải web hoặc gửi dữ liệu đi đâu. Sửa bài trong `data/lessons.json`, không sửa riêng một bản CSV rồi kỳ vọng mọi định dạng tự đồng bộ.

## Lưu ý khi dùng trong ứng dụng

Giữ đáp án, giải thích và dẫn chứng ở backend cho đến khi người học nộp bài. File JSON đầy đủ là dữ liệu quản trị/import, không phải file nên đặt công khai trong thư mục static. View `question_prompts` chỉ cung cấp trường hiển thị câu hỏi; ứng dụng vẫn phải tự quản lý quyền truy cập.

Thẻ từ được tạo theo **nghĩa + ngữ cảnh**. Các thẻ trùng mặt chữ có thể có nghĩa khác hoặc xuất hiện ở bài khác. Số thẻ không phải số từ duy nhất; xem các chỉ số riêng trong manifest. Dữ liệu không cung cấp audio hay IPA chưa được xác minh.
