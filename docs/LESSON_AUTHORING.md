# Biên soạn và mở rộng thư viện LexiRead

## Hợp đồng nội dung

Mỗi file UTF-8 JSON trong `data/lessons` là một bài hoàn chỉnh. Để tạo bài mới, sao chép một file hiện có, đổi slug, tiêu đề, nội dung và toàn bộ phần học tương ứng. Không thay passage mà để nguyên câu hỏi/bằng chứng của bài khác.

| Trường | Quy tắc |
|---|---|
| `slug` | ID bền vững, chữ thường/số/gạch nối, duy nhất. Ví dụ `a-quiet-start`. |
| `title`, `topic`, `summary` | Tiêu đề tiếng Anh, chủ đề và giới thiệu ngắn tiếng Việt. |
| `level`, `level_note` | A1–C2 được schema hỗ trợ; phải nói rõ khi chỉ ước lượng. Bộ hiện có A2/B1/B2. |
| `revision`, `order`, `published` | Phiên bản ≥1, thứ tự không âm, boolean xuất bản. |
| `text` | Văn bản Anh; một dòng trống giữa các đoạn. |
| `author`, `provenance` | Ai biên soạn và quyền/nguồn sử dụng. |
| `analysis.translations` | Đủ mọi đoạn; `paragraph_index` bắt đầu từ 0. |
| `analysis.vocabulary` | Từ/cụm thực sự có trong ngữ cảnh; nghĩa, từ loại, synonym, paraphrase, note. |
| `analysis.grammar` | Cấu trúc, giải thích, ví dụ ngắn và bằng chứng nguyên văn. |
| `questions` | 1–20 câu, id riêng, loại, prompt, 2–4 options, answer index, lý do Việt, đoạn+quote. |
| `faqs` | 0–20 giải đáp soạn sẵn, question/answer_vi/paragraph_index/evidence. |

Xem `data/lessons/a-quiet-start.json` để dùng đúng tên trường. Schema nội bộ và validator ở `learning/services/analysis.py`, `catalog.py`. Không đưa HTML/JavaScript vào nội dung; app hiển thị như chữ.

`answer` là **chỉ số bắt đầu từ 0**, không phải A/B/C/D. Câu `tfng` dùng options đúng thứ tự `TRUE`, `FALSE`, `NOT GIVEN`. Với NOT GIVEN, trích thông tin gần nhất và giải thích rõ điều gì chưa được nói, không tạo một câu trích giả để chứng minh sự vắng mặt.

## Quy trình biên soạn

Viết bài với độ dài và độ khó nhất quán → dịch theo đúng đoạn → chọn ít từ có giá trị → thêm cấu trúc cần học → viết câu hỏi chỉ dựa trên bài → chọn bằng chứng đúng → soát đáp án và phương án nhiễu → kiểm tra máy → duyệt ngôn ngữ → xuất bản.

Các ví dụ hư cấu được ghi là hư cấu. Bài giải thích kiến thức khoa học, y tế, xã hội hoặc dữ liệu thật cần nguồn và kiểm chứng phù hợp; không biến câu chuyện trong bài thành khẳng định thực tế. Không gán level chính thức hoặc “đạt band” chỉ từ độ dài/từ khó.

```powershell
python scripts/validate_lessons.py
python -m unittest discover -s tests -v
python scripts/build_preview.py
```

Lệnh unit test có inventory test cho bộ 12 bài khởi đầu; khi chủ động thêm nội dung, cập nhật kỳ vọng số lượng trong `tests/test_reading_platform.py`. `validate_lessons.py` không cố định số 12. Cần cài dependency của project; riêng validator cơ bản dùng jsonschema và các module Python nội bộ.

`build_preview.py` đưa file JSON vào HTML. Với backend:

```powershell
# Thêm bài chưa tồn tại, không đụng nội dung/tiến độ hiện có
python manage.py seed_lessons

# Chủ động cập nhật bài chuẩn theo file (nên tăng revision trước)
python manage.py seed_lessons --update
```

Bản Docker mặc định COPY code/data vào image, không bind-mount. Khi sửa file trong máy, build lại image trước:

```powershell
docker compose up --build -d
docker compose exec web python manage.py seed_lessons --update
```

Seed không cập nhật snapshot đã mở; đây là lựa chọn giữ ổn định bài đang học, không phải lỗi đồng bộ. Muốn quản lý nhiều phiên bản và chuyển bản học cũ, cần thêm workflow duyệt nâng cấp có chủ đích, chưa có trong v2.

## Dữ liệu chung không phải dữ liệu người học

`CuratedLesson` là nội dung biên tập dùng chung; `Reading` với `catalog_slug` là bản riêng của một người; `Vocabulary`, `ReadingQuestion`, `LessonAttempt` thuộc bản học/tài khoản đó. Không chuyển bài tự import sang `CuratedLesson` nếu chưa được phép xuất bản.

File `scripts/author_lessons.py` là nguồn biên soạn bộ khởi đầu. Chạy lại nó có thể ghi đè các file JSON bài mẫu; không dùng như lệnh học hằng ngày và không chạy sau khi đã tự sửa bài mà chưa backup. Thêm JSON độc lập không cần sửa script này.

## Hạn chế kiểm tra tự động

Validator kiểm tra hình thức, option index, chỉ số đoạn, câu trích có thật và bản dịch đủ đoạn. Nó không chấm được bản dịch tự nhiên hay câu hỏi chỉ có duy nhất một đáp án đúng về nghĩa. Người biên soạn vẫn cần đọc duyệt. Đáp án ẩn khỏi API xem bài, nhưng có trong backup và HTML offline; đây là học cá nhân, không phải nền tảng thi chống gian lận.
