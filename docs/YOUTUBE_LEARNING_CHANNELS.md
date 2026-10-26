# Kênh YouTube theo trình độ — 26/10/2026

Mở `/#guides/youtube` trong không gian học, hoặc `/guides/#guides/youtube` khi chưa đăng nhập. Mục này nằm cùng cẩm nang, không thêm một mục nữa vào thanh điều hướng chính.

Tám kênh được giới thiệu bằng mô tả ngắn, bài/loạt video để bắt đầu và một hoạt động sau khi xem. Có lọc A1–C2, mục tiêu, tìm kiếm không dấu và trạng thái không có kết quả. Link mở kênh hoặc bài tại nguồn. Nút tạo bộ từ nối sang luồng nhập từ cá nhân hiện có.

## Cách chọn

Các mức là **gợi ý biên tập của LexiRead**, không phải chứng nhận CEFR của kênh. Cùng kênh có video dễ và khó. BBC và Easy English có gợi ý loạt video khác nhau cho người mới và người đã có nền tảng. TED/TED-Ed là nội dung kiến thức, không phải khóa tiếng Anh theo cấp độ. Không hứa hẹn tăng band hoặc đánh giá hiệu quả dựa trên lượt xem/người đăng ký.

| Kênh | Mức gợi ý | Nguồn sơ cấp đã đối chiếu |
|---|---|---|
| VOA Learning English | A1–A2 | [Let’s Learn English – Level 1](https://learningenglish.voanews.com/p/5644.html): khóa cho người bắt đầu, bài có video và tài liệu đi kèm |
| Easy English | A1–B1 | [Trang kênh](https://www.easyenglish.video/): Slow Easy English, phỏng vấn và phụ đề tiếng Anh |
| BBC Learning English | A2–B2 | [Kênh chính thức](https://www.youtube.com/channel/UCHaHD477h-FeBbVh9Sh7syA), [danh mục BBC](https://feeds.bbci.co.uk/learningenglish): Real Easy English và 6 Minute English |
| Rachel’s English | A2–C1 | [Trang tác giả](https://rachelsenglish.com/), [luyện âm Mỹ](https://rachelsenglish.com/practice-american-sounds/) |
| Oxford Online English | A2–B2 | [Bài Office Expressions](https://www.oxfordonlineenglish.com/office-expressions): video và bài tập; dùng liên kết YouTube của video được nhúng tại nguồn |
| IELTS Advantage | B1–C1 | [Trang IELTS Reading](https://www.ieltsadvantage.com/ielts-reading-2/): có liên kết trực tiếp tới video được gợi ý |
| TED-Ed | B2–C2 | [Bài The benefits of a bilingual brain](https://ed.ted.com/lessons/how-speaking-multiple-languages-benefits-the-brain-mia-nacamulli) và [video chính thức](https://www.youtube.com/watch?v=MMmOLN5zBLY) |
| TED | B2–C2 | [Bài Julian Treasure](https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen) và [video chính thức](https://www.youtube.com/watch?v=eIho2S0ZahI) |

Trang YouTube có thể chỉ trả phần khung khi đọc tự động; xác nhận tên kênh và nguồn của người xuất bản, không suy ra mọi video đều phát được ở mọi nơi. BBC chặn một số trang qua robots; không vượt chặn. Danh sách không chứa số người theo dõi hoặc khẳng định tần suất đăng hiện tại.

Không tải lại video, phụ đề, thumbnail hoặc nhúng trình phát. Trang chỉ đọc metadata cục bộ; không gọi YouTube khi người dùng mở cẩm nang. Chi tiết nguồn và phần có phí được gói trong “Thông tin thêm”.

## Kiểm tra

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_learning_channels.py
.\.venv\Scripts\python.exe manage.py test learning.test_learning_channels learning.test_learning_hub --settings=config.test_settings --noinput
node scripts/test_learning_channels.cjs
.\.venv\Scripts\python.exe scripts/build_preview.py
```

Kết quả: 108 kiểm thử Python thuần (107 đạt, 1 fixture PDF tùy chọn bỏ qua), 106/106 Django trên PostgreSQL đạt; kiểm thử Node cho kênh và hồi quy frontend/learning hub đạt. Static build: 167 file, 487 thao tác xử lý. Đã thử trình duyệt công khai và sau đăng nhập: bộ lọc A1 + IELTS rỗng, xóa lọc, tìm “phat am”, B1 + công việc, chuyển qua cẩm nang và sang tạo bộ từ. Độ rộng 320/390/768/1024/1440px không tràn ngang; không ghi nhận lỗi console trong lượt kiểm tra.

Ảnh: [desktop](qa/youtube-channels-desktop.jpg), [mobile](qa/youtube-channels-mobile.jpg). Chỉ xác minh liên kết và nguồn; không kiểm chứng phát mọi video trên từng quốc gia/thiết bị.
