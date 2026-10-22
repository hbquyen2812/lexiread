# Triển khai LexiRead lên VPS với HTTPS

Tài liệu này dành cho một VPS Linux, một domain riêng và nhóm người dùng nhỏ/closed beta. Cấu hình production dùng Caddy làm reverse proxy và tự cấp/gia hạn HTTPS; Gunicorn và PostgreSQL không được mở trực tiếp ra Internet.

## 1. Phạm vi đã sẵn sàng

- Landing page công khai; mọi API học tập yêu cầu đăng nhập.
- Đăng nhập bằng email; tài khoản do quản trị viên tạo, chưa có đăng ký công khai, xác minh email hoặc quên mật khẩu.
- Django/Gunicorn chạy bằng user không phải root; PostgreSQL chỉ nằm trong mạng Compose.
- Caddy mở cổng 80/443, chuyển HTTP sang HTTPS và proxy đến service `web`.
- Cookie đăng nhập/CSRF chỉ gửi qua HTTPS; host và CSRF origin bị giới hạn theo `DOMAIN`.
- Dependency Python được khóa trong `requirements.lock`.

Đây chưa phải cấu hình SaaS quy mô lớn: chưa kiểm thử tải/penetration, chưa có hàng đợi AI, SMTP, object storage hoặc rate limiter phân tán. Với website cá nhân hoặc closed beta ít người, có thể triển khai sau khi hoàn thành DNS, backup và kiểm tra bên dưới.

## 2. Chuẩn bị

1. VPS Linux có Docker Engine và Docker Compose plugin.
2. Domain, ví dụ `learn.example.com`, có bản ghi A/AAAA trỏ đúng IP VPS.
3. Firewall chỉ mở SSH, TCP 80, TCP 443 và UDP 443. Không mở 5432 hoặc 8000 ra Internet.
4. Clone repository vào VPS và đứng tại thư mục có `compose.yml`.

Tạo secret mà không cần cài dependency Python:

```bash
python3 scripts/init_env.py
chmod 600 .env
nano .env
```

Sửa tối thiểu:

```dotenv
DOMAIN=learn.example.com
DJANGO_DEBUG=false
DJANGO_HTTPS=true
TRUST_PROXY_HTTPS=true
DJANGO_HSTS_SECONDS=3600
DJANGO_HSTS_INCLUDE_SUBDOMAINS=false
DJANGO_HSTS_PRELOAD=false
AI_PROVIDER=none
```

Không thêm `https://` hoặc đường dẫn vào `DOMAIN`. Giữ `POSTGRES_PASSWORD` và `DJANGO_SECRET_KEY` ngẫu nhiên do script sinh. Chỉ tăng HSTS sau khi HTTPS đã ổn định; không bật includeSubDomains/preload nếu chưa hiểu ảnh hưởng lên toàn bộ domain.

## 3. Kiểm tra trước khi chạy

```bash
docker compose -f compose.yml -f compose.prod.yml config --quiet
docker compose -f compose.yml -f compose.prod.yml build --pull web
docker compose -f compose.yml -f compose.prod.yml run --rm --no-deps --entrypoint python web manage.py check --deploy
docker compose -f compose.yml -f compose.prod.yml run --rm --no-deps --entrypoint caddy caddy validate --config /etc/caddy/Caddyfile
```

Bốn lệnh lần lượt kiểm tra cấu hình Compose, build image bằng lockfile, chạy checklist production của Django và validate Caddyfile. Với cấu hình HSTS khởi đầu an toàn, Django dự kiến cảnh báo `security.W005` và `security.W021` vì chưa bật includeSubDomains/preload. Đây là chủ đích: không bật hai cờ đó chỉ để làm sạch cảnh báo. Các lỗi hoặc cảnh báo khác phải được hiểu và xử lý trước khi tiếp tục.

Sau khi mọi subdomain đều chạy HTTPS ổn định và bạn chủ động muốn tham gia preload, mới tăng `DJANGO_HSTS_SECONDS` tối thiểu một năm rồi cân nhắc hai cờ HSTS còn lại. Khi cả ba được cấu hình phù hợp, `check --deploy` không còn hai cảnh báo trên.

## 4. Khởi động và tạo quản trị viên

```bash
docker compose -f compose.yml -f compose.prod.yml up -d
docker compose -f compose.yml -f compose.prod.yml ps
docker compose -f compose.yml -f compose.prod.yml logs --tail=100 web caddy db
docker compose -f compose.yml -f compose.prod.yml exec web python manage.py createsuperuser
```

`web` tự chạy migration, nạp thư viện bài chuẩn và collectstatic trước khi Gunicorn khởi động. Truy cập `https://DOMAIN/`, đăng nhập bằng email đã nhập ở bước `createsuperuser`, rồi kiểm tra:

```bash
curl -I https://learn.example.com/
curl -fsS https://learn.example.com/health/
```

Thay domain ví dụ bằng domain thật. Caddy chỉ lấy được chứng chỉ công khai khi DNS đúng và cổng 80/443 truy cập được từ Internet.

## 5. Backup PostgreSQL

Tạo backup trước mỗi lần cập nhật và theo lịch hằng ngày:

```bash
mkdir -p backups
docker compose -f compose.yml -f compose.prod.yml exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "backups/lexiread-$(date +%F-%H%M).dump"
```

Kiểm tra file khác 0 byte, mã hóa nếu cần và sao chép sang máy/bucket khác VPS. Volume Docker không phải backup. Backup JSON trong giao diện hữu ích cho tiến độ cá nhân nhưng không chứa tài khoản/quyền hệ thống.

Khôi phục là thao tác phá dữ liệu hiện tại. Chỉ thực hiện sau khi đã giữ thêm một bản dump mới và tốt nhất thử trên VPS staging:

```bash
docker compose -f compose.yml -f compose.prod.yml stop caddy web
cat backups/FILE.dump | docker compose -f compose.yml -f compose.prod.yml exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" pg_restore --clean --if-exists --no-owner --single-transaction -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker compose -f compose.yml -f compose.prod.yml up -d web caddy
```

## 6. Cập nhật

```bash
git status
git pull --ff-only
docker compose -f compose.yml -f compose.prod.yml build --pull web
docker compose -f compose.yml -f compose.prod.yml up -d
docker compose -f compose.yml -f compose.prod.yml ps
docker compose -f compose.yml -f compose.prod.yml logs --tail=100 web caddy
```

Luôn backup database trước `git pull`. Migration chạy tự động khi container `web` mới khởi động. Nếu cập nhật lỗi, không tự ý chạy `down -v`; quay lại mã nguồn đã biết tốt và khôi phục dump khi migration không tương thích ngược.

## 7. Vận hành định kỳ

```bash
docker compose -f compose.yml -f compose.prod.yml exec web python manage.py prune_logs
docker compose -f compose.yml -f compose.prod.yml exec web python manage.py clearsessions
docker compose -f compose.yml -f compose.prod.yml logs --since=24h web caddy db
```

- Chạy backup hằng ngày và thử restore định kỳ.
- Chạy `prune_logs`/`clearsessions` mỗi tuần hoặc tháng.
- Theo dõi dung lượng disk, ngày hết hạn domain, lỗi 5xx và trạng thái container.
- Cập nhật dependency có kiểm soát: sửa `requirements.txt`, tạo lại lockfile trong môi trường sạch, chạy toàn bộ test rồi mới deploy.
- Giữ `AI_PROVIDER=none` cho đến khi đã đặt quota/ngân sách và chấp nhận nội dung bài được gửi đến provider.

## 8. Khi nào chưa nên mở rộng người dùng

Chưa mở public signup trước khi bổ sung xác minh email, luồng quên/đổi mật khẩu, chống bot/rate limit ở biên, điều khoản riêng tư, xóa tài khoản/dữ liệu, giám sát lỗi và kiểm thử tải. Hiện quản trị viên tạo tài khoản thủ công trong `/admin/`, phù hợp hơn cho website cá nhân hoặc nhóm thử nghiệm nhỏ.
