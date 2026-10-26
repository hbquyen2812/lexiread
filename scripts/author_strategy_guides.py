"""Rebuild the original Vietnamese strategy library (no downloaded exam text)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAT = ('IELTS Academic Reading: official task format', 'https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-reading')
SKIM = ('British Council: reading preparation and reading skills', 'https://takeielts.britishcouncil.org/prepare/ielts-academic/reading')
IDP = ('IDP: Academic Reading question types', 'https://ielts.idp.com/prepare/article-question-types-academic-reading')
ETS = ('ETS: official TOEIC preparation materials', 'https://www.ets.org/toeic/test-takers/prepare.html')
ETS_SAMPLE = ('ETS: TOEIC Listening and Reading sample test', 'https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-sample-test.pdf')
GUIDES = []


def add(key, title, summary, minutes, kinds, steps, traps, passage, question, answer, explanation, options=None, sources=None, accepted_answers=None):
    exam = key.split('-')[0]
    example = dict(passage=passage, question=question, answer=answer, explanation_vi=explanation)
    if options:
        example['options'] = options
    if accepted_answers:
        example['accepted_answers'] = accepted_answers
    GUIDES.append(dict(id=key, exam=exam, title=title, summary_vi=summary, duration_minutes=minutes,
        question_types=kinds, steps=[dict(title=title, body=body) for title, body in steps],
        traps=traps, worked_example=example, practice_query=dict(track=exam, kind=kinds[0]),
        sources=[dict(title=title, url=url) for title, url in (sources or ([FORMAT] if exam == 'ielts' else [ETS_SAMPLE]))],
        checked_at='2026-10-26'))


add('ielts-tfng', 'True / False / Not Given: sai hay chưa được nói tới?',
    'Phân biệt “bài nói ngược lại” với “bài chưa cho biết”. Chỉ dựa vào bài đọc để chọn đáp án, dù bạn đã biết thêm về chủ đề.', 6, ['tfng'],
    [('Xem câu hỏi nói về ai và điều gì', 'Chú ý người hoặc vật được nói tới, hành động, thời điểm và các từ như all, only, most. Một câu dài có thể đúng ở phần này nhưng sai ở phần khác.'),
     ('Tìm câu trong bài để đối chiếu', 'Tìm tên, con số hoặc ý tương tự trong bài. Đọc thêm câu trước và sau để hiểu các từ như he, they đang chỉ ai, và có điều kiện hay ngoại lệ nào không.'),
     ('Chọn đáp án và nói rõ lý do', 'Chọn TRUE nếu bài xác nhận, FALSE nếu bài nói ngược lại, NOT GIVEN nếu chưa đủ thông tin để kết luận. Thử giải thích ngắn vì sao bạn chọn trước khi xem đáp án.')],
    ['Bài có thể diễn đạt cùng một ý bằng từ khác. Không thấy từ giống câu hỏi chưa có nghĩa là NOT GIVEN.', 'Gặp từ “all” cũng chưa thể chọn FALSE. Hãy kiểm tra bài nói về tất cả hay chỉ một số.'],
    'The garden opens to members at 8 a.m. on Saturdays. Visitors who are not members can enter after 10 a.m. The entrance fee is the same for both groups.',
    'Non-members pay more to enter the garden. Choose TRUE, FALSE or NOT GIVEN.', 'FALSE',
    'Bài nói hai nhóm trả cùng một mức phí (“the same”), trái với “pay more”, nên chọn FALSE. Hai nhóm được vào lúc khác nhau, nhưng giờ vào không cho biết ai trả nhiều tiền hơn.',
    ['TRUE', 'FALSE', 'NOT GIVEN'], sources=[FORMAT, ('British Council: Reading question types', 'https://takeielts.britishcouncil.org/what-is-ielts/how-it-works/test-format/reading')])

add('ielts-ynng', 'Yes / No / Not Given: ai đang nói điều gì?',
    'Tìm đúng ý kiến của tác giả. Đừng nhầm lời người khác được nhắc trong bài với điều tác giả tin hoặc đồng ý.', 6, ['ynng'],
    [('Xem ý kiến đó là của ai', 'Phân biệt lời tác giả với lời nhà nghiên cứu hoặc người được trích dẫn. “Some critics argue” chỉ cho biết ý kiến của một số người phê bình, chưa cho biết tác giả có đồng ý hay không.'),
     ('Chú ý chỗ tác giả đổi ý hoặc giới hạn ý', 'Đọc kỹ however, although, yet. So các từ may, likely, essential, impossible với câu hỏi: tác giả chỉ nói có thể, hay khẳng định chắc chắn?'),
     ('So cả nhận định với ý tác giả', 'Chọn YES nếu nhận định đúng với quan điểm tác giả, NO nếu trái ngược, NOT GIVEN nếu tác giả chưa nói rõ về điều được hỏi. Dùng đúng YES / NO / NOT GIVEN theo yêu cầu đề.')],
    ['Tác giả nêu một sự việc chưa có nghĩa là họ ủng hộ giải pháp liên quan đến sự việc đó.', 'Đừng ghi TRUE/FALSE khi đề yêu cầu YES/NO.'],
    'Some managers believe that every meeting should be online. I find video calls useful for routine updates, but difficult negotiations still benefit from people sharing a room.',
    'The writer believes that all meetings should take place online.', 'NO',
    'Tác giả thấy họp video phù hợp với việc cập nhật thường lệ, nhưng vẫn muốn gặp trực tiếp khi đàm phán khó. Vì vậy, tác giả không cho rằng mọi cuộc họp đều nên diễn ra trực tuyến. “Some managers” là ý của người khác.',
    ['YES', 'NO', 'NOT GIVEN'])

add('ielts-headings', 'Matching headings: đặt tên cho cả đoạn',
    'Chọn tiêu đề nói được ý chính của cả đoạn. Một chi tiết nổi bật hoặc một từ giống trong bài chưa đủ để chọn.', 7, ['matching_heading'],
    [('Tóm tắt đoạn bằng vài từ', 'Đọc đoạn rồi thử tóm tắt bằng 5–8 từ của bạn. Câu đầu và cuối thường giúp định hướng; nếu chưa rõ ý, hãy đọc kỹ cả phần giữa.'),
     ('So các tiêu đề dễ nhầm', 'Đoạn đang nói về nguyên nhân hay kết quả, khó khăn hay giải pháp, quá khứ hay tương lai? Chọn tiêu đề phù hợp với phần lớn nội dung của đoạn.'),
     ('Xem tiêu đề có vừa với cả đoạn không', 'Loại tiêu đề chỉ nói về một ví dụ nhỏ hoặc bao quát quá nhiều điều mà đoạn không đề cập. Ghi đúng mã tiêu đề; nếu còn phân vân, đánh dấu để quay lại.')],
    ['Không có quy tắc ý chính luôn nằm ở câu đầu.', 'Một tiêu đề có cùng từ “water” chưa chắc đúng với đoạn nói về giảm thất thoát nước.'],
    'The town once repaired pipes only after residents reported a leak. It now uses sensors to identify unusual water use overnight. Repair teams receive alerts before most residents notice a problem. This change has reduced the time taken to find hidden leaks.',
    'Choose the best heading for this paragraph.', 'A new way to detect leaks earlier',
    'Đoạn so sánh cách phát hiện rò rỉ trước đây với cách dùng cảm biến, rồi nêu lợi ích của việc phát hiện sớm. Bài không nói về giá nước, cũng không nói rằng có cảm biến thì không cần sửa ống.',
    ['The rising cost of household water', 'A new way to detect leaks earlier', 'Why pipe repairs are no longer necessary'],
    sources=[('IELTS: preparing for matching headings', 'https://ielts.org/news-and-insights/how-to-prepare-learners-for-matching-headings-task-on-the-ielts-reading-test'), FORMAT])

add('ielts-matching-information', 'Matching information: chi tiết này nằm ở đoạn nào?',
    'Tìm đoạn chứa ví dụ, lý do, phép so sánh hoặc kết quả mà câu hỏi yêu cầu. Bạn cần tìm chi tiết cụ thể, không phải ý chính của cả đoạn.', 7, ['matching_information'],
    [('Biết mình cần tìm gì', 'Đề đang yêu cầu một ví dụ, lời giải thích, số liệu hay ý kiến trái chiều? Xác định rõ trước khi tìm, để không nhầm với dạng chọn tiêu đề.'),
     ('Ghi nhanh nội dung từng đoạn', 'Ghi vài từ cho mỗi đoạn và chú ý tên riêng, con số dễ tìm lại. Câu hỏi có thể diễn đạt lại ý trong bài bằng từ khác.'),
     ('Chỉ ra câu giúp bạn chọn', 'Tìm câu có đủ chi tiết được hỏi. Kiểm tra đề có cho dùng lại một chữ cái không; đừng cho rằng thứ tự câu hỏi luôn trùng với thứ tự các đoạn.')],
    ['Đoạn có cùng chủ đề chưa chắc chứa chi tiết được yêu cầu.', 'Không tự loại một đoạn đã dùng nếu hướng dẫn cho phép dùng lại.'],
    'A. The library lending scheme began in 2018 with forty donated tools.\nB. Staff ask borrowers to attend a short safety demonstration because unfamiliar equipment can cause injuries.\nC. In the past year, residents borrowed drills more often than any other tool.',
    'Which paragraph explains a rule for borrowers?', 'B',
    'Đoạn B yêu cầu người mượn tham gia hướng dẫn an toàn và giải thích rằng thiết bị lạ có thể gây chấn thương. A nói về thời điểm thư viện bắt đầu; C nói về loại dụng cụ được mượn nhiều nhất.', ['A', 'B', 'C'])

add('ielts-matching-features', 'Matching features: nối phát biểu với đúng người',
    'Xác định ai nêu ý kiến hoặc có phát hiện được hỏi. Đọc cả những chỗ tên được nhắc lại hoặc thay bằng he, she, this team.', 6, ['matching_features'],
    [('Tìm các tên hoặc mốc trong lựa chọn', 'Ghi tên người, năm hoặc nhóm được cho, rồi tìm tất cả những chỗ bài nhắc tới chúng.'),
     ('Xem mỗi người đã làm gì', 'Chú ý các từ proposed, challenged, observed, repeated: ai đề xuất, phản đối, quan sát hay nhắc lại ý đó? Theo dõi he, she, this team để không nhầm người.'),
     ('So cả ý trước khi ghép', 'Kiểm tra phát biểu có đúng với người hoặc nhóm đó không. Tên đứng gần từ khóa chưa đủ để chọn. Chỉ dùng lại một lựa chọn nếu đề cho phép.')],
    ['Người nhắc lại một ý để phản đối không nhất thiết là người đề xuất ý đó.', 'Không dừng ở lần xuất hiện đầu tiên của tên.'],
    'Dr Lin suggested that shaded streets might encourage walking. Dr Rao tested the idea by counting pedestrians on shaded and unshaded routes. Her results supported Lin’s suggestion, although she warned that the study covered only one neighbourhood.',
    'Who collected evidence to test the suggestion?', 'Dr Rao',
    'Lin đưa ra ý tưởng; Rao kiểm tra ý tưởng đó bằng cách đếm người đi bộ. “Her results” vẫn nói về Rao. Câu hỏi cần người thu thập bằng chứng, nên chọn Dr Rao.', ['Dr Lin', 'Dr Rao'],
    sources=[('IDP: strategies for matching features', 'https://ielts.idp.com/prepare/article-ielts-reading-test-strategies-matching-features-questions')])

add('ielts-sentence-endings', 'Matching sentence endings: đúng ngữ pháp chưa đủ',
    'Chọn phần kết thúc vừa đúng ngữ pháp vừa đúng ý bài đọc. Đặc biệt chú ý lý do, điều kiện và mục đích của hành động.', 6, ['matching_sentence_endings'],
    [('Đọc đầu câu trước', 'Xem câu nói về ai, làm gì và còn thiếu thông tin nào: lý do, kết quả, đối tượng hay điều kiện.'),
     ('Tìm ý đó trong bài', 'Dùng tên hoặc từ khóa ở đầu câu để tìm chỗ liên quan. Đọc trọn câu trong bài để hiểu ý trước khi thử ghép.'),
     ('Đọc lại câu sau khi ghép', 'Loại lựa chọn đúng ngữ pháp nhưng nói sai người hoặc đảo ngược nguyên nhân và kết quả. Ghi chữ cái của phần kết thúc theo yêu cầu đề.')],
    ['Số lựa chọn có thể nhiều hơn số câu cần ghép.', 'Một kết thúc nghe hợp lý ngoài đời vẫn sai nếu đoạn không nói như vậy.'],
    'The team moved the seedlings indoors because frost was forecast for the following night. They planned to return the plants to the garden when the cold weather passed.',
    'The seedlings were moved indoors ...', 'because a cold night was expected.',
    '“Frost was forecast” tương đương dự báo một đêm lạnh. Đoạn không nói cây đã chết hay việc chuyển cây làm cho trời lạnh.',
    ['because a cold night was expected.', 'because all the plants had died.', 'so that the weather would become colder.'], sources=[IDP])

add('ielts-multiple-choice', 'Multiple choice: chọn đúng và biết vì sao',
    'Đọc rõ câu hỏi cần gì. Với mỗi lựa chọn, tìm chi tiết trong bài để giữ lại hoặc loại bỏ.', 6, ['multiple_choice'],
    [('Xem đề cần chọn mấy đáp án', 'Đề yêu cầu một hay nhiều lựa chọn? Chú ý những từ như main reason, purpose, according to, likely để biết chính xác điều đang được hỏi.'),
     ('Thử trả lời bằng lời của bạn', 'Tìm thông tin trong bài rồi tự trả lời ngắn trước khi so với các lựa chọn. Cách này giúp bạn ít bị cuốn theo một đáp án nghe có vẻ hợp lý.'),
     ('Kiểm tra từng lựa chọn', 'Loại đáp án không được nhắc tới, sai thời điểm, sai người, khẳng định quá mức hoặc chỉ đúng một phần. Nếu đề cần nhiều đáp án, hãy tìm căn cứ cho từng đáp án.')],
    ['Trùng từ với bài không chứng minh đáp án đúng.', 'Không chọn một sự thật có trong bài nếu nó không trả lời đúng câu hỏi.'],
    'The museum introduced evening visits after local teachers said that school trips could not fit into the daytime timetable. The museum also hoped to sell more guidebooks, but improving access for school groups was its main aim.',
    'Why did the museum primarily introduce evening visits?', 'To make visits easier for school groups',
    'Câu cuối nói rõ mục tiêu chính là giúp các nhóm học sinh dễ đến tham quan hơn. Bán thêm sách chỉ là mong muốn phụ, nên không trả lời đúng từ “primarily”.',
    ['To make visits easier for school groups', 'To stop selling guidebooks', 'To reduce the number of teachers', 'To replace all daytime visits'], sources=[IDP])

add('ielts-sentence-completion', 'Sentence completion: điền đúng từ, không vượt giới hạn',
    'Xem chỗ trống cần loại từ nào để tìm nhanh hơn. Khi điền, lấy từ đúng theo yêu cầu đề và kiểm tra số từ.', 5, ['gap_fill', 'sentence_completion'],
    [('Đọc kỹ giới hạn từ', 'Chú ý ONE WORD ONLY hoặc giới hạn khác của đề. Kiểm tra bạn phải lấy từ trong bài hay chọn từ một danh sách.'),
     ('Xem chỗ trống cần gì', 'Đọc phần trước và sau chỗ trống: cần danh từ, con số, tính từ hay động từ? Dự đoán để biết mình cần tìm gì, không tự thay đáp án bằng một từ đồng nghĩa.'),
     ('Điền rồi đọc lại cả câu', 'Đối chiếu với bài và kiểm tra chính tả, số ít/số nhiều, số từ. Nếu trước chỗ trống đã có a, an hoặc the, đừng chép thêm lần nữa.')],
    ['Nếu đề yêu cầu lấy từ trong bài, đừng thay bằng một từ đồng nghĩa bạn tự nghĩ ra.', 'Đừng thêm từ cho câu nghe thuận tai nếu như vậy sẽ vượt giới hạn.'],
    'Before shipping, the company places each glass bowl in a cardboard box. A layer of wool cushions the bowl and prevents it from moving during transport.',
    'Complete the sentence. ONE WORD ONLY from the passage: The bowls are protected by a layer of ______.', 'wool',
    'Sau “a layer of” cần tên vật liệu. Bài nói wool là lớp đệm giữ bát không xê dịch, nên chỉ điền wool. Chép cả “a layer of wool” sẽ lặp phần đề đã cho và vượt giới hạn một từ.')

add('ielts-summary-table', 'Summary, note và table: nhìn tổng thể trước khi điền',
    'Đọc cả phần tóm tắt, ghi chú hoặc bảng để biết mỗi chỗ trống cần thông tin gì và đang nói về ai, điều gì.', 7, ['summary_completion', 'note_completion', 'table_completion', 'gap_fill'],
    [('Đọc phần đề đã cho sẵn', 'Xem tiêu đề, tên cột, từng hàng và những chỗ đã có thông tin. Hiểu phần này đang tóm tắt điều gì trước khi tìm từng từ.'),
     ('Tìm đúng chỗ trong bài', 'Dùng thông tin đã cho để tìm đoạn liên quan. So các ô với nhau và với bài đọc; đừng cho rằng mọi đáp án đều xuất hiện theo thứ tự câu hỏi.'),
     ('Điền theo đúng yêu cầu', 'Nếu đề cho danh sách, chọn theo hướng dẫn. Nếu lấy từ trong bài, giữ đúng giới hạn từ. Đọc lại cả phần tóm tắt hoặc hàng trong bảng để xem ý đã hợp lý chưa.')],
    ['Hai hàng có thể cùng nói về một vật liệu nhưng hỏi mục đích khác nhau.', 'Nếu từ đã chọn đúng nghĩa nhưng không khớp ngữ pháp của câu, hãy kiểm tra lại.'],
    'The trial compared two roof surfaces. White tiles reflected sunlight, while dark tiles absorbed more heat. Sensors showed that the room beneath the white tiles stayed cooler during the afternoon.',
    'Complete the note. ONE WORD ONLY: White tiles kept the room cooler because they ______ sunlight.', 'reflected',
    'Bài nói white tiles “reflected sunlight”, nên điền reflected. Absorbed nói về dark tiles, không phải loại ngói được hỏi. Đề yêu cầu lấy từ trong bài, vì vậy không tự đổi reflected thành reflect.', sources=[IDP])

add('ielts-flowchart-diagram', 'Flow-chart và diagram: theo mũi tên, tìm đúng bộ phận',
    'Nhìn kỹ các bước và vị trí trên sơ đồ. Bài đọc có thể dùng cách diễn đạt khác để mô tả cùng một quy trình hoặc thiết bị.', 7, ['flowchart_completion', 'diagram_completion', 'gap_fill'],
    [('Xem sơ đồ đang mô tả gì', 'Nếu là quy trình, đọc theo chiều mũi tên. Nếu là hình có nhãn các bộ phận, xem chính xác đầu mũi tên đang chỉ vào đâu.'),
     ('Tìm từ chỉ thứ tự và vị trí', 'Chú ý then, before, beneath, outlet để hiểu các bước và vị trí. Đọc kỹ phần mô tả tương ứng; đáp án không nhất thiết xuất hiện theo thứ tự câu hỏi.'),
     ('So lại tên gọi và số từ', 'Kiểm tra từ vừa chọn có đúng bộ phận, chức năng hoặc vị trí được hỏi không. Đừng lấy nhầm tên bên cạnh; soát chính tả và giới hạn từ trước khi đi tiếp.')],
    ['Không dùng kiến thức khoa học bên ngoài để điền thay cho thông tin trong bài.', 'Không mặc định mọi sơ đồ được đọc từ trái sang phải.'],
    'The collected rainwater first passes through a screen that removes leaves. It then enters a tank, where sand settles at the bottom. Finally, a pump sends the water to the vegetable beds.',
    'Complete the flow-chart. ONE WORD ONLY: Screen removes leaves → water enters a ______ → pump supplies the beds.', 'tank',
    'First, then và finally cho biết thứ tự ba bước. Nước đi qua screen rồi vào tank, nên điền tank. Sand là cát lắng ở đáy bể, không phải nơi nước đi vào tiếp theo.', sources=[IDP])

add('ielts-short-answers', 'Short answers: trả lời đúng trọng tâm và đủ ngắn',
    'Xem câu hỏi cần tên người, địa điểm, thời gian hay lý do. Chọn một cụm ngắn trong bài, nhưng vẫn đủ để trả lời rõ ràng.', 5, ['short_answer'],
    [('Xem từ hỏi cần thông tin gì', 'Who hỏi người, where hỏi nơi chốn, how many hỏi số lượng. Đọc cả phần còn lại của câu hỏi để biết đúng sự việc cần tìm.'),
     ('Tìm thông tin và đọc câu xung quanh', 'Kiểm tra đúng người, thời điểm và hành động. Nếu bài nhắc nhiều nơi, tìm nơi diễn ra việc được hỏi, không chọn địa điểm đầu tiên bạn thấy.'),
     ('Trả lời gọn trong giới hạn', 'Lấy từ trong bài nếu đề yêu cầu. Giữ những từ cần thiết để đáp án rõ nghĩa, không chép lại cả câu và nhớ đếm số từ.')],
    ['Không cần viết cả câu nếu đề chỉ yêu cầu một cụm ngắn.', 'Đừng rút ngắn đến mức mất từ giúp phân biệt đáp án, chẳng hạn north trong north entrance.'],
    'Volunteers should meet at the north entrance at nine o’clock. Tools will be distributed in the courtyard, and refreshments will be available in the old kitchen after the work is finished.',
    'Where will volunteers receive their tools? NO MORE THAN TWO WORDS from the passage.', 'the courtyard',
    '“Receive their tools” nói cùng ý với “tools will be distributed”: nhận dụng cụ. Việc này diễn ra ở the courtyard. Cả the courtyard (hai từ) và courtyard (một từ) đều trả lời đủ ý. North entrance là nơi tập trung, còn old kitchen là nơi dùng đồ ăn nhẹ.', accepted_answers=['the courtyard', 'courtyard'])

add('ielts-time-paraphrase', 'Đọc đúng ý và biết khi nào nên chuyển câu',
    'Luyện cách nhận ra cùng một ý được viết bằng từ khác, dành thời gian hợp lý cho câu khó và học lại từ những lỗi vừa mắc.', 8, ['paraphrase', 'time_management'],
    [('Chọn một điều muốn làm tốt hơn', 'Mỗi lượt luyện, tập trung vào một việc: phân biệt NOT GIVEN, tìm ý chính hoặc tránh vượt giới hạn từ. Dùng đồng hồ để biết mình đang mất thời gian ở đâu, không vội đoán chỉ vì thấy đồng hồ chạy.'),
     ('So cả ý, đừng chỉ so từ', 'Xem ai làm gì, điều gì gây ra kết quả nào và câu nói có giới hạn không. Hai câu có từ đồng nghĩa vẫn có thể nói ngược nhau nếu đổi người, mức độ hoặc nguyên nhân và kết quả.'),
     ('Tạm bỏ qua câu khó để quay lại', 'Nếu đã tìm ở phần liên quan mà vẫn chưa rõ, đánh dấu chỗ phân vân rồi làm câu khác. Chừa thời gian cuối để quay lại câu bỏ trống và soát giới hạn từ.'),
     ('Chữa kỹ một lỗi vừa mắc', 'Ghi đáp án bạn đã chọn, câu trong bài cho thấy đáp án đúng và lý do bạn nhầm. Sau đó thử một câu cùng dạng. Thời gian gợi ý cho bài mini chỉ giúp chia buổi luyện, không phải quy tắc cho đề thật.')],
    ['Có từ đồng nghĩa chưa chắc hai câu đã cùng nghĩa.', 'IELTS Reading có tổng cộng 60 phút. Hãy điều chỉnh cách chia thời gian theo khả năng và bài đọc, thay vì cố theo một mốc cố định.'],
    'After the booking form was shortened, fewer customers abandoned their reservations halfway through.',
    'Which sentence preserves the meaning?', 'A simpler form was followed by fewer unfinished bookings.',
    'Trong ngữ cảnh này, mẫu được rút gọn (shortened) được diễn đạt lại là đơn giản hơn (simpler); việc bỏ dở giữa chừng là unfinished bookings. Đáp án giữ đúng ý: sau khi rút gọn mẫu, ít lượt đặt chỗ bị bỏ dở hơn. Bài không nói tất cả khách đều hoàn tất.',
    ['A simpler form was followed by fewer unfinished bookings.', 'A shorter form made every customer finish a booking.', 'Shorter forms caused more customers to abandon their bookings.'], sources=[SKIM, ('British Council: context clues and paraphrasing', 'https://takeielts.britishcouncil.org/blog/mastering-context-clues-boost-your-ielts-reading-skills')])

add('toeic-part5-grammar', 'Part 5 ngữ pháp: tìm bộ khung của câu',
    'Tìm chủ ngữ, động từ và dấu hiệu thời gian. Từ đó xem chỗ trống cần loại từ nào trước khi so bốn lựa chọn.', 6, ['part5_grammar'],
    [('Nhìn các lựa chọn để nhận ra dạng câu hỏi', 'Nếu các lựa chọn là nhiều dạng của cùng một từ, đề thường hỏi từ loại hoặc dạng động từ. Nếu là những từ khác nhau, bạn cần chú ý nhiều hơn đến nghĩa của cả câu.'),
     ('Tìm chủ ngữ và động từ chính', 'Tạm bỏ qua các cụm bổ sung thông tin để thấy cấu trúc chính. Xem chỗ trống đứng cạnh từ nào, có giới từ hay dấu hiệu thời gian nào giúp chọn đáp án không.'),
     ('Đọc lại câu đã điền', 'Kiểm tra câu có đúng cả ngữ pháp lẫn nghĩa không. Chọn đúng từ loại thôi chưa đủ; vẫn cần so thì và số ít/số nhiều.')],
    ['Từ tận cùng -ly không phải lúc nào cũng là trạng từ; phải xem vai trò trong câu.', 'Danh từ gần chỗ trống nhất không nhất thiết là chủ ngữ của động từ.'],
    'The revised safety instructions are written clearly, so new employees can follow them without assistance.',
    'Complete the sentence: The revised safety instructions are written ______.', 'clearly',
    'Chỗ trống nói hướng dẫn được viết như thế nào, nên cần trạng từ clearly để bổ nghĩa cho are written. Clear là tính từ, clarity là danh từ, còn clarify là động từ.',
    ['clear', 'clearly', 'clarity', 'clarify'])

add('toeic-part5-collocations', 'Part 5 từ vựng: học cả cụm và ngữ cảnh',
    'Chọn những từ thường đi cùng nhau và phù hợp với tình huống. Khi ôn, lưu cả cụm kèm ví dụ để nhớ cách dùng.', 6, ['part5_vocabulary', 'collocation'],
    [('Hiểu câu đang nói về việc gì', 'Câu nói về thanh toán, lịch họp, vận chuyển hay tuyển dụng? Hiểu tình huống sẽ giúp bạn loại những từ không hợp nghĩa.'),
     ('Xem các từ quanh chỗ trống', 'Chú ý giới từ và danh từ đi cùng. Với cụm từ cố định, hãy xét cả cụm, đừng chỉ dịch từng từ sang tiếng Việt.'),
     ('Ghi lại cả mẫu để dùng lần sau', 'Sau khi chữa, lưu mẫu như be responsible for + danh từ/V-ing cùng một câu ngắn. Thử dùng mẫu đó trong tình huống khác để xem bạn đã hiểu cách dùng chưa.')],
    ['Hai từ đồng nghĩa tiếng Việt không nhất thiết kết hợp được với cùng một danh từ.', 'Đừng chỉ dựa vào một cụm quen mà bỏ qua nghĩa của cả câu.'],
    'The design team is responsible for updating the product catalogue before the trade fair.',
    'Complete the sentence: The design team is responsible ______ updating the catalogue.', 'for',
    'Cụm đúng là be responsible for + V-ing, nên chọn for. Updating đứng sau giới từ này ở dạng V-ing. Hãy nhớ cả responsible for để biết cách dùng, thay vì chỉ nhớ nghĩa “chịu trách nhiệm”.',
    ['at', 'for', 'with', 'by'])

add('toeic-part6-cohesion', 'Part 6: nối nghĩa giữa các câu',
    'Đọc cả câu trước và sau để chọn từ. Từ nối, đại từ và thì của động từ thường chỉ rõ khi bạn hiểu cả đoạn.', 6, ['part6_cohesion'],
    [('Xem văn bản được viết để làm gì', 'Đọc nhanh người gửi, người nhận và ý chính. Đây là thông báo thay đổi, lời xin lỗi, yêu cầu hay quảng cáo? Biết mục đích sẽ giúp hiểu từng chỗ trống.'),
     ('Đọc cả hai phía chỗ trống', 'Đọc câu có chỗ trống cùng câu trước và sau. Ý tiếp theo đang bổ sung, đối lập, giải thích nguyên nhân hay nêu kết quả?'),
     ('Đọc lại để kiểm tra cả đoạn', 'Xem đại từ chỉ đúng người hoặc vật chưa, và thì của động từ có hợp với thời điểm không. Một đáp án có thể đúng ngữ pháp trong một câu nhưng không hợp với phần còn lại.')],
    ['However nối hai ý trái nhau; therefore nối nguyên nhân với kết quả. Hai từ không thay thế cho nhau.', 'Đừng chỉ nhìn một câu như khi làm Part 5; Part 6 thường cần đọc thêm các câu xung quanh.'],
    'Demand for the new desk lamps has exceeded our forecast. ______, deliveries may take two extra days. Customers with urgent orders should contact our support team.',
    'Choose the best connector for the blank.', 'Therefore',
    'Nhu cầu cao hơn dự báo là lý do việc giao hàng có thể chậm thêm hai ngày. Therefore nối nguyên nhân với kết quả, nên phù hợp ở đây. However dùng khi hai ý trái nhau.',
    ['However', 'Therefore', 'Similarly', 'Meanwhile'])

add('toeic-part6-insertion', 'Part 6: chọn câu còn thiếu để đoạn liền mạch',
    'Câu cần điền phải nối được với cả câu trước và câu sau. Chú ý chủ đề, thứ tự các việc và những từ như this, these, it.', 7, ['part6_sentence_insertion'],
    [('Xem đoạn còn thiếu ý gì', 'Câu trước vừa nói điều gì? Câu sau đang giải thích, nhắc lại hay kết luận về điều gì? Thử đoán câu còn thiếu cần thêm thông tin nào.'),
     ('Tìm những từ giúp nối câu', 'Chú ý this, these, it, also và số ít/số nhiều. Nếu câu sau dùng một đại từ, hãy xem nó cần nhắc lại người hoặc vật nào ở trước.'),
     ('Đọc liền cả ba câu', 'Đọc câu trước, câu bạn chọn và câu sau. Loại đáp án đổi sang chuyện khác, lặp ý không cần thiết hoặc làm các việc xảy ra theo thứ tự vô lý.')],
    ['Cùng chủ đề vẫn chưa đủ: nếu câu sau dùng it hoặc these mà không rõ chỉ điều gì, hãy kiểm tra lại.', 'Câu được chọn cần hợp với cả phía trước lẫn phía sau.'],
    'We are introducing reusable delivery boxes next month. ______ These containers can be returned to any of our stores after use. Please keep the return label attached.',
    'Choose the sentence that best completes the notice.', 'Each order will arrive in a durable green container.',
    'Câu đúng cho biết mỗi đơn hàng sẽ được giao trong một hộp màu xanh, bền và dùng lại được. Nhờ đó, “These containers” ở câu sau có đối tượng rõ ràng để nói tiếp về cách trả hộp.',
    ['Our stores will stop accepting returned boxes.', 'Each order will arrive in a durable green container.', 'The design team met for lunch yesterday.', 'Delivery fees were reduced last year.'])

add('toeic-part7-single', 'Part 7 một văn bản: hiểu ý chính, tìm đúng chi tiết',
    'Xem ai viết cho ai và để làm gì. Với câu suy luận, tìm chi tiết làm căn cứ thay vì đoán thêm những điều bài chưa nói.', 7, ['part7_single', 'inference'],
    [('Nhìn nhanh tình huống', 'Đọc tiêu đề, người gửi, ngày và loại văn bản. Tự hỏi người đọc cần biết gì hoặc làm gì sau khi đọc.'),
     ('Xem câu hỏi cần cách đọc nào', 'Hỏi chi tiết thì tìm thông tin cụ thể. Hỏi mục đích thì nhìn cả văn bản. Hỏi hàm ý thì kết hợp điều được nói với tình huống. Nếu phải chèn câu, kiểm tra cả câu trước và sau.'),
     ('Tìm căn cứ cho đáp án', 'Chỉ ra một hoặc hai chi tiết dẫn đến kết luận bạn chọn. Đừng đoán thêm chức vụ, cảm xúc hay kế hoạch nếu bài không cho căn cứ.')],
    ['Một tên công ty, sản phẩm hoặc con số nổi bật chưa chắc là ý chính của bài.', 'Một việc có thể xảy ra ngoài đời chưa đủ để chọn đáp án; bài đọc phải có chi tiết cho phép suy ra việc đó.'],
    'To: Training participants\nSubject: Thursday workshop\nThe workshop will now be held in Room 204, which has additional seating. Several employees from our regional office have joined the session. The start time remains 9 a.m.',
    'What is most likely the reason for changing rooms?', 'More people are expected to attend.',
    'Phòng mới có nhiều chỗ ngồi hơn, đồng thời có thêm nhân viên tham gia. Ghép hai chi tiết này, ta hiểu rằng đổi phòng là để đủ chỗ cho nhiều người hơn. Giờ bắt đầu không đổi; bài không nói phòng cũ đang sửa.',
    ['The workshop will begin later.', 'More people are expected to attend.', 'The original room is being repaired.', 'The regional office has closed.'])

add('toeic-part7-multiple', 'Part 7 nhiều văn bản: ghép thông tin để tìm đáp án',
    'Dùng tên, mã đơn và thời gian để nối thông tin giữa email, bảng hoặc thông báo. Có câu cần đọc kết hợp hai hay nhiều văn bản mới trả lời được.', 8, ['part7_multiple', 'inference'],
    [('Xem mỗi văn bản cung cấp điều gì', 'Ghi nhanh, chẳng hạn: văn bản 1 nêu chính sách, văn bản 2 là yêu cầu của khách, văn bản 3 là thư trả lời. Tìm xem chúng liên quan với nhau thế nào.'),
     ('Tìm chi tiết chung giữa các văn bản', 'So tên người, sản phẩm, mã đặt chỗ và ngày để chắc rằng bạn đang nối đúng thông tin. Kiểm tra thêm loại tiền, số lượng và điều kiện áp dụng.'),
     ('Kiểm tra thông tin mới nhất', 'Thư trả lời có đổi lịch hoặc sửa yêu cầu ban đầu không? Khi chọn đáp án, thử chỉ ra mỗi văn bản cho bạn biết điều gì và ghép lại ra kết quả nào.')],
    ['Giá niêm yết có thể khác số tiền cần trả. Hãy kiểm tra giảm giá và điều kiện áp dụng.', 'Đừng chọn lịch ban đầu nếu email sau đã đổi lịch.'],
    'NOTICE: Workshop fees are $80 per person. Groups of five or more receive a $10 discount per person.\nEMAIL: Please reserve places for six employees from Pine Studio. All six will attend the same workshop.',
    'What is the total fee for Pine Studio?', '$420',
    'Email đăng ký 6 người, đủ điều kiện nhóm từ 5 người được giảm $10 mỗi người trong thông báo. Mỗi người trả $70, nên tổng là 6 × $70 = $420. Chọn $480 là chưa trừ giảm giá; $470 là mới trừ một lần cho cả nhóm.',
    ['$480', '$470', '$420', '$400'])


if __name__ == '__main__':
    (ROOT/'data/strategy_guides.json').write_text(json.dumps(dict(schema_version=1,
        content_note='Hướng dẫn và ví dụ ngắn do LexiRead tự biên soạn, có tham khảo cách ra câu hỏi từ nguồn chính thức. Đây không phải đề thi chính thức và không dùng để dự đoán điểm thi.',
        guides=GUIDES), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Wrote {len(GUIDES)} original strategy guides.')
