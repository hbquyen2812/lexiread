# Từ vựng theo chủ đề và từ điển lưu trong database

## Người học dùng thế nào?

Mở **Lộ trình & nền tảng → Từ theo chủ đề**. Có 15 chủ đề tiếng Anh, 30 bộ từ A1–C2 và 360 mục từ có nghĩa Việt, ví dụ và cách dùng. Lọc chủ đề/trình độ hoặc tìm theo tên bộ. Mở bộ để học bằng thẻ, tự nhớ trước khi xem nghĩa, luyện câu hỏi hoặc lưu từ vào bộ cá nhân để ôn cách quãng.

Trong chế độ thẻ, **Lưu từ này** chỉ lưu thẻ đang xem. Danh sách từ được ẩn để tránh nhìn thấy đáp án. Phần luyện và lưu nhiều từ vẫn dùng luồng hiện có, giữ nguyên lịch ôn và kết quả theo tài khoản.

**Từ điển** tìm trong 127.311 mục từ Open English WordNet 2025 đã chuẩn hóa, có 27.581 mục với IPA và 4.447 quan hệ dạng biến đổi. Tìm theo đầu từ, phân trang 20 kết quả hoặc tra dạng như `ran`. Vẫn có thể bôi đen từ trong bài để mở popup. Mục từ có nhiều nghĩa được giữ đầy đủ trong database; các nghĩa phụ được thu gọn khi hiển thị.

Kho bổ sung có 371 mục từ Wiktionary và 197 bản thu Commons tải sẵn. Số bản thu là số file khác nhau, không phải số từ có đủ cả hai giọng UK/US. IPA ưu tiên dữ liệu OEWN, tách khỏi nhãn bản thu; không gán phiên âm từ metadata API cho một file ghi âm khi chưa xác minh chúng cùng biến thể phát âm.

Nghĩa Việt vẫn lấy từ bài đang đọc, kho cá nhân và 360 mục từ học. Phần từ điển mở chủ yếu là Anh–Anh; không tự dịch hàng loạt bằng AI. Oxford/Cambridge là liên kết đối chiếu, không phải bộ dữ liệu được sao chép vào LexiRead. Không phải mọi mục từ đều có IPA hoặc audio.

## Chi phí và lưu trữ

- Các trang học chủ đề, thẻ từ, luyện tập, đề xuất lộ trình, tra nghĩa, IPA và audio đã tải sẵn **không gọi AI**. Mặc định cấu hình website vẫn là `AI_PROVIDER=none`; các thao tác AI tùy chọn cũ yêu cầu người học chủ động chọn.
- Không gọi Free Dictionary API/Commons trong request học hoặc tra cứu. Kết quả thiếu từ được trả từ database; không âm thầm gửi truy vấn ra ngoài.
- `DictionaryEntry` lưu nghĩa, ví dụ, nguồn/giấy phép và IPA; `DictionaryForm` lưu dạng biến đổi; `DictionarySupplement` giữ dữ liệu bổ sung; `DictionaryAudio` lưu bytes âm thanh; `VocabularyCollection` lưu các bộ học.
- Trong QA, bảng từ điển chính khoảng **115 MB**, chưa tính bản sao lưu và tăng trưởng dữ liệu cá nhân. Hai gói nguồn nén đi kèm tổng cộng khoảng **13 MB**. Không tải gói từ điển lớn xuống trình duyệt; mỗi lượt tìm chỉ trả tối đa 20 mục.
- Dữ liệu dùng chung có thể tái nhập từ gói nguồn. Backup cá nhân không nhét cả từ điển vào file; backup PostgreSQL bao gồm các bảng này.

## Cài đặt và nâng cấp

```sh
python manage.py migrate --noinput
python manage.py seed_dictionary
```

`entrypoint.sh` đã chạy hai bước này trước Gunicorn. `seed_dictionary` kiểm tra SHA-256 của gói OEWN; gắn phiên bản chuyển đổi; chạy transaction và ghi theo lô. Lần chạy sau bỏ qua gói đã nhập. Seed các bộ học chỉ tạo mục còn thiếu, giữ bộ đã chỉnh và không tác động thẻ/lịch ôn riêng. Giữ file gói trong image khi triển khai. Cần migration 0011–0012.

`scripts/build_pronunciation_pack.py` chỉ dành cho người bảo trì chuẩn bị gói mới: duyệt từ của bộ học/bài đọc, tải nguồn mở với giới hạn đồng thời, timeout và kích thước, kiểm tra nguồn/giấy phép, lưu checkpoint riêng. Script không chạy khi website khởi động. Những từ thiếu dữ liệu hoặc nguồn lỗi vẫn không được gán audio giả. Bản build đã thử 551 từ/cụm từ; kết quả tải được nêu ở trên.

Nguồn đi kèm:

- [Open English WordNet 2025](https://github.com/globalwordnet/english-wordnet/releases/tag/2025-edition), phát triển bởi Open English WordNet Team dựa trên Princeton University WordNet. Gói JSON gốc, manifest checksum và cả hai thông báo giấy phép nằm ở `data/dictionaries/`. Dữ liệu chuyển đổi được gom theo dạng từ chuẩn; giữ các nghĩa và biến thể viết hoa.
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) và giấy phép Princeton WordNet cho OEWN.
- [Free Dictionary API](https://dictionaryapi.dev/), Wiktionary và Wikimedia Commons cho gói bổ sung. Mỗi mục/file giữ liên kết nguồn và giấy phép riêng; giao diện hiển thị các liên kết này.

## Kiểm tra

141/141 kiểm thử Django trên PostgreSQL QA đạt; 8 bộ kiểm thử Node đạt; HTTP smoke và kiểm tra migration đạt. Bộ pure Python chạy 110 ca: 109 đạt, 1 bỏ qua dependency PDF tùy chọn. Collectstatic với cấu hình production trong container QA: 175 file, 511 lượt hậu xử lý.

Kiểm thử tự động chặn `httpx.Client` trong request đọc/tìm/tra dạng từ/nghe audio để xác nhận chúng chỉ dùng database. Có ca kiểm tra phân quyền, phân trang, chống nội dung độc hại, checksum, nhập lại không trùng, giữ chỉnh sửa bộ học, tách nguồn IPA và tính toàn vẹn bản thu.

Kiểm tra Chromium desktop/mobile gồm lọc Travel & Places, học/lật thẻ, lưu riêng một từ, mở từ điển từ thẻ và nghe audio qua `/api/dictionary/audio/…/`. Trang chủ đề/thẻ không tràn ngang ở viewport 390 × 844. Không gọi API AI thật. Chưa triển khai production hoặc kiểm thử Safari/Firefox trên thiết bị thật.

Ảnh: [chủ đề](qa/topic-vocabulary-desktop.jpg), [thẻ desktop](qa/topic-flashcards-desktop.jpg), [thẻ mobile](qa/topic-flashcards-mobile.jpg), [từ điển và audio local](qa/local-dictionary-desktop.jpg). Bản thu `routine` được xác nhận tải từ chính `/api/dictionary/audio/…/`, phát hết 1,121814 giây, `readyState=4` và không có lỗi media.
