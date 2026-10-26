# Tạo bộ từ riêng để ôn trên LexiRead

Vào **Kho từ của tôi → Tạo / nhập bộ từ**. Điền tên bộ, chủ đề, trình độ và số từ; bấm **Sao chép prompt cho AI** rồi dán vào công cụ AI bạn đang dùng. Prompt yêu cầu nghĩa tiếng Việt dễ hiểu, cấu trúc thường gặp và ví dụ có bản dịch. Bước này không gọi API AI của website.

Tải file JSON do AI tạo, chọn file ở bước 2 và bấm **Xem trước bộ từ**. Nếu AI chỉ trả đoạn mã, bạn có thể dán thẳng đoạn JSON vào ô trên trang. Đọc lại nghĩa và ví dụ, bỏ chọn những mục không muốn học, rồi bấm **Lưu bộ từ vào kho của tôi**. Sau đó chọn **Ôn bộ từ này** để bắt đầu.

Bạn cũng có thể tự điền file mẫu ở `static/examples/lexiread-vocabulary.json`. Cấu trúc tối thiểu:

```json
{
  "format": "lexiread-vocabulary",
  "version": 1,
  "deck": { "name": "Email công việc" },
  "vocabulary": [
    { "word": "confirm", "meaning_vi": "xác nhận" }
  ]
}
```

Mỗi mục có thể thêm `pos`, `usage_pattern`, `example`, `example_vi`, `synonyms`, `paraphrases`, `context` và `note`. Hai trường danh sách dùng mảng chuỗi; các trường còn lại dùng chuỗi văn bản. File mẫu đầy đủ có ví dụ cho từng trường. Mỗi file tối đa 2 MB và 500 mục; tên bộ tối đa 100 ký tự. Một mục chỉ nên gồm một từ hoặc cụm từ với một nghĩa.

Từ và nghĩa giống nhau được gộp vào thẻ đã có, thêm tên bộ mới và giữ nội dung cùng lịch ôn hiện tại. Cùng một từ nhưng khác nghĩa được lưu thành thẻ riêng. Một thẻ có thể thuộc nhiều bộ. Nếu thẻ đã có đủ 20 nhãn, website sẽ báo để bạn bớt nhãn hoặc bỏ chọn thẻ đó trước khi nhập.

Để tìm lại, chọn tên bộ trong bộ lọc **Bộ từ** ở kho từ hoặc màn hình ôn tập. Nút **Tải bộ từ** xuất riêng nội dung bộ đang chọn. File này có thể nhập sang tài khoản khác; lịch ôn và thông tin tài khoản không nằm trong file. Muốn giữ cả tiến độ, dùng phần sao lưu đầy đủ trong Cài đặt.

Nội dung AI tạo được lưu ở trạng thái chưa duyệt. Bạn có thể sửa từng thẻ sau khi lưu. Việc kiểm tra cấu trúc file giúp phát hiện lỗi dữ liệu, không thay thế việc đọc lại nghĩa và ví dụ.
