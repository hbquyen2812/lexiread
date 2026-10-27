# Quản lý và nhập nội dung LexiRead

## Hằng ngày — không sửa code, không deploy lại

1. Đăng nhập `/admin/` bằng tài khoản có `is_staff` và quyền **add + change** cho CuratedLesson hoặc ToeicPractice.
2. Vào **Curated lessons** (tổng quát/IELTS) hoặc **Toeic practices** → **Nhập file / bộ dữ liệu**.
3. Chọn file → **Kiểm tra & xem trước**. Xem mã, trình độ, số câu và văn bản; bước này chưa tạo bài trong thư viện.
4. **Xác nhận lưu nháp**. Cả đợt nhập thành công hoặc không bài nào bị thay đổi. Xem trước hết hạn sau 30 phút và chỉ người tạo dùng được.
5. Mở bài nháp, duyệt nguồn/quyền sử dụng, bản dịch, đáp án và dẫn chứng. Tick **published** → Lưu. Website đọc trực tiếp PostgreSQL, không cần build/deploy lại.

Cũng có thể chọn 1–100 bài ở danh sách → **Duyệt và xuất bản các bài đã chọn** → xem danh sách → xác nhận. Bản xác nhận có hiệu lực 30 phút, gắn với phiên bản và người quản trị. Nếu một bài lỗi hoặc đã bị sửa, cả đợt không xuất bản; không công khai nửa chừng.

Nhập luôn lưu nháp, kể cả JSON có `published: true`. Trùng slug bị từ chối mặc định. Muốn thay bài: bỏ xuất bản, tăng `revision` trong JSON, bật cho phép cập nhật rồi xem trước. Bản học của người đã mở bài giữ nguyên. Sửa qua form tự tăng revision; từ chối form cũ khi người khác đã sửa.

Không xóa bài seed chỉ để ẩn: lần khởi động sau có thể thêm lại. Dùng **published = false** để ẩn bền vững.

## Định dạng

- **JSON:** một bài, danh sách 1–100 bài, gói xuất từ admin hoặc gói JSON cùng cấu trúc.
- **TXT/MD UTF-8, DOCX, PDF có lớp chữ:** tạo bài đọc nháp. Điền slug, tên, trình độ, chủ đề trong form. Không tự sinh bản dịch/đáp án. PDF tối đa 30 trang; chưa có OCR.
- Tối đa 8 MB/file; bài đọc tối đa 60.000 ký tự. Không nhận ZIP, SQL hoặc URL fetch.
- **Xuất:** chọn tối đa 100 bài → action Xuất JSON. File chứa đáp án và metadata quản trị; không đưa vào `static/`.

Gói xuất có `format: "lexiread-content"`, `version: 1`, `kind: "lesson"` hoặc `"toeic"`, và `items` là danh sách bài. Xuất một bài hiện có để lấy mẫu; xem thêm `data/lessons/a-quiet-start.json`, `data/toeic/`.

## Gói bài học nguyên bản

Không chạy SQL của gói: schema đó tách rời, website không tự đọc được. Adapter `learning/editorial/dataset.py` ánh xạ vào models hiện tại.

Nhập **cùng file `data/lessons.json` hai lần, ở hai mục khác nhau**:

| Mục admin | Bản ghi nháp | Cần làm tiếp |
|---|---:|---|
| Curated lessons | 42 | 12 IELTS + 30 phổ thông; chưa có bản dịch từng đoạn |
| Toeic practices | 18 | 6 Part 5, 6 Part 6, 6 Part 7; duyệt nội dung trước publish |

Giữ đủ 336 câu đọc/ngữ pháp và 504 mục từ theo ngữ cảnh. 504 câu ôn nghĩa bổ sung được giữ trong `editorial.original.vocabulary_questions`, **chưa có màn làm riêng cho bộ câu này**. Sau publish, người học vẫn lưu các mục từ vào kho để ôn theo chế độ sẵn có.

ID bền vững: `iel_001` → `pack-v1-iel-001`, không trùng bài cũ. Giữ nhánh học/tuổi/nguồn và dữ liệu gốc trong `editorial` để truy vết. Bài phổ thông ở nhánh general, phân mức pre-A1–C2; chưa có bộ lọc cấp trường riêng.

Theo metadata gói: AI tự biên soạn, tình huống hư cấu, chưa có giáo viên đánh giá độc lập; nguồn ngoài chỉ tham khảo cấu trúc/trình độ. Không gắn nhãn đề chính thức, full mock, dự đoán điểm hay chứng nhận CEFR. Kiểm tra cấu trúc không chứng minh nội dung đúng về sư phạm.

## Biên tập và chấm bài

Form bài đọc có ô văn bản, bản dịch và bộ tạo câu hỏi, không phải viết JSON cho các phần này. Mỗi đoạn/bản dịch cách nhau một dòng trống, đúng thứ tự. Chỉ số đoạn đầu là **0**. Từ vựng/ngữ pháp/FAQ là JSON nâng cao, không bắt buộc. TOEIC hiện nhập theo mẫu và sửa JSON trong admin; chưa có form trực quan cho từng câu TOEIC.

- Trắc nghiệm ý chính/chi tiết/từ vựng/suy luận, ghép tiêu đề/thông tin: 2–8 lựa chọn, `answer` là chỉ số từ 0.
- `tfng`: TRUE, FALSE, NOT GIVEN. `ynng`: YES, NO, NOT GIVEN, đúng thứ tự.
- `gap_fill`, `short_answer`: `options: []`, đáp án chữ, `accepted_answers`, `max_words`. Chấm chính xác sau chuẩn hóa Unicode/chữ hoa–thường/khoảng trắng; không chấm gần đúng, không bỏ dấu câu. Từ có gạch nối tính là một từ.

Publish cần 1–20 câu và trích dẫn đúng đoạn. Bản dịch có hai chế độ rõ ràng:

- `translation_status: "complete"` (mặc định): đủ bản dịch cho mọi đoạn (`analysis.translations`: `index`, `vi`).
- `translation_status: "not_provided"`: `translations: []`, giao diện ghi **chưa có bản dịch**, không hiện cột dịch rỗng. Gói 42 bài được nhập ở chế độ này. Không dùng bản dịch giả hoặc bản dịch chỉ có vài đoạn để vượt kiểm tra.

Với NOT GIVEN, trích đoạn liên quan và giải thích điều còn thiếu; không bịa dẫn chứng. Validator không kiểm định CEFR hoặc chất lượng học thuật. Tài liệu này chỉ hướng dẫn xuất bản; không chứng nhận gói AI đã được giáo viên duyệt.

## Từ vựng và flashcard

Mỗi mục nên có `word`, `pos`, `meaning_vi`, `usage_pattern` (cấu trúc hoặc collocation), `example` (một câu đơn giản), `example_vi`, `synonyms`, `paraphrases`. `context` giữ trích đoạn gốc để tra cứu, **không thay ví dụ trên mặt thẻ**. Nếu chưa có ví dụ/cấu trúc, giao diện báo thiếu và cho sửa; không tự bịa.

Adapter lấy `collocation` → `usage_pattern`; lấy `paraphrases` nếu có, nếu không thì dùng `definition_en` để diễn giải nghĩa, không khẳng định có thể thay nguyên cụm vào mọi câu. Từ gần nghĩa phụ thuộc ngữ cảnh. Các bộ TOEIC cũng có mục từ vựng trọng tâm để xem/lưu.

Thẻ cũ vẫn đọc được; trường mới mặc định rỗng. Thẻ đã lưu và snapshot bài cũ không bị tự ghi đè khi cập nhật thư viện. Có thể sửa thẻ cá nhân trong **Kho từ → Sửa**. CSV và backup học tập giữ được `usage_pattern`.

## Ranh giới dữ liệu

- CuratedLesson / ToeicPractice: nội dung chung trong PostgreSQL.
- Reading.lesson_snapshot: bài người học đã mở, không bị đổi khi sửa thư viện.
- ToeicAttempt.snapshot: đề lúc nộp. Nếu nguồn đổi giữa lúc làm, server từ chối revision cũ và yêu cầu bắt đầu lại.
- Vocabulary và tiến độ thuộc người học; nhập thư viện không tự thêm thẻ cá nhân.
- ContentImport: bản xem trước; áp dụng xong xóa bản sao payload. `cleanup_content_imports` dọn bản quá 7 ngày; lịch sử thao tác ở admin LogEntry.

Backup học tập v4 vẫn tương thích bản cũ; lượt TOEIC mới kèm snapshot. Backup này không thay thế backup PostgreSQL cho thư viện chung/tài khoản/nhật ký.

## CLI tùy chọn

```powershell
# Chỉ kiểm tra; không ghi database
python manage.py import_content path/to/lessons.json --kind lesson
python manage.py import_content path/to/lessons.json --kind toeic

# Lưu nháp trên database đã xác nhận là đích cần nhập
python manage.py import_content path/to/lessons.json --kind lesson --apply --editor YOUR_ADMIN_USERNAME
```

Không cần terminal Render để thêm bài: upload qua `/admin/` là luồng chính. `seed_lessons` / `seed_toeic` chỉ bootstrap bài đi kèm, mặc định không ghi đè. `seed_lessons --update` chỉ nhận revision cao hơn. Các script `author_lessons.py` / `author_expansion.py` tái tạo seed, không chạy lại sau khi tự sửa file mà chưa backup. `preview.html` chỉ đóng gói seed công khai, không đồng bộ admin/bài nháp.

Gói v3 đi kèm dùng `python manage.py seed_content_v3 --check` để kiểm tra và `python manage.py seed_content_v3` để nạp. Xem `CONTENT_V3.md`; không cần thư mục v1.
