# Hướng dẫn tích hợp database

## 1. Chọn định dạng

| Trường hợp | File nên dùng |
|---|---|
| Backend chưa có schema hoặc muốn import từng bài | `data/lessons.json` / `lessons.jsonl` |
| PostgreSQL, muốn thử ngay một schema độc lập | `sql/seed_postgresql.sql` |
| Có models/ORM riêng | `data/normalized.json` |
| Công cụ ETL hoặc phần mềm chỉ nhận bảng | `data/csv/*.csv` |
| Tạo flashcard nhanh | `data/flashcards.json` |

**Thứ tự nhập bảng khi tự viết importer:** datasets → sources → lessons → lesson_sources → passages → words → senses → lesson_vocabulary → questions. File SQL đã xếp đúng thứ tự.

Đây là thứ tự tôn trọng khóa ngoại. Các mảng `options`, `answer`, `accepted_answers`, `evidence`, `synonyms`, `antonyms` và `learning_objectives_vi` dùng JSON/JSONB. Đừng split chúng bằng dấu phẩy: dùng JSON parser.

## 2. Ý nghĩa các bảng

| Bảng | Mục đích |
|---|---|
| datasets | Phiên bản và nguồn gốc của đợt dữ liệu |
| sources | Trang nguồn, tổ chức, URL, cách được sử dụng và trạng thái xác minh |
| lessons | Chủ đề, nhánh học, cấp độ ước lượng, độ tuổi gợi ý, hướng dẫn và trạng thái xuất bản |
| lesson_sources | Liên kết nguồn tham khảo với bài học |
| passages | Các đoạn/văn bản của bài; giữ thứ tự và nhãn A/B/C hoặc D1/D2/D3 |
| words | Mặt chữ chuẩn hóa và từ loại; cùng mặt chữ khác từ loại là bản ghi khác |
| senses | Nghĩa tiếng Việt và định nghĩa tiếng Anh của một mục từ |
| lesson_vocabulary | Từ xuất hiện ở đoạn nào, câu ngữ cảnh, ví dụ, collocation, synonym/antonym và cấp độ ước lượng |
| questions | Câu hỏi đọc/ngữ pháp và câu hỏi ôn từ, lựa chọn, đáp án, giải thích, dẫn chứng |

Khóa từ được tạo từ **mặt chữ + từ loại**, không tự động biến số nhiều/biến tố thành lemma. Nghĩa được tách theo mục từ và nghĩa tiếng Việt chuẩn hóa. Điều này tránh gộp bừa những nghĩa khác nhau; biên tập viên có thể hợp nhất những nghĩa tương đương sau. Không đếm mỗi lần xuất hiện trong bài là một “từ mới duy nhất”.

## 3. Các nhánh học

| `track` | Hiển thị gợi ý |
|---|---|
| `ielts_academic` | IELTS Academic Reading |
| `toeic` | TOEIC Reading |
| `school_primary` | Tiếng Anh tiểu học |
| `school_lower_secondary` | Tiếng Anh THCS |
| `school_upper_secondary` | Tiếng Anh THPT |

Khi lọc bài, nên kết hợp `track`, `cefr_estimate`, `topic` và `estimated_minutes`. Tuổi là gợi ý chủ đề; học sinh lớn mất gốc vẫn có thể học bài A1/A2.

## 4. Loại câu hỏi và chấm bài

| `type` | Cách gửi câu trả lời |
|---|---|
| `mcq_single` | Khóa lựa chọn như `"B"`, không gửi nguyên văn option |
| `true_false_not_given` | `"TRUE"`, `"FALSE"`, `"NOT GIVEN"` |
| `yes_no_not_given` | `"YES"`, `"NO"`, `"NOT GIVEN"` |
| `matching_heading` | Khóa heading được cung cấp trong `options` |
| `matching_information` | Khóa lựa chọn ứng với đoạn văn |
| `gap_fill`, `short_answer` | Chuỗi tiếng Anh cần khớp `accepted_answers` và `max_words` |

Mỗi câu trong phiên bản này có một đáp án. `answer` vẫn là mảng để thuận tiện mở rộng. Không tự hỗ trợ câu nhiều đáp án bằng cách đổi cấu trúc mà bỏ qua hàm chấm.

Hàm `tools/grading.py` chuẩn hóa Unicode, chữ hoa/thường và khoảng trắng; không tự bỏ dấu câu hoặc chấm gần đúng. Với điền từ, kiểm tra giới hạn từ rồi so với toàn bộ danh sách `accepted_answers`. Không dùng AI để “đoán gần đúng” cho đáp án đọc cần chính xác. Nếu muốn chấp nhận một biến thể hợp lệ, bổ sung tường minh sau khi biên tập.

Với TFNG, bằng chứng của câu `NOT GIVEN` là đoạn gần nhất để xem xét; giải thích chỉ ra điều còn thiếu. Sự hiện diện của trích dẫn không có nghĩa trích dẫn xác nhận câu nhận định.

## 5. Dẫn chứng và highlight

Trong `lessons.json`, `passage_id` là nhãn trong bài (`A`, `D1`...). Trong dữ liệu chuẩn hóa, đó là ID toàn cục như `iel_001_p_A`. Cột JSONB `evidence` còn có `passage_label`, `quote`, `start_char`, `end_char`.

Vị trí ký tự là offset từ 0, `end_char` không bao gồm ký tự cuối, tính theo Unicode code points của Python. Văn bản bài học v1 chủ yếu dùng ký tự BMP; nếu sau này thêm emoji, JavaScript dùng UTF-16 và có thể cần chuyển offset. Cách đơn giản là dùng `quote` để tìm trong đoạn và highlight đúng lần xuất hiện được chỉ định; offset hiện tại trỏ lần xuất hiện đầu tiên.

Part 6 giữ marker `[1]`… trong passage và câu hỏi chỉ rõ marker tương ứng. Part 5 chứa câu có khoảng trống `____`. Không tự thay đáp án vào passage trước khi làm bài.

## 6. Ví dụ truy vấn

```sql
SELECT track, COUNT(*) AS lessons
FROM lexiread_seed_v1.lessons
GROUP BY track ORDER BY track;

SELECT id, title_en, cefr_estimate, passage_word_count,
       reading_questions, vocabulary_contexts
FROM lexiread_seed_v1.lesson_overview
WHERE track = 'ielts_academic';

SELECT * FROM lexiread_seed_v1.question_prompts
WHERE lesson_id = 'toe_013'
ORDER BY category, position;

SELECT * FROM lexiread_seed_v1.flashcard_view
WHERE lesson_id = 'kid_001';
```

`question_prompts` là view tiện dùng, không tự tạo phân quyền database. Endpoint dành cho người học phải chọn các trường cần thiết; endpoint chấm bài lấy đáp án phía server. Không trả `answer`, `accepted_answers`, `evidence` hoặc `explanation_vi` trước khi nộp bài.

## 7. Gắn vào kho từ cá nhân

Giữ thư viện từ và trạng thái học của từng người ở các bảng riêng. Ví dụ, bảng của ứng dụng `user_vocabulary` có thể lưu `user_id`, `sense_id`, `first_context_id`, `saved_at`; bảng `review_events` lưu từng lần ôn, kết quả và lịch tiếp theo. Các bảng này chưa được tạo vì ứng dụng của bạn chưa cung cấp user model và thuật toán ôn.

Khi người dùng bấm lưu từ từ bài đọc, dùng `sense_id` để giữ đúng nghĩa và `lesson_vocabulary.id` để giữ câu gốc. Hai lượt lưu cùng mặt chữ nhưng khác nghĩa không nhất thiết là bản ghi trùng.

## 8. Cập nhật dữ liệu

Chạy lại seed giữ ID hiện có và bỏ qua hàng trùng; đây là cơ chế nạp ban đầu, không phải đồng bộ hai chiều. Muốn thay một bài đã xuất bản, tạo phiên bản mới hoặc cập nhật có chủ đích qua ORM, đồng thời giữ lịch sử làm bài. Không xóa bài đang có lượt làm để chỉ nạp lại từ đầu.

Sau khi sửa JSON, chạy validator và exporter. Xem cảnh báo độ dài và kiểm tra thủ công những câu đã thay đổi. Kết quả `errors: []` kiểm tra cấu trúc; không tự chứng minh độ khó, tính hay của distractor hay sự tương đương một band IELTS/điểm TOEIC.
