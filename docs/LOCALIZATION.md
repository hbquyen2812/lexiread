# Ngôn ngữ giao diện

LexiRead dùng bốn ngôn ngữ: `vi`, `en`, `fr`, `zh`. Các bản dịch được đóng gói
trong `static/i18n_catalog.js`, nạp trước `static/i18n.js`. Đổi ngôn ngữ chỉ cập
nhật chữ và thuộc tính giao diện trong DOM, không gọi dịch vụ dịch hay AI.

## Ranh giới nội dung

- Dùng `lang="en" data-no-i18n` cho từ đang học, câu ví dụ, bài đọc và đáp án tiếng Anh.
- Dùng `data-no-i18n` cho nội dung người dùng tự nhập, tên bộ từ, nghĩa và ghi chú đã lưu.
- Không khóa cả một trang hướng dẫn bằng `data-no-i18n`. Chỉ đánh dấu phần cần giữ nguyên.
- Với câu có cả nhãn và nội dung học, tách thành các `span`; giữ nhãn ngoài vùng khóa.
- `textarea`, nội dung chỉnh sửa trực tiếp và giá trị form được giữ nguyên. Placeholder
  và nhãn truy cập vẫn có thể dịch. Tên ngôn ngữ trong menu luôn dùng tên bản địa.
- Không dựng lại form khi đổi ngôn ngữ: giữ đáp án, tab đang chọn và dữ liệu nhập dở.

## Sửa bản dịch

`data/interface_translations.json` chứa các bản sửa biên tập theo cấu trúc
`"câu tiếng Việt": ["English", "Français", "简体中文"]`. Bản sửa có ưu tiên cao hơn
bản nháp. Các mẫu như `Câu {0}` được áp dụng cho cả những biến thể chỉ khác số
thứ tự của biến. Luôn giữ đủ biến và các thuật ngữ tiếng Anh trong câu.

```powershell
npm ci --ignore-scripts
npm run locales:extract
.venv\Scripts\python.exe -X utf8 scripts/build_locales.py
npm run test:i18n
.venv\Scripts\python.exe -X utf8 scripts/build_locales.py --check
```

Bộ trích xuất chỉ đọc mã nguồn và nội dung học đã biên soạn trong repository.
Nó không đọc database, `.env`, dữ liệu tài khoản hay kho từ cá nhân. Các tệp
trung gian nằm trong `data/private/localization-build/` và không được commit.
Bản dịch đã đóng gói đủ để chạy lại bước build ngoại tuyến.

Với câu mới chưa có bản dịch, thêm bản dịch biên tập hoặc chủ động chạy
`build_locales.py --translate`. Cờ này cho phép công cụ bảo trì gửi **chữ công khai
trong repository** tới endpoint dịch công khai của Google; endpoint không có
cam kết ổn định. Website không sử dụng endpoint này. Lỗi HTTP sẽ dừng công cụ.
Các bản dịch hỗ trợ máy cần đọc lại, đặc biệt phần thuật ngữ và câu giải thích.
Công cụ từ chối xuất bản nếu thiếu ngôn ngữ hoặc thay đổi biến được bảo vệ.

Sau khi sửa, tăng phiên bản cache của các script trong template, chạy
`scripts/build_preview.py`, rồi kiểm tra trên trình duyệt. Kiểm thử DOM bao gồm
đổi ngôn ngữ qua lại, nội dung tải sau, nhãn truy cập, giữ nguyên tiếng Anh,
nội dung cá nhân và lựa chọn trong bài tập.
