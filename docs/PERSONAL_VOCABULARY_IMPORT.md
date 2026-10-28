# Tạo bộ từ riêng để ôn trên LexiRead

Vào **Kho từ của tôi → Nhập bộ từ cá nhân**. Trang có ba bước: tạo prompt, nhập kết quả và xem lại để lưu. Nếu đã có file bộ từ, bạn có thể bắt đầu ngay ở bước 2.

1. **Tạo prompt từ bài đọc:** đặt tên bộ, giữ nguồn **Từ bài đọc** và dán bài tiếng Anh vào ô. Chọn **Mức từ vựng tối thiểu** và **Số từ tối đa**, rồi bấm **Sao chép prompt cho AI**. Bài đọc tối đa 20.000 ký tự; với bài dài hơn, chia thành nhiều phần. Chọn **Theo chủ đề** nếu muốn tạo bộ từ mà chưa có bài đọc.
2. **Lấy và nhập kết quả:** dán prompt vào AI bạn đang dùng và gửi. Tải file JSON AI trả về, hoặc sao chép toàn bộ khối JSON. Quay lại LexiRead, chọn file ở bước 2 hoặc mở **Dán nội dung JSON**, rồi bấm **Xem trước bộ từ**.
3. **Xem lại và lưu:** đọc nghĩa, ví dụ và bỏ chọn những từ không muốn học. Bấm **Lưu bộ từ vào kho của tôi**, rồi chọn **Ôn bộ từ này** để bắt đầu.

**B1 trở lên** gồm B1, B2, C1 và C2; đây là ngưỡng từ vựng muốn học, không giới hạn bộ từ ở riêng B1. Tương tự, B2 trở lên gồm B2, C1 và C2. Số từ là mức tối đa: nếu bài chỉ có 12 từ phù hợp thì không cần tạo đủ 20. Nếu không có từ phù hợp, prompt yêu cầu AI báo lại để bạn hạ ngưỡng hoặc đổi bài, thay vì xuất một bộ rỗng.

Khi chọn bài đọc, prompt yêu cầu chỉ lấy từ/cụm từ trong bài, giữ đúng nghĩa theo ngữ cảnh và chép một hoặc hai câu gốc vào `context`. Nghĩa Việt và ví dụ mới cần tự nhiên, dễ hiểu. Khi chọn chủ đề, phần bài đọc đã ẩn không được đưa vào prompt.

LexiRead chỉ tạo và sao chép prompt trong trình duyệt, không tự gửi bài đọc hay gọi API AI. Bạn chủ động gửi prompt cho công cụ mình chọn. Nếu trình duyệt không cho sao chép, ô prompt sẽ mở để bạn sao chép thủ công. Khi sửa bài, mức hoặc số từ, bấm sao chép lại để có prompt mới. Mức của từng từ do AI phân loại khi làm theo prompt; chức năng nhập không tự chứng thực cấp độ hoặc kiểm tra lại nghĩa thay cho người học.

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
