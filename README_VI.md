# LexiRead Reading Studio v2 — Đọc tiếng Anh & học từ vựng

**Đọc bài → hiểu nghĩa trong ngữ cảnh → chọn từ → lưu một lần → ôn nhiều cách.**

**Cập nhật 26/10/2026:** [học từ theo 15 chủ đề và từ điển lưu trong database](docs/LOCAL_VOCABULARY.md), gồm 127.311 mục từ, 27.581 mục có IPA và 197 bản thu tải sẵn. Có lật thẻ, luyện câu hỏi, lưu từng từ để ôn và tra ngay khi bôi đen; các luồng này không gọi AI. Quy mô nội dung và kiểm thử mới nhất nằm trong [README](README.md); các con số ở phần giới thiệu bản v2 bên dưới mô tả phiên bản ban đầu.

**Học ngữ pháp:** 36 bài và 216 câu bài tập; 16 bài A1–A2 có giải thích bằng tiếng Việt, ví dụ từng bước, câu tự luyện và phần ghi nhớ. Mở `/#learn/grammar` để học ngay trên website. Nội dung có sẵn, không gọi AI.

Bộ mã nguồn dành cho Huỳnh Bảo Quyên. Dự án riêng, không sửa hoặc kết nối cơ sở dữ liệu SmartEnglish hiện có.

## Bản 2: đọc hiểu, TOEIC và ôn từ trong một luồng


Giao diện chính chọn Việt (mặc định), Anh, Pháp, Trung giản thể. Giữ nguyên bài tiếng Anh và giải nghĩa Việt; một số nhãn cũ vẫn tiếng Việt. Xem [quy trình nội dung](docs/LESSON_AUTHORING.md) và [kiểm thử cập nhật](docs/EDITORIAL_UPDATE_QA.md).

Xem **[Hướng dẫn nâng cấp v2](docs/READING_STUDIO_V2.md)** trước khi thay code; giữ `.env`, database/volume và tiến độ. [Thêm nội dung](docs/LESSON_AUTHORING.md). Không có chứng nhận level hoặc đề IELTS/ETS chính thức.

Muốn lưu mã nguồn lên GitHub: đọc **[Hướng dẫn đưa LexiRead lên GitHub](docs/GITHUB_UPLOAD.md)** trước khi chạy `git add`. Luôn kiểm tra `git status`, xác nhận `.env` bị ignore và xem lại dữ liệu học cá nhân trước khi công khai.

## 1. Bắt đầu từ đâu?

**Học ngay:** mở `preview.html` bằng Chrome/Edge. Có 27 bài đi kèm, 116 thẻ và bài Set in Metal. Đây là localStorage, không phải PostgreSQL; không chứa 60 bài nháp mới hoặc đồng bộ với admin. Xuất backup định kỳ và tránh cửa sổ riêng tư.

**Muốn website đầy đủ, mở rộng bằng code:** dùng Django + PostgreSQL theo phần 3. Dữ liệu học từ HTML có thể xuất JSON và nhập vào bản Django. Không cần Node.js, npm hay React để chạy phiên bản này.

**Tình trạng kiểm thử ngày 22/10/2026:** bộ pure Python chạy 81 test, gồm 80 PASS và 1 test tạo PDF bằng reportlab được skip vì dependency này là tùy chọn. 56 kiểm tra DOM/luồng preview PASS. Docker Compose chạy healthy, migrations đến `0006_daily_visit` đã áp dụng, Django `check` PASS và 43/43 integration tests trên PostgreSQL PASS. Landing page, form email và responsive mobile đã được kiểm tra bằng Chromium. Cấu hình production/Caddy đã qua `check --deploy` với hai cảnh báo HSTS chủ đích được giải thích trong hướng dẫn và Caddyfile đã validate bằng domain mẫu; chưa triển khai lên domain thật, gọi OpenAI API thật hoặc thử restore PostgreSQL production. Chi tiết xem `docs/TEST_REPORT.md`.

## 2. Chức năng và phạm vi

| Chức năng | Django + PostgreSQL | HTML độc lập |
|---|---|---|
| Thư viện 27 bài đi kèm, lọc chủ đề/mức/trạng thái | Có, admin import/publish + seed ban đầu | Có sẵn |
| TOEIC Reading: 2 lựa chọn, 24 câu, giải thích, lưu lượt làm | Có, theo tài khoản | Có, trong trình duyệt |
| Thống kê truy cập first-party, không lưu IP | Có, admin xem tổng | Không gửi dữ liệu ra ngoài |
| Câu hiểu bài/đáp án/bằng chứng cố định | Có | Có |
| Dấu trang, hoàn thành, điểm riêng | Có | Có |
| Giải đáp sẵn; hỏi thêm theo nguồn bài | Có | Có, câu mới qua JSON |
| Kho 116 thẻ/nghĩa ban đầu | Nạp bằng `seed_demo` | Có sẵn |
| Thêm/sửa/xóa bài tự nhập, từ, nghĩa, tags | Có | Có |
| Tìm/lọc/yêu thích/sắp xếp/phân trang bài đã lưu | Có | Có |
| Tìm/lọc kho từ theo tag, bài nguồn, trạng thái; sắp xếp | Có | Có |
| Một nghĩa lưu nhiều bài/ngữ cảnh xuất hiện | Có | Có |
| Dán bài; nhập TXT/MD | Có | Có |
| Nhập DOCX/PDF có lớp chữ | Có, giới hạn bên dưới | Không |
| Bản dịch song ngữ theo đoạn | Có | Có |
| Gọi OpenAI API trực tiếp qua backend | Có, cần cấu hình | Không |
| Copy prompt / dán kết quả JSON | Có | Có |
| Bôi đen từ trong đoạn tiếng Anh | Có | Có |
| Từ gợi ý và cấu trúc, trích đoạn gốc | Có | Có |
| Flashcard, ABCD, synonym, paraphrase, điền từ, gõ từ | Có | Có |
| Lịch ôn, mục tiêu ngày, streak, nhóm tiến độ và từ từng trả lời sai | Có | Có |
| Landing page công khai; đăng nhập email; dữ liệu tách theo tài khoản | Có | Không |
| Lưu chính | PostgreSQL | localStorage |
| Backup/khôi phục JSON | Có | Có |
| Xuất CSV | Có | Có |
| Nhập CSV | Có | Không; dùng JSON |

116 là số **thẻ theo nghĩa**, không phải 116 từ gốc khác nhau. Chẳng hạn `commission` có thẻ động từ “đặt làm” và thẻ danh từ “tiền hoa hồng”. Bộ “Từ cá nhân” gồm 41 thẻ, tính cả apprenticeship đã có trong bộ cũ. Danh sách đã sửa lỗi chính tả, nhưng không gắn nhãn “đã được từ điển xác minh” cho mọi thẻ. Bạn có thể duyệt/chỉnh nội dung trong editor.

## 3. Cài trên Windows — cách dùng Docker

### 3.1. Cài một lần

Cài **Docker Desktop**, chọn backend WSL 2 và dùng Linux containers. Mở Docker Desktop sau khi cài. Yêu cầu hệ điều hành, RAM và WSL xem tài liệu chính thức trong `docs/SOURCES.md` (mục Docker), không tắt kiểm tra bảo mật để ép cài trên hệ điều hành không được hỗ trợ.

Kiểm tra PowerShell:

```powershell
wsl --version
docker --version
docker compose version
docker info
```

Nếu thiếu WSL, làm theo hướng dẫn Docker/Microsoft; thao tác bật WSL có thể cần PowerShell quyền quản trị và khởi động lại. Máy đã chạy Docker bình thường thì không cần cài PostgreSQL hoặc Python riêng cho cách này.

### 3.2. Giải nén

Giải nén sao cho file `manage.py`, `compose.yml`, `setup.ps1` nằm trực tiếp trong:

```text
D:\projects\LexiRead
```

Thư mục có thể khác; đổi lệnh `cd` tương ứng. Không giải nén đè lên SmartEnglish hoặc project đang dùng.

### 3.3. Khởi động

Mở terminal PowerShell của VS Code trong thư mục dự án:

```powershell
cd D:\projects\LexiRead
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
docker compose ps
```

Cờ `ExecutionPolicy Bypass` ở đây chỉ áp dụng cho tiến trình PowerShell chạy script này, không yêu cầu đổi policy toàn máy. Có thể đọc `setup.ps1` trước khi chạy.

Script tạo `.env` từ mẫu, sinh secret và mật khẩu database ngẫu nhiên, giữ cấu hình hiện có nếu đã chạy trước đó. Sau đó build web và tạo database PostgreSQL riêng. Lần build đầu cần Internet để tải image và thư viện. Chờ `web` và `db` báo hoạt động/healthy trước bước tiếp theo.

Không chạy `docker compose exec web ...` khi `docker compose up` chưa thành công: `exec` chỉ chạy lệnh bên trong một container đang hoạt động. Nếu thấy `env file ... .env not found`, chạy đúng thứ tự phục hồi sau:

```powershell
cd D:\LexiRead
python .\scripts\init_env.py
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose exec web python manage.py showmigrations learning
docker compose exec web python manage.py check
```

Ý nghĩa: `init_env.py` tạo `.env` với secret ngẫu nhiên; `config --quiet` kiểm tra Compose; `up --build -d` build và chạy nền; `ps` xem health; hai lệnh `exec` cuối xác nhận migration và cấu hình Django. Cách gọn hơn là chạy lại `powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1`, vì script thực hiện các bước tạo `.env` và khởi động thay bạn.

### 3.4. Tạo tài khoản và nạp kho cá nhân

```powershell
docker compose exec web python manage.py createsuperuser
```

Nhập username nội bộ, **email duy nhất** và mật khẩu mạnh. Khi gõ mật khẩu trong terminal thường không có ký tự hiện ra. Giao diện website đăng nhập bằng email, không dùng username. Nếu muốn nạp dữ liệu demo, thay đúng email ở lệnh sau:

```powershell
docker compose exec web python manage.py seed_demo --email ban@example.com
```

Entry point đã nạp thư viện dùng chung bằng `seed_lessons`. Lệnh `seed_demo` ở trên là tùy chọn: nạp bài Set in Metal + 116 thẻ vào riêng tài khoản. Chạy lại không xóa từ mới, không đặt lại lịch ôn và không ghi đè nghĩa đã có cùng fingerprint. Nếu muốn học từ kho trống, bỏ qua lệnh seed.

Mở trình duyệt. Khi chưa đăng nhập, trang đầu hiển thị danh sách bài đọc, hai hướng TOEIC và các chức năng để người dùng xem trước. Mở bài hoặc bắt đầu học sẽ chuyển sang đăng nhập; API học tập vẫn trả `401` nếu chưa xác thực:

```text
http://localhost:8000
```

Trang quản trị:

```text
http://localhost:8000/admin/
```

Không có public signup. Quản trị viên có thể tạo tài khoản thường trong trang admin và phải nhập email riêng, không trùng tài khoản khác. **Admin có quyền xem dữ liệu quản trị của các tài khoản**; tách dữ liệu owner áp dụng cho giao diện/API học của người dùng. Không cấp quyền staff/superuser cho người dùng chỉ cần học.

### 3.5. Triển khai lên Internet

Không đổi cổng `8000` thành public. Nếu muốn chạy miễn phí, dùng **[Render Free + Neon Free](docs/DEPLOY_FREE.md)**. Nếu dùng VPS riêng, dùng overlay `compose.prod.yml` và đọc toàn bộ **[hướng dẫn VPS + domain + HTTPS](docs/DEPLOYMENT.md)**. Các cấu hình này phù hợp website cá nhân/closed beta; chưa nên mở đăng ký công khai khi chưa có xác minh email, quên mật khẩu, rate limit ở biên và kiểm thử tải.

## 4. Một buổi học trên LexiRead

### 4.0. Luyện TOEIC Reading

Vào **Luyện TOEIC Reading** và chọn một trong hai hướng. **Ngữ pháp & từ vựng** luyện Part 5–6; **Đọc hiểu** luyện Part 7 với email, thông báo, bài đơn và bài kép. Làm đủ câu rồi nộp để xem đáp án, giải thích và bằng chứng. Lượt làm, điểm gần nhất và điểm tốt nhất được lưu riêng theo tài khoản.

Nút **Lưu từ trọng tâm** đưa từ của bộ luyện vào kho chung với tag TOEIC. Từ đó có thể ôn bằng flashcard, ABCD, synonym, paraphrase, cloze hoặc gõ từ theo cùng lịch chống quên. Các bộ luyện là nội dung gốc mô phỏng dạng bài, không phải đề ETS và không dùng để quy đổi điểm TOEIC.

### 4.1. Nhập một passage

Vào **Bài đọc của tôi → Thêm bài đọc**. Điền tiêu đề, dán tiếng Anh hoặc chọn file. Để một dòng trống giữa hai đoạn. Nếu vừa dán text vừa chọn file, app hỏi xác nhận rồi ưu tiên file.

Danh sách bài đã lưu có tìm kiếm theo tiêu đề, tên nguồn hoặc nội dung; lọc **mọi tiến độ / đang đọc / đã đọc** và **tất cả / chỉ yêu thích / chưa yêu thích**; sắp xếp theo cập nhật, ngày thêm hoặc tiêu đề; mỗi trang hiển thị một phần kết quả. Nút ngôi sao lưu trạng thái yêu thích vào tiến độ riêng của tài khoản. Thư viện bài biên soạn sẵn cũng hiển thị và lọc được bài yêu thích.

Giới hạn hiện tại: file tối đa 8 MB, PDF tối đa 30 trang, bài tối đa 60.000 ký tự. PDF cần có lớp chữ. PDF ảnh scan chưa hỗ trợ OCR. DOCX và PDF nhiều cột có thể làm thứ tự đoạn không như mong muốn; đọc kiểm tra rồi dùng **Sửa bài**. Chỉ lưu text đã trích xuất; không lưu bản upload gốc.

Không dán đề và answer key chung vào passage. Thư viện hỗ trợ trắc nghiệm, TFNG/YNNG, ghép tiêu đề/thông tin, điền từ/trả lời ngắn; chưa phải full mock hoặc mọi dạng IELTS. Bài cá nhân tự nhập tập trung đọc, dịch, lưu từ và hỏi đáp.

### 4.2. Dịch và gợi ý — không API

Trong bài đọc, chọn **Copy prompt / Dán JSON**. Sao chép prompt có sẵn, dán vào công cụ AI bạn đang dùng, lấy kết quả JSON và dán lại. Bấm **Nhập kết quả JSON**.

App tự đưa bản dịch vào đúng đoạn, hiển thị từ gợi ý và cấu trúc. Bạn không cần tự tạo từng flashcard. Khi dán sang AI, chính bạn đang gửi bài đọc sang dịch vụ đó; chỉ dùng nội dung bạn có quyền sử dụng/chia sẻ.

Kết quả phải có `translations`, `vocabulary`, `grammar` đúng schema trong prompt. Nếu AI giải thích thêm bên ngoài JSON, chỉ lấy khối JSON. App yêu cầu đầy đủ các đoạn dịch và loại từ/cấu trúc có trích dẫn không khớp nguồn. Kiểm tra cấu trúc/trích đoạn **không chứng minh bản dịch hay synonym chắc chắn đúng**.

### 4.3. Dịch bằng API

Khi đã bật API theo phần 5, chọn **Dịch & gợi ý bằng AI** và xác nhận gửi bài. App gọi backend; backend gọi provider rồi trả kết quả. Mỗi lần xử lý tối đa 16.000 ký tự. Bài dài hơn nên tách phần có tiêu đề rõ.

Đây là một request đồng bộ, chưa có hàng đợi Celery/Redis. Không gửi liên tục nếu app đang chờ. Nếu lỗi hoặc hết thời gian, kiểm tra thông báo và hạn mức trước khi gọi lại.

### 4.4. Chọn từ cần học

Trong đoạn tiếng Anh, bôi đen từ hoặc cụm từ trong cùng một đoạn, chọn lưu từ. Editor giữ ngữ cảnh gốc. Bấm **AI gợi ý nghĩa** hoặc **Copy prompt / Dán JSON** để điền nghĩa, synonym, paraphrase. Bạn cũng có thể tự điền.

Trong tab **Từ gợi ý**, tick các mục cần học, chọn **Lưu mục đã chọn**. Muốn sửa chi tiết, vào **Kho từ của tôi → Sửa**. AI không tự xác nhận thẻ là “đã duyệt”.

Trong **Kho từ của tôi**, có thể tìm theo từ, nghĩa, ghi chú, nguồn, ngữ cảnh hoặc ví dụ; lọc theo tag, bài nguồn và trạng thái học; sắp xếp theo ngày thêm, từ A–Z hoặc lịch ôn gần nhất; rồi chuyển trang. Các phạm vi gồm: **Tất cả, Đến hạn, Đã quá hạn, Từ mới, Đang học, Đã ghi nhớ tốt, Từ khó, Từng trả lời sai, Chưa xác nhận nghĩa**. “Từ mới” là thẻ chưa từng ôn (`last_reviewed` chưa có); “Đang học” là thẻ đã ôn có khoảng cách dưới 21 ngày; “Đã ghi nhớ tốt” là thẻ có khoảng cách từ 21 ngày trở lên; “Từ khó” là thẻ đã được đánh giá Quên từ 3 lần.

Một nghĩa trùng đã có không bị tạo thêm thẻ hoặc đặt lại lịch ôn. Thay vào đó, app ghi thêm một **lần xuất hiện** gồm bài nguồn và ngữ cảnh. Vì vậy cùng một nghĩa có thể được tìm thấy khi lọc theo nhiều bài khác nhau mà vẫn dùng chung một lịch ôn.

Một thẻ có: word, part of speech, meaning_vi, synonyms, paraphrases, original context, short example, example translation, note, tags, origin, verified flag, reading link và lịch ôn.

Không bắt buộc viết ví dụ. Flashcard/ABCD nhớ nghĩa vẫn dùng được. Dạng điền từ cần câu có chứa chính xác từ đã lưu; app không ép dùng một câu thiếu từ để tạo bài.

### 4.5. Đưa thêm danh sách từ cá nhân

Vào **Kho từ → Nhập nhiều từ**. Có ba cách:

- Dán danh sách thô, mỗi dòng một từ, chọn AI điền nghĩa hoặc copy prompt. Prompt yêu cầu sửa typo, giải thích dấu `=` không chính xác và chọn nghĩa phổ biến khi thiếu ngữ cảnh.
- Đã có nghĩa: dùng `word | nghĩa Việt | synonym 1; synonym 2`, chọn **Đọc dòng có sẵn nghĩa**, duyệt rồi lưu.
- Import JSON/CSV tại **Cài đặt & dữ liệu**. Xem `data/import_example.json`, `data/import_example.csv`.

Ví dụ nhập nhanh:

```text
pertinent | liên quan trực tiếp | relevant; applicable
aptitude | năng khiếu, khả năng tự nhiên | talent; ability
untapped | chưa được khai thác | unexploited; unused
```

Đây là định dạng dòng nhập nhanh. Trong **CSV**, nhiều giá trị bên trong cùng một ô dùng dấu `|`, không dùng dấu `;` như ô nhập nhanh bên trên.

### 4.6. Ôn tập

Có bảy chế độ: flashcard; ABCD Anh→Việt; ABCD Việt→Anh; chọn synonym; nhận diện paraphrase; điền từ trong câu; gõ từ tiếng Anh. Chọn bộ từ/tag, phạm vi và số thẻ rồi bắt đầu.

Trang Tổng quan và Luyện nhớ hiển thị mục tiêu 20 lượt/ngày, số lượt hôm nay, streak ngày ôn liên tiếp và các nhóm **Từ mới / Đang học / Đã ghi nhớ tốt / Đã quá hạn**. Khi ôn phạm vi đến hạn hoặc quá hạn, thẻ có lịch cũ hơn được đưa lên trước.

Flashcard: lật xem nghĩa, tự đánh giá **Quên / Khó / Nhớ / Dễ**. Phím Space lật thẻ; phím 1–4 chọn mức sau khi lật. Chọn **Quên** đặt lịch gần 10 phút và đưa thẻ gặp lại sau một số thẻ khác trong cùng lượt, tối đa một lần để tránh vòng lặp vô hạn. Nếu lượt quá ngắn, thẻ sẽ trở lại gần cuối hàng đợi hiện có. Trắc nghiệm có thể dùng A–D. Mỗi câu đã nộp chỉ tính lịch ôn một lần.

Bài luyện dựng từ nghĩa/synonym/paraphrase bạn lưu, không phải đề IELTS chính thức. App loại lựa chọn trùng và một số nhóm synonym chồng lấn, nhưng chưa bảo đảm mọi distractor đều khác nghĩa về mặt ngữ nghĩa. Thấy hai lựa chọn cùng hợp lý thì sửa thẻ, không học thuộc một câu chấm máy móc.

### 4.7. Thống kê và tạo động lực

Trang Tổng quan hiển thị thêm **số ngày học trong 30 ngày**, **lượt mở khu học hôm nay** và **số lượt luyện TOEIC/điểm tốt nhất** của chính tài khoản. Đây là chỉ số tiến bộ thật, không dùng số người học giả để tạo cảm giác đông người.

Tài khoản staff/superuser có mục **Thống kê truy cập** trong menu. Có thể chọn 7/30/90 ngày để xem lượt xem, khách duy nhất ước lượng, tài khoản hoạt động, lượt/khách, biểu đồ ngày và trang được xem nhiều. Hệ thống không lưu IP và không tải Google Analytics hay script theo dõi bên thứ ba; một mã phiên ngẫu nhiên được băm dùng để tránh đếm một phiên thành nhiều khách trong cùng ngày. Số liệu này là analytics ứng dụng, không nằm trong backup dữ liệu học v4.

## 5. Bật AI — tùy chọn

Mở `.env` và chỉnh:

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=YOUR_PRIVATE_API_KEY
OPENAI_MODEL=gpt-4.1-mini
AI_DAILY_LIMIT=30
```

Sau đó:

```powershell
docker compose up -d --force-recreate web
```

Key cần quyền dùng model và tài khoản API cần hạn mức phù hợp. Model có thể thay, nhưng phải hỗ trợ Responses API + Structured Outputs với JSON schema dùng trong `learning/services/ai.py`. Không phải đổi tên model nào cũng chạy. Tên model mặc định không có nghĩa đây luôn là lựa chọn mới nhất/rẻ nhất.

**API tính phí riêng với gói ChatGPT.** Không dán session/cookie ChatGPT vào app, không dùng API key của người khác. Chưa muốn trả phí API thì giữ `AI_PROVIDER=none` và dùng luồng copy prompt.

Ứng dụng giới hạn số lượt gọi theo người dùng/ngày và khoảng cách tối thiểu giữa hai lượt. Đây **không phải trần chi phí tiền tuyệt đối**: giá còn phụ thuộc token, model, số tài khoản và chính sách provider. Đặt cảnh báo/ngân sách phía API nếu có.

API key chỉ đọc trong backend; `.env` nằm trong `.gitignore` và `.dockerignore`. Không commit/share `.env`, không đặt key vào `app.js`. Bật AI chỉ gửi nội dung sau thao tác xác nhận: phân tích bài gửi bài đó; tra từ gửi từ và đoạn ngữ cảnh.

Request đặt `store=false`, nhưng không được hiểu là cam kết toàn bộ hệ thống của nhà cung cấp không lưu bất kỳ dữ liệu nào. Xem chính sách dữ liệu của provider trước khi đưa tài liệu nhạy cảm lên.

## 6. Chạy Python trực tiếp để chỉnh code

Cách này dành cho môi trường phát triển. Có thể dùng Python 3.12 hoặc 3.13. Dockerfile đã chọn Python 3.12. Chạy PostgreSQL bằng Compose riêng, web chạy trong venv:

```powershell
cd D:\projects\LexiRead
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\init_env.py

docker compose -f compose.yml -f compose.dev.yml up -d db
```

Nếu chỉ có Python 3.13 thì đổi lệnh tạo venv sang `py -3.13`. Cách dùng đường dẫn interpreter trực tiếp không cần thay execution policy để activate venv.

`.env` cho web chạy trên máy:

```dotenv
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=15432
DJANGO_DEBUG=true
```

Mật khẩu phải khớp `.env` đã dùng để tạo container database. Các lệnh tiếp:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_lessons
.\.venv\Scripts\python.exe manage.py seed_toeic
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_demo --email ban@example.com
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Nếu container web đang giữ cổng 8000, chạy `docker compose stop web` trước. `runserver` chỉ dùng phát triển, không phục vụ Internet công khai. Gunicorn nằm trong Docker Linux; không chạy Gunicorn trực tiếp trên Windows.

## 7. Backup, khôi phục và bảo trì

**Cách thường dùng:** Cài đặt & dữ liệu → Backup JSON. Backup v4 chứa bài, snapshot bài cố định, các lượt làm câu hỏi và hỏi đáp của văn bản hiện tại, thẻ, toàn bộ lần xuất hiện theo bài/ngữ cảnh, lịch sử/lịch ôn và lượt TOEIC; không chứa tài khoản, password hash, API key hoặc cookie. V4 vẫn đọc backup v1/v2/v3. Ứng dụng chỉ phát hành file backup không quá 8 MB để bảo đảm chính file đó có thể nhập lại; kho lớn hơn cần backup PostgreSQL bằng `pg_dump`. JSON có thể chứa nội dung cá nhân, nên bảo quản như dữ liệu riêng.

**Chuyển HTML sang PostgreSQL:** xuất JSON từ bản HTML, đăng nhập bản Django, import file. Khôi phục theo kiểu gộp: nghĩa đã tồn tại giữ nguyên tiến độ hiện tại, không tự ghi đè. Do đó muốn nhập chính xác toàn bộ tiến độ mới từ HTML, hãy dùng tài khoản/kho trống trước khi chạy seed; nếu đã seed hoặc có thẻ trùng, tiến độ của thẻ đó được giữ theo bản đang có. Đây là lựa chọn chống mất dữ liệu, không phải đồng bộ hai chiều.

CSV chỉ phù hợp chuyển nội dung thẻ; không mang đủ tiến độ/lịch sử/nguồn như JSON. Với kho rất lớn, backup JSON có thể vượt giới hạn import 8 MB; khi đó dùng backup PostgreSQL, hoặc mở rộng importer theo hướng streaming/batch.

Volume PostgreSQL vẫn tồn tại khi dừng/restart container. **Không dùng `docker compose down -v` trừ khi chủ động muốn xóa database volume.** JSON ứng dụng không thay cho backup database đầy đủ khi cần giữ tài khoản/quyền và toàn bộ trạng thái hệ thống.

Các lệnh thường dùng:

```powershell
docker compose stop
docker compose start
docker compose logs --tail=100 web
docker compose logs --tail=100 db
# Sau khi sửa code:
docker compose up --build -d
# Sau khi chỉ sửa .env của web:
docker compose up -d --force-recreate web
# Dọn log cũ, sau khi đọc help:
docker compose exec web python manage.py prune_logs --help
docker compose exec web python manage.py prune_logs
```

Lệnh `prune_logs` giữ nguyên lịch sử ôn từ, nhưng dọn log đăng nhập, lượt tạo bài tập, lời gọi AI hết hạn và thống kê truy cập cũ hơn 400 ngày. Có thể chạy định kỳ mỗi tuần hoặc mỗi tháng.

Thay `POSTGRES_PASSWORD` trong `.env` sau khi database đã được khởi tạo **không tự đổi mật khẩu role trong PostgreSQL**. Cần đổi role đúng cách và cập nhật cấu hình đồng bộ; đừng xóa volume để “sửa” lỗi đăng nhập khi đang có dữ liệu.

## 8. Kiểm thử trên máy bạn

```powershell
# Kiểm tra cấu hình và migrations (không tạo thay đổi mới):
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
# Python tests không cần database:
docker compose exec web python -m unittest discover -s tests -v
# Integration: Django tạo test database riêng, cần quyền CREATEDB:
docker compose exec web python manage.py test learning -v 2
```

Integration tests không gọi AI thật. PostgreSQL role do image Docker tạo trong cấu hình phát triển thường có quyền tạo test database; khi dùng role hạn quyền, cấp quyền phù hợp cho môi trường test, không nâng quyền tùy tiện trên production.

Kết quả kèm gói: bộ pure Python chạy 81 test, gồm 80 PASS và 1 test tạo PDF dùng reportlab được skip; runtime không dùng reportlab. Browser test ở `scripts/test_platform_preview.py` cần Playwright và Chromium riêng; 56 checks đã PASS. Bộ browser dùng Storage test double, không phải kiểm tra đóng/mở trình duyệt với localStorage thật. Docker Compose chạy healthy; Django `check`, migrations đến `0006_daily_visit` và 43/43 integration tests PostgreSQL đã PASS. Landing page, form đăng nhập email và responsive mobile cũng đã qua Chromium smoke test.

## 9. Lỗi thường gặp

**Docker chưa chạy:** mở Docker Desktop, kiểm tra `docker info`, rồi chạy lại setup.

**Thiếu `.env` / biến PostgreSQL rỗng:** chưa chạy bước tạo cấu hình. Dùng `powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1`. Nếu chỉ muốn sửa tại chỗ, dùng chuỗi lệnh phục hồi ở mục 3.3. Không tự điền password rỗng và không commit `.env`.

**Cổng 8000 bận:** dừng ứng dụng đang chiếm cổng hoặc đổi mapping thành `127.0.0.1:8001:8000` trong compose rồi truy cập cổng 8001.

**Web restart liên tục:** xem `docker compose logs --tail=100 web`. Thường cần kiểm tra database/password, dependency install hoặc biến `.env`; không gửi secret lên chat.

**Không thấy trang style:** chạy collectstatic; với Docker đọc log bước này, rebuild sau khi sửa frontend.

**Không thấy kho từ:** kiểm tra email trong lệnh seed và tài khoản đang đăng nhập. API không chia sẻ kho giữa hai người dùng.

**Không gọi được AI:** chưa bật provider, key sai, model không được phép, hạn mức API, hoặc mạng. Luồng copy prompt vẫn dùng được. Không retry liên tục khi 429.

**JSON thiếu đoạn:** prompt yêu cầu đủ `index` từ 0; kiểm tra AI có cắt ngắn kết quả không. Bài quá dài nên chia phần. Không nhập một bản dịch thiếu đoạn như thể đã hoàn tất.

**PDF scan:** chưa có OCR; dùng bản có chữ hoặc tự đưa text đã nhận dạng vào ô dán.

**Import trùng không tăng từ:** chủ đích; cùng `word + meaning_vi` chuẩn hóa là cùng một thẻ. Một nghĩa khác của cùng từ sẽ là thẻ khác.

**Chưa đủ ABCD:** cần tối thiểu bốn nghĩa khác nhau trong tập đang lọc. Có thể chuyển phạm vi “Tất cả từ”, thêm thẻ hoặc dùng flashcard/gõ từ. Dạng cloze cần câu chứa đúng từ gốc, không tự chuyển lemma/thì.

**Build lỗi SSL/download:** kiểm tra mạng, proxy và chứng chỉ công ty theo cấu hình chính thống. Không vô hiệu hóa xác minh TLS hoặc dùng mirror không tin cậy để lách lỗi.

## 10. Mở rộng dự án

Xem `docs/ARCHITECTURE.md`: vị trí code, API contract, chỗ thay model/provider và các việc chưa triển khai. Giao diện ưu tiên HTML/CSS/JS đơn giản để bạn thay trực tiếp. Không bắt đầu bằng việc viết lại toàn bộ thành microservices.

Base Compose chỉ bind localhost. Overlay production đã có Caddy/HTTPS, cookie an toàn, host/origin cụ thể, HSTS khởi đầu và dependency lock; xem `docs/DEPLOYMENT.md`. Trước khi mời người thật vẫn phải chạy trên domain thật, thử backup/restore, cấu hình firewall/giám sát và đánh giá tải. Không mở cổng database hoặc Gunicorn trực tiếp ra Internet.

**Nguồn tài liệu chính thức:** `docs/SOURCES.md`. **Lưu ý từ vựng:** `docs/VOCAB_NOTES.md`. **Kết quả kiểm thử thực tế:** `docs/TEST_REPORT.md`.
> Tài khoản mới: đăng ký bằng username, sửa hồ sơ, đổi mật khẩu và khôi phục qua email — xem [hướng dẫn cấu hình mail](docs/ACCOUNT_SETUP.md). Không bắt OTP; SMS chưa bật. Tính năng gửi mail thật cần cấu hình sender và API key trên máy chủ.

## Nội dung v3

Bản triển khai tự nạp 486 bài/phần Reading và 486 bộ từ theo ngữ cảnh bằng `seed_content_v3`. Gói được lưu gọn trong `data/content_packs/v3`; không cần ZIP hay thư mục v1. Nhập lại chỉ thêm mục chưa có, giữ nội dung đã biên tập và tiến độ cá nhân. Xem `docs/CONTENT_V3.md`.
