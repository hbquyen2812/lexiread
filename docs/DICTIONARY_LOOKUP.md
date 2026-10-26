# Tra nghĩa và phát âm trong LexiRead

**Đã được nâng cấp:** xem [từ điển lưu trong database và bộ từ theo chủ đề](LOCAL_VOCABULARY.md). Phiên bản hiện tại phục vụ nghĩa/IPA/audio tải sẵn từ database, không gọi nguồn ngoài trong request tra từ. Phần dưới giữ lại báo cáo của phiên bản tra trực tuyến trước đó.

## Cách dùng

Trong bài đọc, bôi đen một từ hoặc cụm từ tiếng Anh ngắn rồi chọn **Tra từ & phát âm**. Cửa sổ hiển thị nghĩa tiếng Việt có sẵn trong bài hoặc kho cá nhân, từ loại, phiên âm IPA, bản thu khi nguồn có cung cấp và các nghĩa Anh–Anh. Mục **Đọc phiên âm thế nào?** giải thích dấu trọng âm và liên kết bảng âm Cambridge.

Chọn **Lưu nghĩa này** để mở thẻ đã điền nghĩa, ngữ cảnh bài đọc và IPA. Người học kiểm tra rồi lưu; thao tác tra không tự thêm thẻ. Với từ chưa có nghĩa tiếng Việt trong kho, cần bổ sung nghĩa trước khi lưu. Có thể tra từ ngoài kho tại **Lộ trình & nền tảng → Tra từ → Tra nghĩa & phát âm**.

## Nguồn và phạm vi

- 360 mục từ của khóa học vẫn có ví dụ và nghĩa do LexiRead biên soạn. Các nghĩa riêng được lấy trong phạm vi tài khoản đang đăng nhập.
- [Free Dictionary API](https://dictionaryapi.dev/) cung cấp nghĩa Anh–Anh từ Wiktionary và thông tin phiên âm. Bản thu ưu tiên file gốc của Wikimedia Commons, lấy URL bằng [Imageinfo API](https://www.mediawiki.org/wiki/API:Imageinfo). Giữ liên kết mục từ, bản thu gốc và giấy phép Creative Commons trong popup. Không dùng AI hoặc giọng đọc tổng hợp cho tính năng này.
- Oxford và Cambridge là liên kết đối chiếu. LexiRead **không có bộ dữ liệu Oxford/Cambridge được cấp phép tích hợp** và không trình bày nguồn miễn phí như dữ liệu của hai nhà xuất bản này.
- Không phải từ/cụm từ nào cũng có mục từ, IPA, ví dụ hoặc đủ giọng UK/US. Không tự đoán phiên âm, bản dịch hay giọng đọc. Nếu nguồn lỗi, nghĩa nội bộ và liên kết tra cứu vẫn dùng được.
- Bản `preview.html` chỉ tra nghĩa đã có trong bài và mở liên kết nguồn; không gọi API từ điển bên ngoài.

## Dữ liệu và vận hành

`GET /api/dictionary/?word=...&reading_id=...` yêu cầu đăng nhập. `reading_id` tùy chọn phải thuộc người đang dùng. Chỉ từ/cụm từ được gửi đến Free Dictionary API; không gửi đoạn văn, tài khoản hoặc nghĩa cá nhân. Commons chỉ nhận ID/tên bản thu công khai. Khi bấm nghe, trình duyệt tải âm thanh từ nguồn được hiển thị.

Giới hạn 64 ký tự / 5 từ; chỉ chấp nhận cấu trúc từ tiếng Anh. Các URL ngoài được giới hạn tên miền, giao thức HTTPS và định dạng file; nội dung được escape. API không theo redirect, giới hạn timeout/kích thước và phân biệt lỗi HTML của CDN với mục từ không tồn tại.

Cache chỉ chứa dữ liệu công khai: thành công 24 giờ, không tìm thấy 1 giờ, lỗi nguồn 15 giây. Giới hạn 30 lượt tra chưa có cache mỗi phút/tài khoản. Cache dùng backend Django hiện có; với LocMem, giới hạn áp dụng theo tiến trình. Kết quả có dữ liệu cá nhân trả `Cache-Control: private, no-store`. Không cần migration, API key hoặc phí gọi AI.

## Kiểm tra ngày 26/10/2026

- 134/134 kiểm thử Django trên PostgreSQL QA đạt, gồm 10 kiểm thử từ điển: phân quyền, tách nghĩa cá nhân/cache, giới hạn truy vấn, nguồn lỗi, giấy phép, URL, HTML và metadata bản thu.
- 7 bộ kiểm thử Node đạt; HTTP smoke toàn hệ thống đạt. Các kiểm thử tự động dùng mock nguồn ngoài để chạy ổn định, độc lập mạng.
- Kiểm tra live trên Chromium: bôi đen `routine`, mở nghĩa theo bài, IPA và file Commons; bản thu tải đủ, dài 1,14068 giây và phát đến cuối; mở form lưu giữ đúng ngữ cảnh/IPA. Popup và thanh chọn từ không tràn ngang ở viewport 390 × 844.
- Kiểm tra lỗi thật trong QA phát hiện HTML 404 của CDN và URL audio nhà cung cấp lỗi 502. Đã phân biệt lỗi nguồn với thiếu từ và bổ sung bản thu gốc Commons.
- [Giao diện desktop](qa/dictionary-desktop.jpg) · [Giao diện mobile](qa/dictionary-mobile.jpg).

Chưa kiểm thử trên Safari/Firefox hoặc thiết bị điện thoại thật. Nguồn ngoài vẫn có thể gián đoạn; UI hiển thị trạng thái lỗi và liên kết gốc. Chưa triển khai thay đổi này lên production.
