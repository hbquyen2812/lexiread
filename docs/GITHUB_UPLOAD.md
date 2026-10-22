# Đưa LexiRead lên GitHub an toàn

Hướng dẫn này dành riêng cho thư mục dự án hiện tại trên Windows. Git đã có trên máy, nhưng `D:\LexiRead` **chưa được khởi tạo thành Git repository**, chưa có commit và chưa có remote. Không cần cài GitHub CLI; có thể tạo repository trên website GitHub rồi dùng PowerShell để đẩy mã nguồn.

## 1. Chọn private trước

Nên tạo repository **Private** ở lần đẩy đầu tiên. Private giúp tránh vô tình công khai tên thật, dữ liệu học và nội dung chưa xác minh quyền tái xuất bản; nó không thay thế việc kiểm tra bản quyền và không biến nội dung không có quyền chia sẻ thành nội dung được phép đăng.

Không commit hoặc gửi cho người khác:

- `.env`, `OPENAI_API_KEY`, `DJANGO_SECRET_KEY`, mật khẩu PostgreSQL hoặc token đăng nhập;
- file backup do ứng dụng xuất, database dump và thư mục `data/private/`;
- dữ liệu cá nhân hoặc bài đọc chưa chắc chắn quyền chia sẻ.

File `.env.example` chỉ chứa tên biến và placeholder nên được giữ trong repository để hướng dẫn cài đặt. `.gitignore` đã loại `.env`, môi trường ảo, log, database dump, backup cục bộ và `data/private/`.

## 2. Nội dung phải xem xét trước khi public

Tài liệu nguồn của dự án ghi rõ bài **Set in Metal** do người học cung cấp và chưa có nguồn độc lập chứng minh quyền tái xuất bản. Nội dung đầy đủ hoặc dữ liệu dẫn xuất hiện nằm trong:

- `data/set_in_metal.txt`;
- `data/demo_analysis.json`;
- `data/seed_vocab.json`;
- `data/personal_vocab.json`;
- `preview.html`, vì file này nhúng sẵn passage và bộ từ khi được build.

Các file trên đang được ứng dụng demo sử dụng. Không chỉ thêm chúng vào `.gitignore` rồi coi như xong, vì `seed_demo` và `scripts/build_preview.py` sẽ thiếu dữ liệu. Trước khi đổi repository sang Public, hãy thay chúng bằng một bài và bộ từ tự biên soạn hoặc có giấy phép phù hợp, cập nhật test/tài liệu liên quan, rồi build lại `preview.html`.

`README_VI.md` cũng đang có tên thật và ví dụ username cá nhân. Hãy chủ động quyết định giữ hay ẩn các thông tin này trước khi public.

## 3. Tạo repository trên website GitHub

1. Đăng nhập [GitHub](https://github.com/), chọn **New repository**.
2. Đặt tên, ví dụ `lexiread`.
3. Chọn **Private**.
4. Không chọn tạo sẵn README, `.gitignore` hoặc LICENSE để repository từ xa hoàn toàn trống và tránh xung đột lần push đầu.
5. Chọn **Create repository**, sau đó sao chép URL HTTPS dạng `https://github.com/USERNAME/lexiread.git`.

Repository hiện chưa có LICENSE. Không chọn giấy phép ngẫu nhiên; chỉ thêm sau khi đã quyết định rõ người khác được phép làm gì với mã nguồn và nội dung học.

## 4. Khởi tạo Git bằng PowerShell

Mở PowerShell và chạy:

```powershell
cd D:\LexiRead
git init -b main
git status --short --branch
git config --get user.name
git config --get user.email
```

Nếu hai lệnh cuối chưa trả về thông tin đúng, cấu hình **riêng cho repository này**:

```powershell
git config user.name "TEN_HIEN_THI_CUA_BAN"
git config user.email "EMAIL_GITHUB_CUA_BAN"
```

Có thể dùng địa chỉ `noreply` do GitHub cung cấp nếu không muốn email cá nhân xuất hiện trong lịch sử commit.

## 5. Kiểm tra trước commit đầu tiên

Trước hết xác nhận các loại file nhạy cảm được ignore:

```powershell
git check-ignore -v --no-index .env data/private/example.txt backups/example.dump lexiread-backup-2026.json
```

Sau đó stage và xem toàn bộ danh sách. `git add .` chỉ an toàn khi luôn đi kèm bước kiểm tra ngay sau đó:

```powershell
git add .
git status --short
git diff --cached --stat
git diff --cached --name-only
```

Kiểm tra các dấu hiệu secret có độ tin cậy cao trong phần đã stage:

```powershell
git grep --cached -n -I -E "(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY)"
git grep --cached -n -I -E "(OPENAI_API_KEY|DJANGO_SECRET_KEY|POSTGRES_PASSWORD)"
```

Lệnh thứ hai dự kiến sẽ thấy tên biến trong `.env.example`, mã nguồn và tài liệu. Hãy mở từng kết quả để chắc chắn chỉ có placeholder hoặc cách đọc biến môi trường, không có giá trị thật.

Trước khi public, kiểm tra thêm dữ liệu cá nhân và nội dung đang bị chặn:

```powershell
git grep --cached -n -I -E "(Set in Metal|Huỳnh Bảo Quyên|quyen)"
```

Nếu stage nhầm một file mới, bỏ file đó khỏi index nhưng giữ file trên máy:

```powershell
git rm --cached -- DUONG_DAN_FILE
```

Với cả thư mục, thêm `-r`:

```powershell
git rm -r --cached -- DUONG_DAN_THU_MUC
```

Sau khi sửa `.gitignore` hoặc thay dữ liệu, chạy lại `git add .`, `git status --short` và các kiểm tra trên. Không commit trước khi hiểu rõ mọi file trong danh sách staged.

## 6. Commit và push repository private

Khi phần staged đã an toàn:

```powershell
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/lexiread.git
git remote -v
git push -u origin main
```

Thay `USERNAME` và tên repository bằng URL vừa sao chép. Git Credential Manager trên Windows có thể mở trình duyệt để đăng nhập. Không lưu access token vào file trong dự án và không dán token vào URL remote.

Sau khi push, mở repository trên GitHub, kiểm tra lại **Settings → General → Visibility** vẫn là Private và duyệt danh sách file trực tiếp trên GitHub.

## 7. GitHub Pages không chạy bản Django

Đẩy mã nguồn lên GitHub **không tự triển khai website**. GitHub Pages chỉ phục vụ file tĩnh; nó không chạy Django, PostgreSQL, Docker, đăng nhập server, API AI hoặc đồng bộ dữ liệu giữa thiết bị.

Về sau có thể phát hành một bản HTML tĩnh đã làm sạch từ `preview.html`, nhưng cần cấu hình file entry/build cho Pages. Bản đó dùng `localStorage`: mỗi trình duyệt có dữ liệu riêng, không có tài khoản server và không tự đồng bộ. Không bật Pages với `preview.html` hiện tại vì file đang nhúng dữ liệu Set in Metal.

Muốn đưa bản Django lên Internet cần một dịch vụ chạy Python/PostgreSQL, HTTPS, biến môi trường an toàn, backup và cấu hình production riêng. Không đổi mapping trong `compose.yml` thành cổng public rồi coi đó là triển khai an toàn.

## 8. Checklist trước khi chuyển Public

- Thay toàn bộ bài Set in Metal và dữ liệu dẫn xuất bằng nội dung tự biên soạn hoặc có quyền phát hành; build lại `preview.html`.
- Xóa hoặc chủ động chấp nhận việc công khai tên thật, username ví dụ và mọi dữ liệu học cá nhân.
- Chạy lại secret scan trên toàn bộ phần staged và xác nhận `.env`, backup, dump không có trong lịch sử Git.
- Chọn và thêm LICENSE phù hợp cho **mã nguồn**; ghi riêng quyền sử dụng dataset/nội dung nếu khác với mã nguồn.
- Sửa README để người lạ hiểu cách cài, giới hạn của bản local và trạng thái kiểm thử thực tế.
- Chạy kiểm tra cấu hình, migrations và test được hướng dẫn trong `README_VI.md`; không mô tả dự án là production-ready khi chưa kiểm chứng triển khai thật.
- Bật branch protection hoặc CI nếu bắt đầu nhận đóng góp; repository cá nhân chưa bắt buộc phải có các phần này.
- Kiểm tra lại lịch sử commit trước khi đổi visibility. Nếu secret từng được commit, xóa file ở commit mới là chưa đủ: phải thu hồi/đổi secret và làm sạch lịch sử trước khi public.

Khi checklist hoàn tất, đổi visibility trong GitHub **Settings → General → Danger Zone → Change repository visibility**. Đọc kỹ cảnh báo của GitHub trước khi xác nhận.

## 9. Tài liệu GitHub chính thức

- [Đưa mã nguồn đang có trên máy lên GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [Thiết lập repository Public/Private](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [Tạo GitHub Pages và giới hạn với ngôn ngữ server-side](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
