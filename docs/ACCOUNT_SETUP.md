# Tài khoản và email khôi phục

## Người học sử dụng

- `/signup/`: tự tạo username + mật khẩu + email khôi phục. Username 3–30 ký tự không dấu; mật khẩu ít nhất 10 ký tự và qua bộ kiểm tra mật khẩu Django.
- `/login/`: username hoặc email; tài khoản cũ vẫn dùng email được.
- **Cài đặt → Chỉnh sửa thông tin** (`/account/`): họ, tên, username, email. Đổi username/email phải nhập mật khẩu hiện tại. Dữ liệu học vẫn thuộc cùng user ID.
- **Đổi mật khẩu** (`/account/password/`): cần mật khẩu cũ. Phiên hiện tại giữ đăng nhập; các phiên khác mất hiệu lực.
- **Quên mật khẩu** (`/password-reset/`): gửi liên kết có hiệu lực 1 giờ. Dùng thành công thì liên kết mất hiệu lực. Không gửi mật khẩu cũ/mới qua thư.

Theo lựa chọn của chủ dự án: **không bắt xác minh email, không OTP, không SMS, không Google OAuth**. Email phải do người dùng sở hữu; hệ thống chưa xác minh điều đó. Không dùng nhãn “email đã xác thực”. Chưa có tính năng xóa tài khoản tự phục vụ hoặc 2FA; không coi đây là chứng nhận đã đáp ứng mọi tiêu chuẩn production.

## Bật gửi mail trên Render

Code dùng HTTPS API của Resend. Render Free chặn các cổng SMTP 25/465/587 nên không cấu hình Gmail SMTP theo các hướng dẫn dùng cổng đó. [Giới hạn Render](https://render.com/docs/free).

1. Tạo tài khoản Resend, xác minh tên miền gửi thư và các bản ghi DNS theo [hướng dẫn tên miền](https://resend.com/docs/dashboard/domains/introduction). Sender không phải một địa chỉ Gmail tùy ý. Cần quyền quản lý DNS của tên miền; bạn không sở hữu DNS của `onrender.com`.
2. Tạo API key chỉ cấp quyền gửi mail, giới hạn đúng tên miền nếu có thể. Không gửi key qua chat, không đưa vào Git/JavaScript.
3. Render → dịch vụ LexiRead → **Environment**, thêm:

   ```text
   RESEND_API_KEY=<key của bạn, nhập trực tiếp trong Render>
   DEFAULT_FROM_EMAIL=LexiRead <no-reply@TEN-MIEN-DA-XAC-MINH>
   PUBLIC_SITE_URL=https://lexiread-a3h8.onrender.com
   AUTH_DAILY_LIMIT=100
   ```

4. Kiểm tra `DJANGO_DEBUG=false`, HTTPS bật, `DJANGO_ALLOWED_HOSTS` và `DJANGO_CSRF_TRUSTED_ORIGINS` chỉ chứa các host/origin thực sự của web. URL khôi phục dùng `PUBLIC_SITE_URL` cố định, không lấy Host do người yêu cầu gửi lên.
5. Lưu và deploy. Dùng một tài khoản/email **của bạn**: yêu cầu khôi phục → kiểm tra inbox/spam → đổi mật khẩu → thử liên kết lần hai (phải không dùng được) → đăng nhập bằng mật khẩu mới.

Thiếu key, sender hoặc URL chuẩn thì trang khôi phục thông báo tính năng chưa mở. Không giả báo gửi mail thành công. Khi đã bật, phản hồi công khai là chung cho email không có tài khoản, tài khoản khóa/trùng email và lỗi gửi; lỗi gửi ghi cảnh báo không chứa key hay nội dung thư. Kiểm tra log và dashboard nhà cung cấp nếu người dùng không nhận thư. Luồng gửi đồng bộ có thể khác thời gian phản hồi; chưa có hàng đợi gửi thư nền.

Theo [bảng giá Resend kiểm tra ngày 26/10/2026](https://resend.com/pricing), gói Free có 3.000 email/tháng, tối đa 100/ngày. **Tên miền có thể tốn phí riêng**, nên không hứa toàn bộ triển khai luôn 0 đồng nếu chưa có tên miền. Chưa mua tên miền, đăng ký gói trả phí hay gửi thư thật thay bạn. API được triển khai theo [tài liệu gửi email](https://resend.com/docs/api-reference/emails/send-email).

## Chống lạm dụng và vận hành

- Giới hạn gửi khôi phục: chờ ít nhất 60 giây giữa các lần cho cùng email, tối đa 3/giờ/email, 10/giờ/IP, và `AUTH_DAILY_LIMIT`/24 giờ cho toàn ứng dụng.
- Đăng ký, sửa hồ sơ, đổi mật khẩu có ngân sách riêng: 10 lần/giờ/IP và hạn mức chung/24 giờ. Cả lần gửi sai biểu mẫu cũng tính. Bộ đếm lưu trong PostgreSQL, kiểm thử có nhiều request đồng thời, không reset theo từng worker.
- IP/email trong bảng hạn mức được băm; không lưu mật khẩu hoặc token khôi phục trong bảng này. `prune_logs` dọn bộ đếm không dùng quá 2 ngày; lệnh cũng có chính sách dọn các log cũ khác, xem mã lệnh trước khi đặt lịch vận hành.
- Username/email trùng ở dữ liệu cũ: không tự liên kết tài khoản hoặc gửi reset nhiều tài khoản. Quản trị viên cần xử lý trùng trước. Luồng đăng ký/chỉnh sửa công khai tuần tự hóa kiểm tra; nên kiểm tra trùng nếu nhập User trực tiếp bằng SQL/script.
- Ứng dụng nhỏ có thể dùng cấu hình hiện tại. Khi mở đăng ký rộng rãi, bổ sung giám sát lạm dụng, CAPTCHA theo nhu cầu, hàng đợi gửi mail và quy trình xóa dữ liệu; không chỉ tăng hạn mức.

## Kiểm thử riêng, không đụng production

`config.test_settings` dùng database SQLite in-memory, mail locmem; `config.qa_settings` dùng PostgreSQL QA và mail console. Không import `.env` production. Trong QA, liên kết khôi phục chỉ in ra log container, **không đi đến Gmail**.

```powershell
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa build web
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web manage.py test learning --settings=config.qa_settings --noinput
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web scripts/prepare_qa.py --publish-pack
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa up -d web
```

Mở `http://127.0.0.1:8766/`. Username học viên `qa-reader`; username quản trị `qa-editor`; email tương ứng `@example.test`; mật khẩu QA chung `LexiRead-QA-2026!`. Chỉ dùng ở localhost, không đưa các tài khoản/settings QA lên web thật. `--publish-pack` chỉ cho database QA cố định, xuất bản để kiểm thử chứ không đánh dấu nội dung đã được giáo viên duyệt.

Quên mật khẩu QA: dùng `qa-reader@example.test`, rồi xem `docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa logs --tail 80 web`. Không chia sẻ log chứa liên kết khôi phục đang có hiệu lực. QA dùng dữ liệu PostgreSQL tạm; xóa container database sẽ mất dữ liệu QA.
