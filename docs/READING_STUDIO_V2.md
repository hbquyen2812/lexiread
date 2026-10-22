# LexiRead Reading Studio — bản 2

**Một website chuyên biệt cho đọc tiếng Anh và học từ theo ngữ cảnh.**

Đọc để hiểu → chọn điều cần học → lưu vào kho của mình → ôn lại qua nhiều dạng bài.
Bản này nâng cấp trực tiếp code LexiRead đã cung cấp, không yêu cầu tạo dự án khác hoặc chuyển sang React.

## 1. Hai luồng học, một kho từ cá nhân

| | Thư viện luyện đọc | Bài đọc của tôi |
|---|---|---|
| Nguồn | Bài biên soạn sẵn, nội dung cố định theo phiên bản | Nội dung do người học dán/nhập |
| Mục đích | Có bài để học hằng ngày, đa dạng chủ đề và mức khó | Học tài liệu, passage hoặc bài đang quan tâm |
| Bản dịch và từ gợi ý | Có sẵn, không cần gọi AI | Nhập kết quả AI hoặc tự điền |
| Bài tập hiểu bài | Câu hỏi, đáp án, lý do, bằng chứng cố định | Không tự gán một bài kiểm tra giả; tập trung hỏi đáp |
| Câu khó | Giải đáp soạn sẵn + hỏi thêm theo bài | Hỏi nghĩa, cấu trúc, đại từ, ý chính, paraphrase |
| Ai xem được? | Nội dung chuẩn dùng chung trong app | Riêng tài khoản người nhập trong giao diện/API học |
| Lưu từ | Chọn những từ cần học, không tự nạp tất cả | Chọn từ/cụm từ trong ngữ cảnh |

Bản Django tách dữ liệu người học theo owner. Quản trị viên hệ thống có quyền quản trị dữ liệu; đây không phải cơ chế mã hóa để giấu nội dung khỏi admin. Bản HTML không có tài khoản: dữ liệu ở trình duyệt hiện tại.

## 2. Bộ nội dung khởi đầu

12 bài nguyên gốc, tình huống hư cấu biên soạn cho ứng dụng. Không sao chép bài báo hay đề IELTS thương mại.
Mỗi bài khoảng **194–246 từ**, chia 4 đoạn, gồm:

- 4 bản dịch đoạn tiếng Việt, có thể ẩn/hiện.
- 6 từ/cụm gợi ý, nghĩa đúng ngữ cảnh, synonym/paraphrase và lưu vào kho cá nhân.
- 2 ghi chú cấu trúc, ví dụ ngắn kèm dịch.
- 4 câu hiểu bài: ý chính, chi tiết, True/False/Not Given, nghĩa từ; có đáp án, giải thích và trích đoạn.
- 2 phần giải đáp soạn sẵn dùng khi chưa bật API.

Tổng: **72 mục từ gợi ý, 48 câu hỏi, 24 ghi chú cấu trúc, 24 giải đáp sẵn**. Đây không phải 72 thẻ đã được tự thêm vào kho cá nhân. Bộ 116 thẻ cũ vẫn là dữ liệu tùy chọn riêng (`seed_demo`).

| Mức ước lượng | Tên bài | Chủ đề |
|---|---|---|
| A2 | A Quiet Start to the Day | Thói quen & đời sống |
| A2 | One Meal at a Time | Ẩm thực |
| A2 | The Balcony Garden | Thiên nhiên |
| A2 | An Afternoon without Photos | Sở thích & kết nối |
| B1 | The Book Exchange | Cộng đồng & văn hóa |
| B1 | The Repair Afternoon | Môi trường & đồ dùng |
| B1 | Learning in the Bicycle Shop | Nghề nghiệp |
| B1 | Room for a Change of Plan | Du lịch & trải nghiệm |
| B2 | The Useful Feature | Công nghệ & thiết kế |
| B2 | The Empty Shop | Không gian đô thị |
| B2 | Changing the Club Rules | Thể thao & tổ chức |
| B2 | A Slower Workshop | Nghệ thuật & kinh doanh |

**A2/B1/B2 là ước lượng của người biên soạn, chưa hiệu chuẩn CEFR.** Không quy điểm 4 câu thành band IELTS hoặc chứng nhận trình độ. Các câu có bằng chứng đúng nguyên văn vẫn cần duyệt về ngôn ngữ/sư phạm trước khi dùng cho lớp học hoặc xuất bản.

## 3. Giao diện và một buổi học

Menu: **Tổng quan → Thư viện luyện đọc → Bài đọc của tôi → Kho từ của tôi → Luyện nhớ từ → Cài đặt & dữ liệu.**

Vào thư viện, lọc mức khó/chủ đề/trạng thái/yêu thích. Mở một bài: ứng dụng tạo bản học riêng cho tài khoản để lưu dấu trang, trạng thái yêu thích, điểm và câu đã hỏi; không thay đổi nội dung chuẩn. Trong trang đọc có các tab **Bài đọc / Từ gợi ý / Cấu trúc / Hiểu bài / Hỏi đáp & giải thích**.

Có thể tắt bản dịch trước khi đọc, chọn cỡ chữ 17/19/22, đánh dấu đoạn đang đọc và chủ động đánh dấu hoàn thành. Xem bài không tự tăng số bài đã hoàn thành. Nút “Hiểu bài” yêu cầu trả lời đầy đủ rồi mới hiện đáp án và trích dẫn. Mỗi lượt nộp có token để tránh tính hai lần khi retry. Có thể làm lại; lưu điểm tốt nhất.

Bôi đen từ/cụm từ sẽ mở thanh chọn. Với một mục đã được biên soạn trong bài, editor điền sẵn nghĩa và ngữ cảnh; từ khác có thể dùng AI hoặc tự bổ sung. Chọn cả câu/đoạn rồi bấm **Giải thích câu** để hỏi. Phần lưu từ giới hạn 160 ký tự/16 từ; phần hỏi câu cho phép đoạn chọn dài hơn, tối đa 4.000 ký tự.

Trong **Bài đọc của tôi**, có thể tìm theo tiêu đề/nguồn/nội dung; lọc tiến độ và yêu thích; sắp xếp; chuyển trang. Trong **Kho từ**, có thể tìm theo nội dung thẻ, lọc tag/bài nguồn/trạng thái và sắp xếp. Các nhóm học gồm đến hạn, quá hạn, mới, đang học, đã ghi nhớ tốt, từng sai và chưa xác nhận. “Mới” chỉ gồm thẻ chưa từng ôn; “đang học” là thẻ đã ôn có khoảng cách dưới 21 ngày.

Chỉ những mục bạn chọn lưu mới vào kho. Các cách ôn cũ vẫn giữ: flashcard; ABCD Anh→Việt; ABCD Việt→Anh; synonym; paraphrase; điền từ; gõ từ. Dashboard có mục tiêu ngày, số lượt hôm nay, streak và các nhóm tiến độ. Hàng đợi đến hạn ưu tiên lịch cũ hơn; đánh giá **Quên** đưa thẻ gặp lại trễ hơn trong cùng lượt, tối đa một lần. Thẻ theo nghĩa đã có thì không bị đặt lại lịch ôn. Một thẻ hiện chỉ giữ một ngữ cảnh chính và một liên kết bài nguồn; lưu từ cùng nghĩa ở bài khác gộp tags chứ chưa có bảng toàn bộ lần xuất hiện.

## 4. Hỏi đáp theo đúng bài đang đọc

Giải đáp soạn sẵn chạy hoàn toàn từ dữ liệu bài. Câu hỏi mới có hai cách xử lý:

**Không API:** điền câu hỏi, chọn **Copy prompt / Dán JSON**, dán prompt sang công cụ AI đang dùng, mang JSON về. App kiểm tra rồi lưu lịch sử. Đây vẫn là thao tác copy–paste, không phải AI chạy offline hoặc tích hợp sẵn gói ChatGPT.

**API:** cấu hình OpenAI ở backend như README_VI. Sau khi người dùng xác nhận, app gửi bài đang mở, câu hỏi và phần đã chọn. Key không nằm trong JavaScript. Nội dung người học nhập được coi là dữ liệu học, không phải quyền thực thi lệnh.

Mỗi câu trả lời phải có `answer_vi`, `cannot_answer`, `limitation_vi`, `evidence`, `language_notes`. Nếu trả lời được, ít nhất một trích đoạn phải khớp đúng đoạn gốc. Thiếu bằng chứng thì app từ chối lưu; nếu bài không đủ dữ kiện, AI được yêu cầu nói rõ. Bản dịch/synonym/nội dung giải thích vẫn là tham khảo: **khớp trích dẫn không chứng minh lập luận đúng**.

Lịch sử hiển thị tối đa 30 câu mới nhất của phiên bản văn bản hiện tại. Sửa nội dung bài tự nhập sẽ xóa phân tích/tiến độ đọc hiện tại và ẩn câu trả lời của văn bản cũ; thẻ đã lưu không bị xóa. App không tự suy ra rằng ngữ cảnh của các thẻ cũ cũng đã được cập nhật.

Giới hạn: 16.000 ký tự bài cho một yêu cầu AI, 1.500 ký tự câu hỏi. Không có tìm kiếm web, OCR, hàng đợi tác vụ dài, tự sinh kho đề thi hay API Gemini/Ollama trong bản này.

## 5. Cài mới

Dùng Docker Desktop đã chạy Linux containers. Xem `README_VI.md` cho hướng dẫn Windows đầy đủ.
Trong thư mục có `manage.py`, `compose.yml`, `setup.ps1`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
docker compose ps
docker compose exec web python manage.py createsuperuser
```

Entry point chạy migration và `seed_lessons` để nạp thư viện dùng chung. Khi web healthy, mở `http://localhost:8000`.
Muốn có bộ 116 thẻ cũ và Set in Metal trong tài khoản cá nhân thì chạy thêm (thay đúng username):

```powershell
docker compose exec web python manage.py seed_demo --username quyen
```

Chỉ muốn đọc bài và tự lưu từ thì bỏ qua `seed_demo`. `seed_lessons` không cần username và không tự thêm từ vào tài khoản.

## 6. Nâng cấp từ LexiRead bản trước — giữ database cũ

**Trước hết xuất Backup JSON trong app, sao lưu `.env` ở nơi riêng và có backup PostgreSQL khi dữ liệu đã quan trọng.** Không chia sẻ `.env`. Không chạy `docker compose down -v`.

Giữ thư mục project/Compose project name hiện tại; không vô tình chạy ở một thư mục tên khác rồi cho rằng database biến mất. Tên project khác có thể trỏ tới volume mới. Giải nén gói mới ở nơi tạm, chép mã nguồn vào project đang dùng, **giữ nguyên `.env` và Compose project name/volume hiện tại**. Không chép đè file cấu hình cá nhân đã chỉnh mà chưa đối chiếu.

Tại thư mục project cũ, ví dụ `D:\projects\LexiRead`:

```powershell
cd D:\projects\LexiRead
docker compose up --build -d
docker compose ps
docker compose logs --tail 80 web
docker compose exec web python manage.py showmigrations learning
docker compose exec web python manage.py seed_lessons
```

Kiểm tra `0001_initial` và `0002_reading_platform` đã đánh dấu `[X]`. Lệnh seed cuối chỉ để kiểm tra/nạp lại an toàn; entry point đã chạy khi khởi động. **Không tạo lại tài khoản và không cần chạy lại `seed_demo`** nếu trước đó đã dùng.

Chạy web trực tiếp bằng Python thay vì Docker: dừng tiến trình cũ, giữ `.env` và DB, cập nhật requirements rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_lessons
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Migration bổ sung bảng/trường, không có thao tác chủ động xóa từ, tài khoản hoặc lịch ôn. **Migration vẫn chưa được chạy trên PostgreSQL trong môi trường tạo gói**, nên backup và kiểm thử trên DB bản sao trước khi nâng cấp dữ liệu quan trọng.

## 7. Dùng bản HTML và chuyển dữ liệu

`preview.html` chứa toàn bộ thư viện 12 bài và bộ từ mẫu; chỉ cần mở file, không cần API để đọc bài, xem bản dịch, làm câu hỏi cố định và ôn từ. Chỉ import TXT/dán chữ ở bản này; import DOCX/PDF có text là tính năng backend.

Bản v2 giữ khóa Storage của v1 để không chủ động đặt lại kho đang có. Tuy nhiên, **đổi đường dẫn file/trình duyệt không được bảo đảm dùng cùng vùng lưu trữ**. Cách chuyển tin cậy là xuất backup ở bản cũ → mở bản mới → Cài đặt & dữ liệu → nhập backup. Để khôi phục đúng lịch ôn cho những từ trùng với bộ seed, nên dùng kho đích trống; importer giữ tiến độ sẵn có và không ghi đè.

Backup JSON v2 gồm bài nguồn, snapshot bài cố định, thẻ, lịch ôn, câu đã hỏi của văn bản hiện tại và các lần làm câu hiểu bài. V2 đọc được backup v1. Không nhập backup v2 vào ứng dụng v1 chưa nâng cấp.

Khôi phục kiểu gộp: bài/thẻ có sẵn giữ dữ liệu hiện tại; chỉ đối tượng mới được khôi phục tiến độ. Điểm quiz được tính lại từ bộ đáp án trong snapshot thay vì tin con số do file nhập cung cấp. Thời điểm ghi log hỏi đáp/hiểu bài có thể là thời điểm nhập lại ở backend, không phải bản sao audit đầy đủ. Backup ứng dụng không chứa tài khoản/mật khẩu, không thay backup database hệ thống.

## 8. Quản trị và thêm bài mới

Xem `LESSON_AUTHORING.md`. Dữ liệu gốc ở `data/lessons/*.json`, nạp vào bảng `CuratedLesson`. Admin có thể lọc theo chủ đề/mức và chỉnh JSON trong trang quản trị, chưa có CMS kéo-thả.

`seed_lessons` mặc định chỉ thêm bài chưa có; không ghi đè biên tập đã làm. Dùng `--update` khi thực sự muốn cập nhật bài chuẩn từ file. Người đã mở một bài tiếp tục dùng snapshot cũ để bản dịch, câu hỏi và điểm không thay đổi giữa chừng. Chưa có nút nâng phiên bản snapshot của một bài đang học; đọc phiên bản cũ vẫn hoạt động.

## 9. Những gì đã kiểm tra

Ngày 22/10/2026, bộ pure Python chạy 76 test, gồm 75 PASS và 1 test reportlab tùy chọn skip. 49 kiểm tra DOM/luồng bản HTML qua Chromium PASS khi không có fixture v1 cũ; suite có 50 checks nếu cung cấp fixture đó. Ảnh chụp giao diện cũng đã được kiểm tra trực quan. Chi tiết thực tế và hạn chế xem `TEST_REPORT.md`.

35 integration tests cho Django/PostgreSQL đã được chuẩn bị (16 trong `learning/tests.py`, 19 trong `learning/test_platform.py`), **chưa chạy vì không có PostgreSQL listener**. Django `check` đã PASS và `makemigrations --check --dry-run` báo không có thay đổi khi dùng môi trường xác nhận tạm. Chưa chạy Docker/full database hoặc gọi OpenAI API thật. Kiểm tra DOM dùng Storage giả lập trong bộ nhớ, không chứng minh dữ liệu tồn tại qua việc đóng/mở trình duyệt thật. Website chưa được triển khai public.

```powershell
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web python manage.py test learning -v 2
```

Dùng database phát triển cho các lệnh kiểm thử, không cấu hình vào DB production. Sau đó thử thực tế đăng nhập hai tài khoản, lưu từ từ bài chuẩn/bài tự nhập, hỏi JSON, tải lại trang, export/import và đối chiếu tiến độ.
