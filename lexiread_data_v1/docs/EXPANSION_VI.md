# Mở rộng kho dữ liệu sau v1

## Một quy trình nhập dùng được lâu dài

1. **Chọn nguồn và lưu quyền sử dụng theo từng mục.** Bắt đầu từ `sources.json`. Trang đề chính thức chủ yếu để tham khảo/dẫn link. Với nguồn cấp phép mở, lưu URL của chính bài, tác giả, người dịch/họa sĩ nếu có, giấy phép, URL giấy phép và thay đổi đã thực hiện. Nhãn toàn website không thay cho quyền của một ảnh hoặc bài cụ thể.
2. **Nhập vào staging.** Lưu raw metadata và bản nội dung được phép sử dụng; gắn `content_origin` là `original_ai_authored`, `licensed_reuse` hoặc `public_domain_verified` đúng thực tế. Tách trường ngày truy cập với ngày xuất bản. Lưu bằng chứng quyền sử dụng và điều kiện riêng khi cần.
3. **Biên soạn bài học.** Chọn mục tiêu đọc, sau đó viết câu hỏi và lấy từ vựng từ chính văn bản. Với nội dung mới, thay đổi thật về chủ đề, cấu trúc và cách lập luận; không nhân hàng bằng cách thay tên người hoặc vài con số.
4. **Kiểm tra tự động và biên tập.** Kiểm tra ID, đáp án, từ trong bài, trích dẫn, số từ, distractor trùng, từ loại và nghĩa. Rà thủ công TFNG, suy luận, thông tin liên văn bản và phương án có thể cùng đúng. Thử với người học để hiệu chỉnh độ khó.
5. **Xuất bản có phiên bản.** Chỉ đưa bài đã duyệt lên luồng học. Giữ ID/phiên bản để lịch sử làm bài và flashcard không mất liên kết. Có trường `reviewed_by`, `reviewed_at`, `revision` trong hệ thống biên tập nếu ứng dụng cần.

## Ưu tiên mở rộng

| Nhóm | Nội dung nên bổ sung |
|---|---|
| Trẻ mới bắt đầu | Bài 30–60 từ có tranh hợp lệ, câu rất ngắn, audio được phép dùng, 3 lựa chọn nếu giao diện phù hợp |
| THCS | Tin nhắn, lịch trình, thông báo, bài đọc A1–A2, tìm thông tin và tham chiếu đại từ |
| THPT | Cloze, liên kết câu, suy luận, thái độ tác giả; nếu ôn kỳ thi cụ thể thì đối chiếu đề minh họa chính thức của kỳ thi đó |
| IELTS | Bài dài hơn, nhiều kiểu văn bản, matching features, table/flow-chart completion, sơ đồ được tự tạo; thiết kế full mock riêng nếu cần |
| TOEIC | Bổ sung Part 7 ba văn bản, email đối chiếu hóa đơn/lịch, sentence insertion, distractor theo mốc thời gian và điều kiện |
| Từ vựng | Nghĩa theo ngữ cảnh, word families, collocation, paraphrase, ví dụ và bài tập ứng dụng sau khi đọc |

Để kho bài phong phú mà vẫn kiểm soát được, mở rộng theo lô nhỏ đủ để giáo viên đọc hết. Theo dõi tỷ lệ làm đúng và phản hồi “có hai đáp án đúng/giải thích chưa rõ” để ưu tiên sửa; không dùng tỷ lệ làm đúng của một nhóm nhỏ như bằng chứng đã chuẩn hóa CEFR hay band thi.

## Về nguồn mở được khảo sát

StoryWeaver là ứng viên cho truyện trẻ em vì phần thông tin chính thức trong kết quả tìm kiếm nêu CC BY 4.0. Phiên khảo sát chưa mở được trang chi tiết qua công cụ và không tải truyện. Khi triển khai nhập thật, kiểm tra quyền trên từng truyện trước và giữ ghi công. OpenLearn có hạn chế phi thương mại và các ngoại lệ được nêu ở trang copyright; không mặc định phù hợp website thương mại.

Tham chiếu: [StoryWeaver Attribution](https://storyweaver.org.in/en/attributions), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [OpenLearn Copyright](https://about.open.ac.uk/strategy-and-policies/policies-and-statements/copyright-openlearn), [ETS Permissions](https://www.ets.org/legal/permissions.html).
