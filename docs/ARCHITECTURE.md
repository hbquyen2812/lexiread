# Kiến trúc và điểm mở rộng — v2 + editorial workflow

## Cập nhật 26/10/2026

`CuratedLesson` và `ToeicPractice` trong PostgreSQL là nguồn thư viện runtime. `data/lessons/` và `data/toeic/` chỉ bootstrap/offline demo. Thêm bài qua admin không sửa code/deploy lại. Xem [quy trình nội dung](LESSON_AUTHORING.md).

```text
learning/
  models.py, migrations/       dữ liệu và thay đổi schema
  views.py                    API người học, giới hạn theo owner
  editorial/
    admin.py                  nhập → xem trước → xác nhận, xuất JSON
    forms.py                  biên tập, kiểm tra phiên bản sửa
    services.py               quyền, atomic import, audit
    dataset.py                adapter gói bài đọc v1/v3
  services/
    catalog.py, toeic.py       validation/scoring thuần
    toeic_repository.py       TOEIC runtime từ database
    importers.py              trích xuất văn bản
    storage.py                backup/restore cá nhân
templates/admin/editorial/    UI quản trị nội dung
static/editorial.*           form tạo câu hỏi
config/test_settings.py      test SQLite tách biệt, không đọc .env
```

Cấu trúc Django này phù hợp quy mô hiện tại. JSONB cho một bài có phiên bản không phải thiết kế sai; người dùng, bài học, từ và lượt học vẫn relational. Đã tách biên tập khỏi views và tách TOEIC repository khỏi validator. `views.py` / `static/app.js` còn nhiều trách nhiệm, nên tách theo tính năng khi tiếp tục mở rộng; chưa cần microservices hay database thứ hai.

`data/content_packs/v3/` là gói runtime có checksum, được nhập bổ sung qua `seed_content_v3`. Nó thay thế thư mục nguồn v1; giữ slug của 60 bài cũ. ZIP gốc được giữ cục bộ, các CSV/SQL/JSONL lặp lại không đi vào Docker image. Không thay đổi dữ liệu riêng hay backup. Xem `CONTENT_V3.md`.

Import kiểm tra 8 MB/100 bài, staff+model permissions, CSRF, owner, hết hạn, khóa hàng và phiên bản kỳ vọng. Ghi batch trong transaction, audit bằng LogEntry. Draft chưa đủ dịch/câu hỏi bị chặn khi publish. `track` có index; API lọc trạng thái/yêu thích trước phân trang.

TOEIC giữ snapshot khi nộp, kiểm tra revision để không chấm nhầm phiên bản. Backup v4 mới kèm snapshot; v4 cũ khôi phục bộ bundled gốc. SQLite smoke tests không chứng minh PostgreSQL lock/concurrency. Phần bên dưới mô tả nền tảng v2; quy trình hiện hành theo tài liệu trên.

## Lựa chọn thiết kế

Django 5.2 LTS + PostgreSQL 16, frontend HTML/CSS/JavaScript thuần. Django giữ authentication/session/CSRF và phục vụ API JSON cùng origin. Không JWT/localStorage token, không cần CORS cho cấu hình này. Dữ liệu của ứng dụng đầy đủ lưu PostgreSQL; localStorage chỉ dùng trong bản HTML demo độc lập.

```text
Trình duyệt
  templates/app.html + static/app.css + static/app.js
          ↓ same-origin requests + session + CSRF
Django views (owner-scoped)
          ↓
Services: input → schema → grounding → data / exercises / scheduling
          ├── PostgreSQL
          └── OpenAI Responses API (chỉ sau xác nhận)
```

Không phụ thuộc nhà cung cấp AI khi ôn dữ liệu đã lưu. Không có tiến trình tự gửi mọi passage ra cloud. Không có OCR, crawler hay URL fetch. PDF/DOCX chỉ được đọc khi người dùng upload.

## Tổ chức mã nguồn

| File | Trách nhiệm |
|---|---|
| `config/settings.py` | Env, PostgreSQL, auth, CSRF, static, bảo mật |
| `learning/models.py` | Reading, Vocabulary, ReviewLog, ExerciseAttempt, AICall, LoginFailure |
| `learning/views.py` | API, ownership, limits, request/response, auth |
| `learning/services/core.py` | Chuẩn hóa, validate, fingerprint, lịch ôn đơn giản |
| `learning/services/analysis.py` | JSON schema, prompt, kiểm tra trích dẫn và paragraph index |
| `learning/services/ai.py` | Adapter OpenAI, error handling, JSON output |
| `learning/services/importers.py` | TXT, MD, DOCX, PDF text extraction |
| `learning/services/exercises.py` | Sinh câu hỏi, distractors và ngữ cảnh |
| `learning/services/storage.py` | Lưu trùng, idempotency, backup, import merge |
| `static/app.js` | Routing hash, editor, reader selection, practice flows |
| `static/app.css` | Theme, responsive layout, cards, modal |
| `scripts/preview_adapter.js` | LocalStorage backend giả lập cho HTML; không tải trong Django |

## Luồng thư viện cố định (v2)

`data/lessons/*.json` → validator → bảng dùng chung `CuratedLesson` → mở bài tạo `Reading` snapshot riêng → `LessonAttempt` và `ReadingQuestion` của bản học → chọn từ vào `Vocabulary`.

`Reading.catalog_slug` trống là bài tự nhập; không trống là bản học riêng từ thư viện chuẩn. Unique owner+slug (khi không trống) ngăn mở trùng. `lesson_snapshot` giữ nguyên phiên bản đang học; `progress` lưu paragraph, completed, favorite, quiz_best/total/attempts. Shared seed mặc định chỉ thêm. Sửa nội dung chuẩn không ghi đè bản học đang có.

`LessonAttempt` lưu answers/result và unique reading+token; server chấm từ snapshot. `ReadingQuestion` lưu câu hỏi, phần chọn, JSON lời giải, hash văn bản và origin. Đổi bài nguồn làm lịch sử cũ không còn được hiển thị là câu trả lời cho bài mới.

`static/reading_platform.js` triển khai catalog, homepage, quiz, tiến độ và hỏi đáp; `catalog.py` validate/grade; `qa.py` prompt/schema/exact evidence. `toeic.py` validate bộ Part 5–7, giấu answer key và chấm phía server. `storage.py` xuất backup v4, đọc backup v1–v4 và giữ định danh nguồn để import lặp không tạo trùng bài/lượt TOEIC.

`traffic.py` ghi một `DailyVisit` cho mỗi mã phiên/ngày, cộng lượt xem theo trang và gắn owner sau đăng nhập. Mã phiên được băm với `SECRET_KEY`; không lưu IP. API tổng hợp chỉ cho staff/superuser. Analytics không được đưa vào backup học tập vì là dữ liệu vận hành, không phải tiến độ cá nhân cần chuyển tài khoản.

Routes mới:

```text
GET        /api/catalog/ (q, level, topic, status, favorite)
POST       /api/catalog/<slug>/open/
POST       /api/readings/<uuid>/progress/
POST       /api/readings/<uuid>/quiz/
GET, POST  /api/readings/<uuid>/questions/
POST       /api/prompts/ (task=question bổ sung)
```

API xem bài không trả answer key trước nộp; backup và HTML offline vẫn có đáp án để người học sở hữu dữ liệu. Không thiết kế để chống gian lận thi cử. API catalog hiện tối đa 300 bài. Danh sách bài riêng dùng phân trang; dropdown nguồn dùng endpoint riêng và chỉ trả những bài đang có thẻ liên kết.

## Các bảng và quan hệ

**Reading:** một owner, title, original text, analysis JSON. Analysis giữ đoạn dịch, từ ứng viên và grammar. Sửa text làm analysis mất hiệu lực; xóa reading không xóa thẻ đã học.

**Vocabulary:** một owner, một nghĩa, nhiều tags và một lịch ôn. Fingerprint từ word + meaning đã chuẩn hóa. Cùng từ có thể nhiều nghĩa. Các trường `reading/context/source_label` cũ vẫn là ngữ cảnh chính để tương thích.

**VocabularyOccurrence:** nhiều lần xuất hiện của cùng một nghĩa theo bài nguồn/ngữ cảnh. Lưu lại từ trùng nghĩa ở bài khác tạo occurrence mới nhưng không tạo thẻ mới và không đặt lại lịch ôn. Fingerprint occurrence ngăn ghi trùng cùng bài + nguồn + ngữ cảnh.

**ReviewLog:** lịch sử các lượt ôn, rating, mode, correct nếu trắc nghiệm, next_due. Unique owner+token chống tính hai lần khi browser retry.

**ExerciseAttempt:** câu hỏi do server sinh, đáp án lưu server, chưa trả đáp án ra client trước khi nộp. Đáp án lần đầu cố định; lần nộp lặp trả kết quả cũ. Câu hết hạn sau hai giờ. Không phải cơ chế chống gian lận cho kỳ thi: người học sở hữu dữ liệu và có thể xem kho từ.

**AICall:** task/model/status/timestamp, không lưu API key hay toàn prompt trong log bảng này. Giới hạn lượt/ngày không phải ngân sách USD tuyệt đối.

**LoginFailure:** key hash theo secret + địa chỉ kết nối, không lưu IP nguyên bản trong bảng này. Sau 10 lần sai trong 15 phút trả 429. Chưa phải rate limiter phân tán hoàn chỉnh cho public SaaS; reverse proxy có thể gom nhiều người vào cùng IP.

## Các route chính

```text
GET                 /api/bootstrap/
GET, POST           /api/readings/
GET, PATCH, DELETE  /api/readings/<uuid>/
POST                /api/readings/<uuid>/analyse/
GET, POST           /api/vocabulary/
GET                 /api/vocabulary/sources/
PATCH, DELETE       /api/vocabulary/<uuid>/
POST                /api/vocabulary/<uuid>/review/
GET                 /api/exercises/next/
POST                /api/exercises/<uuid>/answer/
POST                /api/prompts/
POST                /api/ai/lookup/
POST                /api/ai/words/
GET                 /api/backup/
GET                 /api/export.csv
POST                /api/restore/
GET                 /health/
```

`GET /api/readings/` nhận `q`, `status`, `favorite`, `sort`, `page`, `limit`. `status` là `all/completed/in_progress`; `favorite` là `all/yes/no`; `sort` là `updated/newest/oldest/title`. Kết quả chỉ gồm bài tự nhập của owner và trả `items`, `total`, `page`, `limit`.

`GET /api/vocabulary/` nhận `q`, `tag`, `scope`, `reading`, `sort`, `page`, `limit`. `scope` là `all/due/overdue/new/learning/mastered/weak/mistakes/unchecked`; `sort` là `due/newest/oldest/word`. `new` dùng `last_reviewed IS NULL`; `learning` dùng `last_reviewed IS NOT NULL` và `interval_days < 21`; `mastered` dùng `interval_days >= 21`; `weak` dùng `lapses >= 3`. Lọc `reading` kiểm tra cả ngữ cảnh chính và `VocabularyOccurrence`. API giới hạn một lần đọc 500 thẻ; exercise lấy tối đa 1.000 thẻ từ tập lọc.

Backup v4 gồm counts, occurrences, định danh import riêng và lượt TOEIC được chấm lại từ dữ liệu nguồn khi khôi phục. Hai bài riêng có cùng tiêu đề/nội dung vẫn được giữ tách biệt; import cùng một backup lần nữa là idempotent. File backup do ứng dụng phát hành bị giới hạn 8 MB giống đường restore để không tạo ra file mà chính ứng dụng không thể đọc lại. Kho lớn hơn phải backup PostgreSQL.

Một request ôn thẻ:

```json
{"rating":"good","token":"0dcc6220-939b-4bac-b67b-8c4d3dc110da"}
```

Chỉ client sinh token; lịch tiếp theo server tính. Chưa có FSRS. Quên: 10 phút; Nhớ: lần đầu 1 ngày, tiếp theo 3 ngày, sau đó nhân ease; Khó và Dễ dùng các hệ số minh bạch trong `schedule()`. UI ưu tiên `due_at` cũ hơn khi ôn đến hạn/quá hạn và đưa thẻ **Quên** gặp lại trễ hơn trong cùng lượt, tối đa một lần; đây là hành vi hàng đợi client, còn lịch chính vẫn do server lưu. Bootstrap trả mục tiêu ngày, tiến độ hôm nay, streak và các bucket mới/đang học/đã ghi nhớ/quá hạn. Không bảo đảm xác suất ghi nhớ hoặc tăng band.

## Hợp đồng AI

Structured Outputs giúp ràng buộc JSON, không tự đảm bảo kiến thức đúng. Backend vẫn validate schema; mọi bản dịch cần đủ chỉ số; vocabulary.context và grammar.evidence phải là trích đoạn có thực. Gợi ý không khớp bị loại. Người học duyệt nghĩa/synonyms trước hoặc sau khi lưu, không gắn verified tự động.

Không dùng output AI trực tiếp làm HTML. Trường văn bản được escape trước render. Không thực thi code do AI sinh. Không đưa tool credentials cho model. Passage được đặt trong khối DATA và developer instruction không cho thực hiện lệnh ẩn trong passage. Những biện pháp này giảm rủi ro, không phải chứng nhận tuyệt đối về prompt injection.

Adapter hiện hỗ trợ **OpenAI Responses API**. Muốn Gemini, Ollama hoặc nhà cung cấp khác, viết adapter trả cùng schema, xử lý response/error/refusal theo API của họ; không chỉ thay API URL. Chưa có Gemini/Ollama adapter trong gói này. Model mới cần test lại strict schema, độ dài output, unicode, billing và grounding.

## Ưu tiên mở rộng sau khi bản local ổn định

1. **Độ tin cậy:** chạy integration/migration checks; đóng băng dependency đã kiểm thử; thêm test API mock, concurrent review và backup restore đầy đủ; hardened PDF worker riêng nếu mở public.
2. **Dữ liệu tốt hơn:** đã có occurrence nhiều bài/ngữ cảnh; bước sau có thể tách sâu Lexeme/Sense, thêm paragraph index và ghi chú riêng cho từng occurrence.
3. **Lịch ôn nâng cao:** adapter FSRS với phiên bản có nguồn chính thức, migration cho trạng thái và đánh giá trên lịch sử thật. Không gọi scheduler hiện tại là FSRS.
4. **Bài dài / nhiều người:** hàng đợi phân tích, progress state, retry có idempotency, token budget; index/search/pagination phù hợp; không chạy request AI 150 giây trên nhiều web worker bị chiếm.
5. **Trải nghiệm:** audio/dictionary adapter có giấy phép; quiz ngữ nghĩa kiểm định tốt hơn, không ghép arbitrary synonym; OCR tùy chọn với duyệt text; đồng bộ và quản lý thiết bị sau khi có auth/deployment vững.

Đây là lộ trình, **không phải danh sách chức năng đã làm**. Không cần triển khai toàn bộ để bắt đầu học hằng ngày.

## Ranh giới production

`compose.yml` dành cho máy cá nhân, bind `127.0.0.1:8000`; database không publish port trừ override dev. `compose.prod.yml` bổ sung Caddy trên 80/443, ép cấu hình Django HTTPS/host/origin, HSTS khởi đầu và giữ Gunicorn/PostgreSQL sau mạng Compose. Quy trình VPS, backup/restore và cập nhật nằm trong `docs/DEPLOYMENT.md`.

Production overlay đặt DEBUG=false, domain/CSRF origin cụ thể, HTTPS cookies và chỉ tin header proxy khi dùng Caddy đi kèm. HSTS mặc định 1 giờ để kiểm tra ban đầu; chỉ tăng hoặc bật includeSubDomains/preload khi toàn bộ HTTPS đã ổn định. Vẫn cần secrets riêng, firewall, ngân sách/quota, logs không lộ nội dung riêng và backup đã thử khôi phục. Deployment checklist là chuẩn đối chiếu, không phải project tự chứng nhận production.

## Dựng lại bản HTML sau khi sửa giao diện

Sau khi cài requirements, chạy `python scripts/build_preview.py`. Script ghép template, CSS, JS và seed thành `preview.html` độc lập. File nguồn Django không cần build bằng Node. Dựng lại HTML không tự xóa localStorage hiện có; export backup trước khi thay dữ liệu/phiên bản.
