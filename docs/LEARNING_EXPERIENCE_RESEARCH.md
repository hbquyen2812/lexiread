# Nghiên cứu trải nghiệm học và thư viện chiến thuật — 26/10/2026

## Phạm vi và kết quả nội dung

Đã đọc các nguồn chính thức của IELTS, British Council, IDP, ETS và IIBC; đồng thời xem cách tổ chức hoạt động học của British Council LearnEnglish và ReadTheory. Không lấy thiết kế, câu hỏi, passage hay đáp án của các website này để tái xuất bản.

`data/strategy_guides.json` có **18 hướng dẫn tự biên soạn bằng tiếng Việt: 12 IELTS và 6 TOEIC**, gồm 55 bước thực hành, 36 lỗi cần tránh và 18 ví dụ mini nguyên bản. Mỗi ví dụ có đoạn tiếng Anh, câu hỏi, đáp án và giải thích tiếng Việt. Đây là bài hướng dẫn ngắn, không phải đề thi chính thức, bài đo CEFR hoặc lời hứa đạt band/điểm. Thời lượng 5–8 phút là ước tính đọc/luyện hướng dẫn, không phải giới hạn của một dạng câu hỏi trong kỳ thi.

IELTS gồm TFNG, YNNG, headings, information, features, sentence endings, multiple choice, sentence completion, summary/note/table, flow-chart/diagram, short answers và quản lý thời gian/paraphrase. TOEIC gồm Part 5 ngữ pháp/từ vựng, Part 6 liên kết/chọn câu thiếu và Part 7 một/nhiều văn bản. Phần suy luận được lồng vào Part 7, phần chèn câu cũng được nhắc trong cách đọc một văn bản.

Nguồn chính thức dùng để đối chiếu tên dạng câu hỏi, cơ chế trả lời và giới hạn của định dạng. Các bước diễn giải, câu hỏi mini, tình huống và ví dụ trong thư viện là nội dung biên tập riêng. Không dịch lại hoặc rút gọn một đề thi có bản quyền để đưa vào website.

## Quan sát và quyết định thiết kế

| Quan sát từ nguồn | Ý tưởng phù hợp LexiRead | Giới hạn cần giữ |
| --- | --- | --- |
| [British Council LearnEnglish B1](https://learnenglish.britishcouncil.org/free-resources/reading/b1) tổ chức bài với hoạt động chuẩn bị, văn bản và bài kiểm tra hiểu. | Đưa hướng dẫn dạng bài và một ví dụ nhỏ trước khi chuyển sang luyện; giữ người học biết bước tiếp theo. | Không sao chép hoạt động hoặc nội dung bài của nguồn. |
| [ReadTheory](https://readtheory.org/) giới thiệu mục tiêu do người học đặt và khả năng theo dõi phát triển. | Cho người học chọn trọng tâm, xem lại mục đã học, đánh dấu nội dung cần ôn; nối với mục tiêu/ngày và tiến độ đã có. | Đây là cảm hứng sản phẩm, không phải bằng chứng rằng LexiRead có hệ thống thích ứng hay đo năng lực tương đương ReadTheory. |
| [British Council: Reading preparation](https://takeielts.britishcouncil.org/prepare/ielts-academic/reading) phân biệt đọc lấy ý chung, tìm dữ kiện và đọc kỹ. | Viết từng bước gắn với thao tác cụ thể và yêu cầu người học chỉ ra bằng chứng. | Không biến “skim trước” thành một quy tắc cứng cho mọi câu hỏi. |
| [IDP: matching features](https://ielts.idp.com/prepare/article-ielts-reading-test-strategies-matching-features-questions) chú trọng quan hệ ý, cách diễn đạt tương đương và những lần tên xuất hiện. | Hiển thị bẫy thường gặp ngay cạnh ví dụ; giải thích tại sao đáp án nhiễu sai. | Không suy ra rằng tất cả dạng bài có cùng thứ tự đáp án. |
| [IELTS: matching headings](https://ielts.org/news-and-insights/how-to-prepare-learners-for-matching-headings-task-on-the-ielts-reading-test) phân biệt ý chính với chi tiết và thừa nhận câu chủ đề có thể ở vị trí khác. | Cho người học tự tóm tắt đoạn rồi mới xem lời giải; tránh mẹo “chỉ đọc câu đầu”. | Không dùng vị trí câu làm bằng chứng duy nhất. |
| [ETS preparation](https://www.ets.org/toeic/test-takers/prepare.html) tập hợp tài liệu theo đúng loại bài thi và nêu các hoạt động phản ánh công việc. | Phân biệt TOEIC L&R với TOEIC Bridge, đặt ngữ pháp và từ vựng trong email/lịch/đơn hàng ngắn. | Không quy đổi điểm bài mini thành điểm TOEIC. |

Các tính năng khuyến nghị cho UI trong đợt này: tìm/lọc chiến thuật theo kỳ thi và dạng câu hỏi; thử trả lời trước khi mở đáp án; hiện lý do bằng chứng; đánh dấu đã học/cần ôn; liên kết sang thư viện luyện hoặc nguồn chính thức. Đây là các quyết định thiết kế rút ra từ quan sát, không phải khẳng định hiệu quả học tập đã được nghiên cứu cho LexiRead. Kết quả tích hợp UI và browser QA được ghi trong báo cáo triển khai của đợt cập nhật.

## Nguồn về cấu trúc đề

- [IELTS Academic Reading format](https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-reading): nhóm dạng bài và yêu cầu trả lời.
- [IDP Academic Reading question types](https://ielts.idp.com/prepare/article-question-types-academic-reading): khác biệt giữa completion, diagram và matching; phải tuân thủ hướng dẫn riêng của dạng bài.
- [British Council Reading task types](https://takeielts.britishcouncil.org/what-is-ielts/how-it-works/test-format/reading): phân biệt thông tin và quan điểm tác giả.
- [British Council context clues](https://takeielts.britishcouncil.org/blog/mastering-context-clues-boost-your-ielts-reading-skills): ngữ cảnh và diễn đạt tương đương.
- [ETS TOEIC sample PDF](https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-sample-test.pdf): đối chiếu hình thức Parts 5–7. Nội dung PDF không được chép vào thư viện tự soạn.
- [IIBC official TOEIC format/sample collection](https://www.iibc-global.org/toeic/test/lr/about/format.html): nguồn TOEIC tại Nhật Bản sử dụng thương hiệu/nội dung theo giấy phép ETS; điều hướng chủ yếu tiếng Nhật.

## Đợt mở rộng liên kết công khai

Danh mục tăng từ **23 lên 33 tài nguyên**: thêm 7 worksheet Reading của British Council, 2 sổ tay thí sinh ETS và 1 tuyển tập mẫu tương tác IIBC. Tổng hiện tại: **28 IELTS, 5 TOEIC**. 28 tài nguyên có liên kết đáp án; trong worksheet, phần chữa nằm cùng PDF. Đây là số tài nguyên, không phải số đề đầy đủ hoặc số tập câu hỏi độc nhất.

Đã theo liên kết từ [trang lesson plans Reading hiện tại](https://takeielts.britishcouncil.org/teach-ielts/teaching-resources/lesson-plans-reading) tới bảy PDF `/sites/default/files/2026-06/`. Một số URL PDF cũ vẫn hiện trong tìm kiếm nhưng chuyển hướng về trang chung; chúng không được thêm. Các PDF hiện tại dài lần lượt 10, 9, 15, 10, 14, 10 và 13 trang, có hướng dẫn cho giáo viên và bài luyện. Các bài mẫu có thể xuất hiện lại giữa bộ tuyển tập và worksheet; không khẳng định đây là các đề hoàn toàn mới.

IIBC được lưu thành **một** tuyển tập. Không tách sáu trang Part thành sáu “đề mới”, vì ví dụ của IIBC có thể trùng với PDF ETS. Hai sổ tay ETS được ghi rõ là tài liệu hướng dẫn, không phải đề mới. Không tải hay lưu toàn bộ PDF/HTML vào repository. URL, nhãn, quyền sử dụng, biến thể bài thi và ngày kiểm tra nằm trong catalog.

`learning_expansion_crawl.json` và `learning_expansion_health.json` giữ kết quả crawler thực tế, kể cả khi robots không cho phép/không truy cập được. Crawler không tự xuất bản và không né kiểm soát truy cập. Việc công cụ web mở được tài liệu được ghi tách biệt với kết quả crawler; HTTP/đọc PDF không chứng minh toàn bộ tương tác bên thứ ba hoạt động.

## API và kiểm tra

`learning.services.strategy_guides.strategy_guides(exam=None)` trả bản sao độc lập; bộ lọc nhận `ielts` hoặc `toeic`. `strategy_guide(id)` trả một hướng dẫn hoặc `None`. Loader không truy cập database/mạng và không chứa trạng thái người dùng. Những trường hợp ID trùng, URL không chính thức/không an toàn, thiếu bước/giải thích, đáp án không thuộc các lựa chọn, track không khớp hoặc thời lượng không hợp lệ bị từ chối.

```powershell
.\.venv\Scripts\python.exe scripts/author_strategy_guides.py
.\.venv\Scripts\python.exe -m unittest tests.test_strategy_guides tests.test_public_resources -v
.\.venv\Scripts\python.exe scripts/crawl_public_resources.py --source british-council-reading-lessons --source iibc-toeic-samples --output data/public_sources/learning_expansion_crawl.json
.\.venv\Scripts\python.exe scripts/crawl_public_resources.py --check-links --output data/public_sources/learning_expansion_health.json
```

16 kiểm thử dữ liệu/trust boundary đã PASS trên Python local. Chúng không thay thế kiểm thử trình duyệt hay thẩm định học thuật bởi giảng viên IELTS/TOEIC.

Lần crawler cuối: IIBC HTTP 200, phát hiện 6 liên kết mẫu; BC bỏ qua do robots. Lần health cuối: 50 URL, 41 OK, 9 PDF BC bị bỏ qua và vẫn ghi trạng thái đó. Không gặp 404 trong các URL được phép kiểm tra.
