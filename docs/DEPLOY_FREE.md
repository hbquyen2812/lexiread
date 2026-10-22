# Deploy LexiRead miễn phí với Render và Neon

Phương án này dùng Render Free cho ứng dụng Django và Neon Free cho PostgreSQL. Không cần mua VPS hoặc domain: Render cấp địa chỉ `https://<ten-dich-vu>.onrender.com` và HTTPS tự động.

## Giới hạn cần biết

- Render Free ngủ sau 15 phút không có truy cập. Lượt mở đầu tiên sau đó có thể chờ khoảng một phút.
- Neon Free phù hợp dự án cá nhân, có 1 GB lưu trữ cho mỗi project và tự giảm compute khi không dùng.
- Đây là môi trường học tập/side project, không có SLA. Luôn xuất bản sao dữ liệu quan trọng.

## 1. Đưa mã nguồn lên GitHub

Thực hiện theo `docs/GITHUB_UPLOAD.md`. Không commit file `.env`.

## 2. Tạo PostgreSQL miễn phí trên Neon

1. Mở `https://console.neon.tech/`, đăng nhập và tạo project tên `lexiread`.
2. Chọn region gần Singapore nếu giao diện cung cấp.
3. Trong **Connect**, chọn **Pooled connection** và sao chép URL bắt đầu bằng `postgresql://`.
4. Giữ URL này bí mật. Không lưu vào GitHub, ảnh chụp hoặc tin nhắn công khai.

## 3. Deploy web miễn phí trên Render

1. Mở `https://dashboard.render.com/blueprints` và chọn **New Blueprint Instance**.
2. Kết nối GitHub và chọn repository LexiRead.
3. Render đọc `render.yaml`; giữ gói **Free** và region **Singapore**.
4. Khi được hỏi `DATABASE_URL`, dán URL **Pooled connection** từ Neon.
5. Chọn **Apply** và chờ build. Container tự chạy migration, nạp bài học và collectstatic.
6. Khi trạng thái thành **Live**, mở URL `https://lexiread-....onrender.com/health/`; kết quả phải là `ok`.

## 4. Tạo tài khoản quản trị đầu tiên

Render Free không có shell. Chạy lệnh này tại PowerShell trong `D:\LexiRead`; URL được nhập bằng `Read-Host` nên không xuất hiện trực tiếp trong lịch sử lệnh. Lệnh dùng image Docker đã build, không phụ thuộc package trong `.venv`:

```powershell
$env:DATABASE_URL = Read-Host "Dán Neon DATABASE_URL"
docker compose run --rm --no-deps -e DATABASE_URL="$env:DATABASE_URL" --entrypoint python web manage.py createsuperuser
Remove-Item Env:DATABASE_URL
```

Nhập một username nội bộ, email đăng nhập và mật khẩu mạnh. Sau đó đăng nhập website bằng **email** vừa nhập. Nếu lệnh lỗi, chạy `Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue` trước khi đóng terminal.

## 5. Mỗi lần cập nhật

```powershell
git add .
git commit -m "Mô tả thay đổi"
git push origin main
```

Render tự build lại sau mỗi commit. Không dùng `docker compose` trên Render; Compose vẫn dành cho chạy local hoặc VPS.

## 6. Sao lưu dữ liệu

Neon Free có snapshot giới hạn nhưng không nên coi là bản sao lưu duy nhất. Định kỳ dùng chức năng xuất JSON trong LexiRead và tải file về máy. Khi dữ liệu quan trọng hơn, dùng `pg_dump` hoặc nâng gói có backup theo lịch.
