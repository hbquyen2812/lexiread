"""Original fictional graded-reading seed pack. Run to regenerate data/lessons/*.json.
Levels are author estimates, not certified CEFR or official IELTS material.
All English examples and Vietnamese translations below were composed for this app.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/lessons'; OUT.mkdir(exist_ok=True)
LESSONS=[]
def make(slug,title,level,topic,summary,paragraphs,translations,vocab,grammar,questions,faqs):
    assert len(paragraphs)==len(translations)
    words=[]
    for word,pos,meaning,syn,para,idx,note in vocab:
        assert word.lower() in paragraphs[idx].lower(),(title,word)
        words.append(dict(word=word,pos=pos,meaning_vi=meaning,synonyms=syn,paraphrases=[para],context=paragraphs[idx],example='',example_vi='',note=note,tags=[topic,level,title],paragraph_index=idx,origin='curated',verified=False))
    gs=[]
    for pattern,evidence,explain,example,example_vi in grammar:
        assert evidence in '\n\n'.join(paragraphs),(title,evidence)
        gs.append(dict(pattern=pattern,evidence=evidence,explanation_vi=explain,example=example,example_vi=example_vi))
    qs=[]
    for i,(kind,prompt,options,answer,idx,quote,explanation) in enumerate(questions):
        assert quote in paragraphs[idx],(title,quote)
        qs.append(dict(id=f'q{i+1}',kind=kind,prompt=prompt,options=options,answer=answer,paragraph_index=idx,evidence=quote,explanation_vi=explanation))
    fs=[]
    for question,answer,idx,quote in faqs:
        assert quote in paragraphs[idx],(title,quote)
        fs.append(dict(question=question,answer_vi=answer,paragraph_index=idx,evidence=quote))
    lesson=dict(slug=slug,title=title,level=level,topic=topic,summary=summary,revision=1,published=True,order=len(LESSONS)+1,
        author='LexiRead · nội dung soạn riêng',provenance='Bài đọc và tình huống hư cấu được biên soạn cho ứng dụng; không phải đề IELTS chính thức.',
        level_note='Mức độ do người biên soạn ước lượng; chưa được hiệu chuẩn CEFR.',text='\n\n'.join(paragraphs),
        analysis=dict(translations=[dict(index=i,vi=t) for i,t in enumerate(translations)],vocabulary=words,grammar=gs,origin='curated',warnings=[]),
        questions=qs,faqs=fs)
    LESSONS.append(lesson)

make('a-quiet-start','A Quiet Start to the Day','A2','Thói quen & đời sống','Một thay đổi nhỏ giúp buổi sáng của Mai bớt vội vàng.',[
"Mai used to check her phone as soon as she woke up. She read messages while eating breakfast and often left home in a hurry. One Monday, she forgot the notebook she needed for class. That evening, she decided to change her morning routine. She did not want a perfect morning. She wanted a calmer one.",
"Her new plan was simple. She put her bag beside the door before going to bed. In the morning, she left her phone on a shelf and made breakfast first. She also prepared a short list of three important tasks. A longer list made her feel worried, so she kept it short.",
"At first, the change felt strange. Mai reached for her phone without thinking. After a week, however, she found it easier to wait. She did not stop using her phone completely. She checked her messages on the bus, when she had already packed everything she needed.",
"Mai still had busy mornings, especially on rainy days. But she no longer felt that every morning was a race. Her favourite part was not finishing more tasks. It was having enough time to enjoy a warm breakfast. She chose to continue the routine because it suited her, not because someone said it was the best one."
],[
"Mai từng kiểm tra điện thoại ngay khi thức dậy. Cô đọc tin nhắn trong lúc ăn sáng và thường vội vã ra khỏi nhà. Một thứ Hai, cô quên cuốn vở cần dùng trên lớp. Tối hôm đó, cô quyết định thay đổi thói quen buổi sáng. Cô không muốn một buổi sáng hoàn hảo. Cô muốn một buổi sáng bình tĩnh hơn.",
"Kế hoạch mới của cô rất đơn giản. Cô đặt cặp cạnh cửa trước khi đi ngủ. Buổi sáng, cô để điện thoại trên kệ và chuẩn bị bữa sáng trước. Cô cũng viết một danh sách ngắn gồm ba việc quan trọng. Danh sách dài hơn khiến cô lo lắng nên cô giữ nó ngắn gọn.",
"Lúc đầu, thay đổi này khá lạ lẫm. Mai với lấy điện thoại mà không suy nghĩ. Tuy nhiên, sau một tuần, cô thấy việc chờ đợi dễ hơn. Cô không ngừng dùng điện thoại hoàn toàn. Cô kiểm tra tin nhắn trên xe buýt, khi đã xếp đủ những thứ cần mang theo.",
"Mai vẫn có những buổi sáng bận rộn, nhất là vào ngày mưa. Nhưng cô không còn cảm thấy sáng nào cũng là một cuộc đua. Điều cô thích nhất không phải là làm xong nhiều việc hơn, mà là có đủ thời gian thưởng thức bữa sáng ấm nóng. Cô tiếp tục thói quen này vì nó phù hợp với mình, không phải vì ai đó nói rằng đó là cách tốt nhất."
],[
('routine','n','thói quen hoặc trình tự thường ngày',['habit','regular pattern'],'the things you regularly do',0,'Routine nhấn mạnh trình tự thường làm; habit thường là một hành vi quen thuộc.'),
('in a hurry','phrase','vội vàng',['in a rush'],'without much time to spare',0,''),
('prepared','v','đã chuẩn bị',['got ready'],'made something ready in advance',1,''),
('reached for','phrase','với tay lấy',['stretched towards'],'moved her hand towards something',2,''),
('no longer','phrase','không còn nữa',['not anymore'],'not now, although it was true before',3,''),
('suited','v','phù hợp với',['was right for'],'matched her needs',3,'Suit ở đây là động từ, không phải danh từ bộ com-lê.')
],[
('used to + V','Mai used to check her phone as soon as she woke up.','Diễn tả thói quen trong quá khứ, nay đã thay đổi. Không nhầm với be used to + V-ing: quen với.','I used to study late at night.','Tôi từng học đến khuya.'),
('before + V-ing','before going to bed','Sau before có thể dùng V-ing khi chủ thể đã rõ và trùng với chủ thể câu chính.','I pack my bag before leaving.','Tôi xếp cặp trước khi đi.')
],[
('main_idea','What is the main focus of the passage?',['A small change to a morning routine','The best phone to buy','A new bus service','A difficult school examination'],0,0,'she decided to change her morning routine.','Toàn bài theo dõi việc Mai thay đổi nếp sinh hoạt buổi sáng, không đánh giá thiết bị hay kỳ thi.'),
('detail','When did Mai check messages after changing her routine?',['Before breakfast','On the bus','During class','Just before going to sleep'],1,2,'She checked her messages on the bus','Thông tin ở đoạn 3 nói rõ địa điểm/thời điểm là trên xe buýt.'),
('tfng','Mai stopped using her phone completely.',['TRUE','FALSE','NOT GIVEN'],1,2,'She did not stop using her phone completely.','Câu hỏi nói ngừng hoàn toàn; bài phủ định trực tiếp điều đó.'),
('vocabulary','In the final paragraph, “suited her” means:',['made her famous','was expensive','was right for her','was chosen by her teacher'],2,3,'She chose to continue the routine because it suited her','Suited her nghĩa là phù hợp với nhu cầu của cô.')
],[
('“A calmer one” thay cho điều gì?','One thay cho morning để tránh lặp danh từ. A calmer one là một buổi sáng bình tĩnh, ít vội vàng hơn.',0,'She wanted a calmer one.'),
('“No longer” khác “never” thế nào?','No longer nói trước đây có nhưng hiện tại không còn. Never là chưa bao giờ/không bao giờ, không hàm ý một sự thay đổi như vậy.',3,'she no longer felt that every morning was a race.')
])

make('one-meal-at-a-time','One Meal at a Time','A2','Ẩm thực','Nam bắt đầu học nấu ăn bằng một món đơn giản thay vì một thực đơn dài.',[
"Nam wanted to cook at home, but online recipes often looked difficult. Some needed ten ingredients or several special tools. His sister suggested a different approach: learn one simple meal first. Nam chose vegetable rice because he already had a pan and most of the ingredients in his kitchen.",
"On his first attempt, he cut the carrots into pieces that were too large. They were still hard when the rice was ready. His sister did not cook the meal for him. Instead, she showed him how to cut smaller pieces and asked him to try again the next evening.",
"Nam wrote three short notes beside the recipe. He did not copy every instruction. He only recorded the steps he had forgotten or misunderstood. On Thursday, the meal turned out well. He made enough for himself and his sister, and they ate together at the small kitchen table.",
"A month later, Nam could prepare three meals without looking at a recipe. He still made mistakes, but he was less worried about them. For him, learning to cook was not a competition. It was a way to become more independent and enjoy time with his family."
],[
"Nam muốn nấu ăn ở nhà, nhưng công thức trên mạng thường có vẻ khó. Một số công thức cần mười nguyên liệu hoặc vài dụng cụ đặc biệt. Chị cậu đề xuất cách khác: học một món đơn giản trước. Nam chọn cơm rau củ vì cậu đã có chảo và phần lớn nguyên liệu trong bếp.",
"Lần thử đầu tiên, cậu cắt cà rốt thành những miếng quá lớn. Chúng vẫn cứng khi cơm đã chín. Chị không nấu hộ cậu. Thay vào đó, chị chỉ cách cắt miếng nhỏ hơn và bảo cậu thử lại vào tối hôm sau.",
"Nam viết ba ghi chú ngắn bên cạnh công thức. Cậu không chép lại mọi hướng dẫn. Cậu chỉ ghi các bước mình đã quên hoặc hiểu sai. Đến thứ Năm, món ăn có kết quả tốt. Cậu làm đủ cho hai chị em, và họ cùng ăn ở chiếc bàn nhỏ trong bếp.",
"Một tháng sau, Nam có thể chuẩn bị ba món mà không nhìn công thức. Cậu vẫn mắc lỗi nhưng bớt lo lắng về chúng. Với cậu, học nấu ăn không phải cuộc thi. Đó là cách để tự lập hơn và tận hưởng thời gian bên gia đình."
],[
('ingredients','n','nguyên liệu của món ăn',['food components'],'the foods used to make a dish',0,''),
('approach','n','cách tiếp cận, phương pháp',['method'],'a way of doing something',0,''),
('attempt','n','lần thử, nỗ lực thực hiện',['try'],'an effort to do something',1,''),
('Instead','adv','thay vào đó',['as an alternative'],'in place of doing that',1,''),
('turned out well','phrase','cuối cùng có kết quả tốt',['went well'],'had a successful result',2,'Turn out không mang nghĩa sản xuất trong cụm này.'),
('independent','adj','tự lập, ít phụ thuộc người khác',['self-reliant'],'able to do things without depending on others',3,'Trong bài nói về khả năng tự lo cho bản thân, không phải độc lập chính trị.')
],[
('too + adj','pieces that were too large','Too large là quá lớn so với yêu cầu, không chỉ rất lớn.','This bag is too heavy.','Chiếc túi này quá nặng.'),
('without + V-ing','without looking at a recipe','Without + V-ing: mà không thực hiện hành động đó.','I answered without checking my notes.','Tôi trả lời mà không xem ghi chú.')
],[
('main_idea','What helped Nam begin learning to cook?',['Buying expensive tools','Starting with one simple dish','Entering a competition','Memorising ten recipes'],1,0,'learn one simple meal first.','Chị gợi ý bắt đầu bằng một món đơn giản.'),
('detail','What was wrong with the carrots on his first attempt?',['They were missing','They were too sweet','The pieces were too large','There were too few'],2,1,'he cut the carrots into pieces that were too large.','Lỗi nằm ở kích thước miếng cà rốt.'),
('tfng','Nam bought a new pan before his first attempt.',['TRUE','FALSE','NOT GIVEN'],2,0,'he already had a pan','Bài nói cậu có sẵn chảo, không cho biết cậu có mua thêm một chiếc mới trước lần thử hay không. Có sẵn không loại trừ việc mua thêm.'),
('vocabulary','“More independent” means Nam could:',['depend less on help from others','cook without ingredients','win more competitions','avoid all mistakes'],0,3,'become more independent','Independent nhấn mạnh khả năng tự làm, không phải không bao giờ mắc lỗi.')
],[
('Vì sao “instead” không dịch là “tuy nhiên”?','Ở đây chị không nấu hộ mà chọn một hành động thay thế: chỉ cách cắt nhỏ. Instead nhấn mạnh sự thay thế; however chỉ biểu thị tương phản rộng hơn.',1,'Instead, she showed him how to cut smaller pieces'),
('“The steps he had forgotten” có thiếu “that” không?','Đây là mệnh đề quan hệ xác định. Có thể viết the steps that he had forgotten; that làm tân ngữ nên có thể bỏ.',2,'the steps he had forgotten or misunderstood.')
])

make('the-balcony-garden','The Balcony Garden','A2','Thiên nhiên','Linh thử trồng cây trong một không gian nhỏ và điều chỉnh kế hoạch của mình.',[
"Linh lived in a flat without a garden, but she wanted to grow something. Her balcony was narrow, with space for a chair and a few pots. She started with two plants rather than filling the whole balcony. A neighbour gave her an old pot, and she bought another one at a small shop.",
"Each morning, Linh looked at the plants before leaving for work. She kept a notebook with the date and a short observation. One pot stood close to the wall, where it received little light. When that plant looked weak, she moved the pot nearer the front of the balcony.",
"Not every change worked immediately. Once, she gave a plant too much water and had to ask her neighbour for advice. The neighbour suggested checking the soil first. Linh began to pay attention to each plant instead of following the same routine for both of them.",
"After several weeks, one plant produced a few small flowers. Linh was delighted, but she did not want a much bigger collection. She liked being able to care for the plants she had. The garden remained small, leaving enough room for her chair and a quiet cup of tea."
],[
"Linh sống trong căn hộ không có vườn nhưng muốn trồng cây. Ban công của cô hẹp, chỉ đủ chỗ cho một chiếc ghế và vài chậu cây. Cô bắt đầu với hai cây thay vì lấp kín ban công. Một người hàng xóm cho cô chậu cũ, và cô mua thêm một chậu ở cửa hàng nhỏ.",
"Mỗi sáng, Linh ngắm cây trước khi đi làm. Cô ghi ngày tháng và một quan sát ngắn trong sổ. Một chậu đặt sát tường, nơi nhận được ít ánh sáng. Khi cây trông yếu, cô chuyển chậu ra gần phía trước ban công hơn.",
"Không phải thay đổi nào cũng có tác dụng ngay. Có lần cô tưới quá nhiều nước và phải hỏi hàng xóm. Người hàng xóm gợi ý kiểm tra đất trước. Linh bắt đầu chú ý đến từng cây thay vì áp dụng cùng một cách chăm sóc cho cả hai.",
"Sau vài tuần, một cây ra vài bông hoa nhỏ. Linh rất vui nhưng không muốn có một bộ sưu tập cây lớn hơn nhiều. Cô thích việc mình có thể chăm sóc những cây đang có. Khu vườn vẫn nhỏ, để lại đủ chỗ cho chiếc ghế và một tách trà yên tĩnh."
],[
('narrow','adj','hẹp',['not wide'],'having little width',0,''),
('rather than','phrase','thay vì, chứ không phải',['instead of'],'choosing one option instead of another',0,''),
('observation','n','điều quan sát hoặc ghi nhận được',['something noticed'],'a detail noticed by watching',1,''),
('immediately','adv','ngay lập tức',['at once'],'without waiting',2,''),
('pay attention to','phrase','chú ý đến',['notice','focus on'],'look at something carefully',2,''),
('delighted','adj','rất vui, hài lòng',['very pleased'],'feeling very happy about something',3,'Mức độ mạnh hơn pleased trong nhiều ngữ cảnh.')
],[
('not every + noun','Not every change worked immediately.','Không phải mọi thay đổi đều có tác dụng ngay. Không đồng nghĩa với không thay đổi nào có tác dụng.','Not every answer is correct.','Không phải đáp án nào cũng đúng.'),
('enough + noun','leaving enough room for her chair','Enough đứng trước danh từ: enough room = đủ không gian.','We have enough time.','Chúng ta có đủ thời gian.')
],[
('main_idea','What does Linh learn through her small garden?',['How to sell flowers','How to move to a larger flat','How to care for the plants she has','How to replace all her furniture'],2,3,'care for the plants she had.','Trọng tâm là chăm sóc và điều chỉnh cách làm cho số cây hiện có.'),
('detail','Why did she move the pot away from the wall?',['The plant looked weak','The pot was broken','She needed a new chair','Her neighbour wanted it'],0,1,'When that plant looked weak, she moved the pot','Đoạn 2 nêu trực tiếp lý do cây trông yếu.'),
('tfng','Linh wanted to fill the whole balcony with more plants at the end.',['TRUE','FALSE','NOT GIVEN'],1,3,'she did not want a much bigger collection.','Bài phủ định mong muốn có thêm nhiều cây.'),
('vocabulary','Which expression is closest to “pay attention to”?',['give away','notice carefully','forget about','wait for'],1,2,'pay attention to each plant','Cụm này có nghĩa chú ý, quan sát kỹ từng cây.')
],[
('“Little light” và “a little light” khác nhau thế nào?','Little light nhấn mạnh ít, có sắc thái thiếu ánh sáng; a little light nhấn mạnh vẫn có một chút ánh sáng. Cả hai đi với danh từ không đếm được light.',1,'where it received little light.'),
('“Room” ở đoạn cuối có phải phòng không?','Không. Trong enough room, room là không gian/chỗ trống, không đếm được. A room mới có thể là một căn phòng.',3,'leaving enough room for her chair')
])

make('an-afternoon-without-photos','An Afternoon without Photos','A2','Sở thích & kết nối','Hai người bạn thử dành một buổi đi chơi để trò chuyện thay vì chụp ảnh.',[
"Every time An met her friend Ruby, they took dozens of photos. They chose a table near the window, moved their drinks and waited for the right light. Sometimes they spent more time looking at the screen than talking to each other. An enjoyed the pictures, but she missed their long conversations.",
"For their next meeting, An suggested leaving their phones in their bags for the first hour. Ruby agreed, although she wanted one photo at the end. They visited a small cafe and talked about a book they were both reading. Without a screen on the table, they noticed that their conversation moved more slowly.",
"Halfway through the meeting, Ruby remembered a funny message and reached for her bag. Then she stopped and told the story in her own words. An laughed, and neither of them felt they needed to see the message. They were interested in the story, not in the exact words on a screen.",
"Before leaving, they asked a member of staff to take one picture. The photo was a little dark, but they kept it anyway. They had not decided that photos were bad. They simply wanted their next meeting to include more conversation and fewer interruptions."
],[
"Mỗi lần An gặp bạn Ruby, họ chụp hàng chục bức ảnh. Họ chọn bàn gần cửa sổ, di chuyển đồ uống và chờ ánh sáng phù hợp. Đôi lúc họ nhìn màn hình lâu hơn thời gian trò chuyện với nhau. An thích những bức ảnh nhưng nhớ những cuộc nói chuyện dài của hai người.",
"Lần gặp tiếp theo, An đề nghị để điện thoại trong túi suốt giờ đầu. Ruby đồng ý, dù vẫn muốn chụp một tấm vào cuối buổi. Họ đến quán cà phê nhỏ và nói về cuốn sách cả hai đang đọc. Không có màn hình trên bàn, họ nhận thấy cuộc trò chuyện diễn ra chậm rãi hơn.",
"Giữa buổi gặp, Ruby nhớ ra một tin nhắn hài hước và với tay lấy túi. Rồi cô dừng lại, kể câu chuyện bằng lời của mình. An bật cười, và cả hai đều không thấy cần đọc tin nhắn. Họ quan tâm đến câu chuyện, không phải từng chữ chính xác trên màn hình.",
"Trước khi rời đi, họ nhờ một nhân viên chụp một tấm ảnh. Ảnh hơi tối nhưng họ vẫn giữ. Họ không kết luận rằng ảnh là xấu. Họ chỉ muốn lần gặp sau có nhiều trò chuyện hơn và ít gián đoạn hơn."
],[
('dozens of','phrase','hàng chục',['many groups of twelve'],'a large number, measured in tens',0,'Dozens of chỉ số lượng ước chừng; không có nghĩa chính xác 24.'),
('suggested','v','đề nghị, gợi ý',['proposed'],'offered an idea for consideration',1,''),
('although','conj','mặc dù',['even though'],'introduces a contrasting fact',1,''),
('in her own words','phrase','bằng lời của chính cô ấy',['using her own expression'],'without copying the original wording',2,''),
('anyway','adv','dù vậy, vẫn cứ',['despite that'],'even though there was a reason not to',3,''),
('interruptions','n','những sự gián đoạn',['breaks','disruptions'],'things that stop an activity briefly',3,'Không phải break nào cũng gây gián đoạn không mong muốn; nghĩa phụ thuộc ngữ cảnh.')
],[
('suggest + V-ing','An suggested leaving their phones in their bags','Sau suggest có thể dùng V-ing. Không dùng suggest to leave trong mẫu này.','She suggested walking home.','Cô ấy đề nghị đi bộ về.'),
('more ... than ...','more time looking at the screen than talking to each other','So sánh thời gian dành cho hai hoạt động song song dạng V-ing.','I spend more time reading than watching TV.','Tôi dành thời gian đọc nhiều hơn xem tivi.')
],[
('main_idea','What did the friends want to change?',['The amount of conversation during meetings','The books in the cafe','The work of the cafe staff','The price of their phones'],0,3,'more conversation and fewer interruptions.','Mục tiêu là nói chuyện nhiều hơn, ít bị gián đoạn hơn.'),
('detail','How many photos did they ask the staff member to take?',['None','One','Twelve','Dozens'],1,3,'take one picture.','Đoạn cuối nói rõ một bức ảnh.'),
('tfng','The friends decided never to take photos again.',['TRUE','FALSE','NOT GIVEN'],1,3,'they asked a member of staff to take one picture.','Họ vẫn chụp một ảnh cuối buổi nên không hề từ bỏ việc chụp ảnh.'),
('vocabulary','“In her own words” means:',['in a foreign language','by reading the message aloud','using her own way of telling it','by showing a photograph'],2,2,'told the story in her own words.','Ruby kể lại bằng cách diễn đạt riêng, không đọc nguyên văn tin nhắn.')
],[
('“Neither of them” chỉ ai?','Them chỉ An và Ruby. Neither of them nghĩa là không người nào trong hai người, không phải cả hai đều cần xem tin nhắn.',2,'neither of them felt they needed to see the message.'),
('“Although” có thể bỏ vế chính không?','Mệnh đề although tạo ý nhượng bộ và cần gắn với mệnh đề chính trong câu hoàn chỉnh. Ở đây Ruby agreed là mệnh đề chính.',1,'Ruby agreed, although she wanted one photo at the end.')
])

make('the-book-exchange','The Book Exchange','B1','Cộng đồng & văn hóa','Một tủ sách dùng chung phải cân bằng sự linh hoạt và quy tắc rõ ràng.',[
"When a small reading club placed a bookcase in the entrance of an apartment building, the instructions were deliberately simple: take a book, read it and bring it back. Nobody had to register. The organisers hoped that an informal exchange would encourage people who did not usually visit the public library to try reading something new.",
"For the first month, the bookcase was busy. Residents left novels, travel stories and children's books. Then a problem appeared. Several popular books disappeared for weeks, while old magazines gradually filled the shelves. The organisers could not tell whether the missing books were still being read or had been lost. They had no record of individual loans.",
"Rather than introducing fines, the club tried a modest change. Borrowers could write a return date on a card and place it in a box. A separate shelf was created for magazines. These measures did not prevent every problem, but they made the system easier to understand. The club also asked residents to suggest titles they wanted to read.",
"The exchange remained free and open to everyone in the building. Its success was not measured only by the number of books in circulation. At a meeting, one resident explained that she had started talking to a neighbour because they enjoyed the same novel. For the organisers, that conversation was as valuable as a returned book."
],[
"Khi một câu lạc bộ đọc sách nhỏ đặt tủ sách ở lối vào tòa chung cư, hướng dẫn được cố ý giữ đơn giản: lấy sách, đọc rồi mang trả. Không ai phải đăng ký. Ban tổ chức hy vọng hình thức trao đổi không chính thức sẽ khuyến khích những người ít đến thư viện công thử đọc điều mới.",
"Trong tháng đầu, tủ sách được sử dụng nhiều. Cư dân để lại tiểu thuyết, truyện du lịch và sách thiếu nhi. Sau đó nảy sinh vấn đề: vài cuốn được yêu thích biến mất nhiều tuần, trong khi tạp chí cũ dần lấp đầy các kệ. Ban tổ chức không biết sách còn đang được đọc hay đã thất lạc. Họ không ghi lại từng lượt mượn.",
"Thay vì đưa ra tiền phạt, câu lạc bộ thử thay đổi nhỏ. Người mượn có thể viết ngày trả dự kiến trên thẻ rồi bỏ vào hộp. Một kệ riêng được dành cho tạp chí. Các biện pháp không ngăn được mọi vấn đề nhưng giúp hệ thống dễ hiểu hơn. Câu lạc bộ cũng đề nghị cư dân gợi ý đầu sách muốn đọc.",
"Việc trao đổi vẫn miễn phí và mở cho mọi người trong tòa nhà. Thành công không chỉ được đo bằng số sách đang luân chuyển. Trong một cuộc họp, một cư dân kể rằng cô bắt đầu nói chuyện với hàng xóm vì họ thích cùng một tiểu thuyết. Với ban tổ chức, cuộc trò chuyện đó cũng có giá trị như một cuốn sách được trả lại."
],[
('deliberately','adv','một cách có chủ đích',['intentionally'],'on purpose rather than by accident',0,''),
('informal','adj','không theo thủ tục chính thức',['casual'],'without many formal rules',0,''),
('gradually','adv','dần dần',['little by little'],'over time rather than suddenly',1,''),
('modest','adj','nhỏ, không quá lớn về quy mô',['small','limited'],'not large in scale',2,'Không phải nghĩa khiêm tốn về tính cách trong câu này.'),
('in circulation','phrase','đang được luân chuyển, sử dụng',['being passed around'],'moving between readers',3,'Trong ngữ cảnh sách; không phải tuần hoàn máu.'),
('valuable','adj','có giá trị, đáng quý',['worthwhile'],'important or useful',3,'Giá trị ở đây không nhất thiết đo bằng tiền.')
],[
('whether ... or ...','whether the missing books were still being read or had been lost','Nêu hai khả năng mà người nói chưa xác định được. Không khẳng định rằng sách chắc chắn đã mất.','I do not know whether she is busy or away.','Tôi không biết cô ấy đang bận hay đi vắng.'),
('as + adj + as','as valuable as a returned book','So sánh ngang bằng về một đặc tính.','Practice is as important as theory.','Thực hành cũng quan trọng như lý thuyết.')
],[
('main_idea','What does the passage mainly describe?',['Why public libraries should close','How a shared bookcase was adjusted to serve residents','How a bookshop increased its profits','Why residents disliked novels'],1,2,'the club tried a modest change.','Bài mô tả tủ sách cộng đồng, vấn đề phát sinh và điều chỉnh nhỏ.'),
('detail','What was introduced to help with book returns?',['A borrowing fee','A security camera','A card with a return date','A ban on popular novels'],2,2,'Borrowers could write a return date on a card','Thẻ ghi ngày trả được thêm vào, không có phí hay lệnh cấm.'),
('tfng','All the books that disappeared were lost.',['TRUE','FALSE','NOT GIVEN'],2,1,'The organisers could not tell whether the missing books were still being read or had been lost.','Bài nói không biết sách đang được đọc hay đã mất; không thể kết luận tất cả đã mất, cũng chưa có phản ví dụ xác nhận tất cả không mất.'),
('vocabulary','“A modest change” is a change that is:',['small in scale','extremely expensive','impossible to understand','legally required'],0,2,'the club tried a modest change.','Modest bổ nghĩa quy mô thay đổi, không nói tính cách người thực hiện.')
],[
('“Were still being read” là thì/cấu trúc gì?','Đây là quá khứ tiếp diễn bị động: were + being + V3. Sách là đối tượng được đọc; still nhấn mạnh có thể việc đọc vẫn tiếp diễn lúc ấy.',1,'were still being read'),
('Vì sao không suy ra “mất sách” từ “disappeared”?','Disappeared mô tả sách không còn ở kệ trong thời gian đó. Câu sau nói người tổ chức chưa biết sách đang được đọc hay đã thất lạc, nên không được tự chọn một khả năng.',1,'had been lost.')
])

make('the-repair-afternoon','The Repair Afternoon','B1','Môi trường & đồ dùng','Một buổi sửa đồ đề cao kỹ năng và quyết định sửa hay bỏ theo từng trường hợp.',[
"On the first Saturday of each month, a group of volunteers used a community room as a repair workshop. Visitors brought lamps, bags and small pieces of furniture. The aim was not to promise that everything could be fixed. It was to help people understand what had gone wrong and decide whether a repair was worth attempting.",
"A retired craft worker named Elena usually examined wooden objects. She could take a chair to pieces and identify the damaged part without replacing the whole frame. She explained each step to the owner. Visitors were encouraged to watch and ask questions rather than simply leave an object and return when the work was finished.",
"Some repairs were straightforward; others were not. One lamp needed a replacement part that the volunteers did not have. They did not improvise an unsafe solution. Instead, they explained the limitation and suggested asking a qualified specialist. The workshop kept a small box for parts that could be reused, but electrical work was restricted to volunteers with the relevant skills.",
"At the end of the afternoon, the organisers counted completed repairs and items that still needed attention. They also recorded what visitors had learned. A bag that was repaired might eventually wear out again, but knowing how to sew a simple seam could remain useful. For Elena, passing on that knowledge was an important part of the project."
],[
"Vào thứ Bảy đầu tiên mỗi tháng, nhóm tình nguyện viên dùng phòng sinh hoạt cộng đồng làm xưởng sửa đồ. Người đến mang theo đèn, túi và đồ nội thất nhỏ. Mục tiêu không phải hứa rằng mọi thứ đều sửa được, mà là giúp mọi người hiểu lỗi ở đâu và quyết định việc sửa có đáng thử không.",
"Một người thợ thủ công đã nghỉ hưu tên Elena thường kiểm tra đồ gỗ. Bà có thể tháo rời ghế và xác định bộ phận hỏng mà không thay cả khung. Bà giải thích từng bước cho chủ đồ vật. Khách được khuyến khích quan sát và đặt câu hỏi thay vì chỉ để đồ lại rồi quay lại khi xong.",
"Một số việc sửa đơn giản; số khác thì không. Một chiếc đèn cần linh kiện thay thế mà nhóm không có. Họ không ứng biến một giải pháp thiếu an toàn. Thay vào đó, họ giải thích hạn chế và gợi ý tìm người có chuyên môn phù hợp. Xưởng có hộp nhỏ đựng linh kiện tái sử dụng, nhưng việc điện chỉ dành cho tình nguyện viên có kỹ năng liên quan.",
"Cuối buổi, ban tổ chức đếm số đồ đã sửa và số đồ còn cần xử lý. Họ cũng ghi những gì khách đã học. Chiếc túi đã sửa có thể rồi lại mòn, nhưng biết khâu một đường may đơn giản vẫn có ích. Với Elena, truyền lại kiến thức ấy là phần quan trọng của dự án."
],[
('worth attempting','phrase','đáng để thử thực hiện',['worth trying'],'useful enough to make an effort',0,''),
('take a chair to pieces','phrase','tháo rời chiếc ghế',['dismantle a chair'],'separate a chair into its parts',1,''),
('straightforward','adj','đơn giản, không phức tạp',['uncomplicated'],'easy to understand or carry out',2,''),
('improvise','v','ứng biến bằng những thứ sẵn có',['make do creatively'],'create a solution without a prepared plan',2,'Ứng biến không tự đồng nghĩa với bất cẩn; bài chỉ bác bỏ giải pháp ứng biến thiếu an toàn.'),
('restricted to','phrase','giới hạn cho một nhóm/phạm vi',['limited to'],'allowed only for a specified group',2,''),
('wear out','phrase','hao mòn do sử dụng',['become worn'],'lose condition through repeated use',3,'Không đồng nghĩa hoàn toàn với break down: ngừng hoạt động/hỏng máy.')
],[
('be worth + V-ing','whether a repair was worth attempting','Worth đi với danh từ hoặc V-ing, không dùng worth to attempt trong cấu trúc này.','This book is worth reading.','Cuốn sách này đáng đọc.'),
('be encouraged to + V','Visitors were encouraged to watch and ask questions','Cấu trúc bị động: người tham gia được khuyến khích làm điều gì.','Students are encouraged to ask questions.','Sinh viên được khuyến khích đặt câu hỏi.')
],[
('main_idea','Which goal best represents the workshop?',['Repairing every object without exception','Teaching visitors while assessing possible repairs','Selling brand-new furniture','Collecting objects without returning them'],1,0,'help people understand what had gone wrong','Xưởng giúp hiểu lỗi, đánh giá và học kỹ năng; không bảo đảm sửa tất cả.'),
('detail','Why was one lamp not repaired there?',['The owner refused to watch','There was no room','A needed replacement part was unavailable','The volunteers disliked lamps'],2,2,'a replacement part that the volunteers did not have.','Bài nêu thiếu linh kiện cần thiết.'),
('tfng','The volunteers promised to fix every object brought to the workshop.',['TRUE','FALSE','NOT GIVEN'],1,0,'The aim was not to promise that everything could be fixed.','Câu gốc phủ định trực tiếp lời hứa sửa tất cả.'),
('vocabulary','“Restricted to” has the closest meaning to:',['open to everybody','limited to','delayed by','paid for by'],1,2,'electrical work was restricted to volunteers with the relevant skills.','Việc điện chỉ giao cho nhóm có kỹ năng liên quan.')
],[
('“Had gone wrong” dùng quá khứ hoàn thành để làm gì?','Sự hỏng hóc xảy ra trước khi khách và nhóm tìm hiểu. Had + V3 giúp thể hiện quan hệ trước–sau trong câu chuyện quá khứ.',0,'what had gone wrong'),
('“Some ...; others ...” có nghĩa là gì?','Mẫu này chia nhóm: một số việc sửa đơn giản, các việc khác thì không. Others thay cho other repairs để tránh lặp.',2,'Some repairs were straightforward; others were not.')
])

make('learning-in-the-bicycle-shop','Learning in the Bicycle Shop','B1','Nghề nghiệp','Một người học nghề phát hiện sự kiên nhẫn quan trọng không kém năng khiếu.',[
"When Leo began his apprenticeship at a bicycle shop, he expected to spend most of his time repairing bikes. In the first week, however, his supervisor asked him to label tools, check deliveries and listen to customers. Leo thought these tasks were less important than technical work. He soon discovered that they were part of learning the trade.",
"One customer said that her bicycle made a strange sound only when she rode uphill. Leo wanted to replace a part immediately, but his supervisor asked him to repeat the customer's description first. The missing detail was pertinent to the problem: the sound did not occur on every journey. Without that information, they might replace a part that was working correctly.",
"Leo showed an aptitude for understanding how parts fitted together. Nevertheless, he sometimes rushed his explanations. The supervisor encouraged him to describe one step at a time and check that the customer understood. Over several months, Leo became more confident both with the tools and with the people who brought their bikes into the shop.",
"The shop did not take on an apprentice to obtain cheap labour. The owner set aside time for teaching and accepted that some jobs would take longer. Leo, in turn, had to ask for help when he was uncertain. The arrangement worked because both sides treated learning as a responsibility rather than a lucky extra."
],[
"Khi Leo bắt đầu học nghề tại cửa hàng xe đạp, cậu nghĩ phần lớn thời gian sẽ dành để sửa xe. Tuy nhiên, tuần đầu, người hướng dẫn bảo cậu dán nhãn dụng cụ, kiểm hàng giao đến và lắng nghe khách. Leo cho rằng những việc này kém quan trọng hơn việc kỹ thuật. Cậu sớm nhận ra chúng là một phần của quá trình học nghề.",
"Một khách hàng nói xe chỉ phát tiếng lạ khi đi lên dốc. Leo muốn thay linh kiện ngay nhưng người hướng dẫn yêu cầu cậu nhắc lại mô tả của khách trước. Chi tiết bị bỏ sót liên quan trực tiếp đến vấn đề: âm thanh không xuất hiện ở mọi chuyến đi. Thiếu thông tin ấy, họ có thể thay một linh kiện vẫn đang hoạt động đúng.",
"Leo có năng khiếu hiểu cách các bộ phận lắp với nhau. Dù vậy, đôi khi cậu giải thích quá vội. Người hướng dẫn khuyến khích cậu mô tả từng bước và kiểm tra khách đã hiểu chưa. Qua vài tháng, Leo tự tin hơn với cả dụng cụ và những người mang xe đến cửa hàng.",
"Cửa hàng không nhận người học nghề chỉ để có lao động giá rẻ. Chủ dành thời gian dạy và chấp nhận một số việc sẽ lâu hơn. Về phần mình, Leo phải hỏi giúp đỡ khi chưa chắc. Sự hợp tác hiệu quả vì cả hai coi việc học là trách nhiệm chứ không phải lợi ích phụ may mắn có được."
],[
('apprenticeship','n','quá trình học nghề có hướng dẫn và thực hành',['practical job training'],'a period of learning a trade while working',0,'Apprentice là người học nghề; apprenticeship là quá trình/chương trình.'),
('pertinent','adj','liên quan trực tiếp đến vấn đề',['relevant'],'directly connected with the matter being discussed',1,'Thường dùng pertinent to; không đồng nghĩa với important trong mọi câu.'),
('aptitude','n','năng khiếu hoặc khả năng tự nhiên',['natural ability','talent'],'a natural ability to learn or do something',2,'Aptitude for + danh từ/V-ing. Không nhầm attitude: thái độ.'),
('Nevertheless','adv','tuy nhiên, dù vậy',['however'],'despite what has just been said',2,''),
('take on','phrase','tuyển hoặc nhận người vào làm',['hire'],'employ someone',3,'Take on còn nghĩa đảm nhận trách nhiệm; ở đây tân ngữ là người.'),
('set aside','phrase','dành riêng thời gian hoặc nguồn lực',['reserve'],'keep something available for a particular purpose',3,'Trong bài là dành thời gian, không phải gạt bỏ một ý kiến.')
],[
('might + V','they might replace a part that was working correctly.','Might diễn tả khả năng, không khẳng định việc thay sai đã xảy ra.','Without a map, we might get lost.','Không có bản đồ, chúng ta có thể bị lạc.'),
('rather than + noun phrase','a responsibility rather than a lucky extra','Đối lập cách nhìn A chứ không phải B.','It is a habit rather than a rule.','Đó là thói quen chứ không phải quy định.')
],[
('main_idea','What does Leo learn about his apprenticeship?',['It involves people and organisation as well as repairs','Only replacing parts matters','Customer descriptions are always unnecessary','Learning requires no time from the owner'],0,0,'they were part of learning the trade.','Toàn bài mở rộng việc học nghề sang nghe khách, tổ chức và giải thích.'),
('detail','When did the customer report hearing the strange sound?',['On every journey','Only while riding uphill','Only when the bike was parked','After every repair'],1,1,'only when she rode uphill.','Only giới hạn tình huống là khi lên dốc.'),
('tfng','Leo was already skilled at repairing cars.',['TRUE','FALSE','NOT GIVEN'],2,2,'Leo showed an aptitude for understanding how parts fitted together.','Có năng khiếu cơ khí không xác lập kinh nghiệm sửa ô tô; bài không đề cập kỹ năng đó.'),
('vocabulary','Which meaning of “pertinent” fits this passage?',['Beautifully designed','Relevant to the problem','Too costly to use','No longer available'],1,1,'pertinent to the problem','Pertinent to = liên quan đến vấn đề đang xét.')
],[
('“Aptitude” có phải “attitude” không?','Không. Aptitude là năng khiếu/khả năng tự nhiên, thường đi với for. Attitude là thái độ. Bài nói khả năng hiểu cách các bộ phận khớp nhau.',2,'an aptitude for understanding how parts fitted together.'),
('Vì sao không thể nói họ chắc chắn đã thay sai linh kiện?','Câu dùng might để nêu khả năng nếu thiếu thông tin. Đây là cảnh báo giả định, không phải tường thuật một lỗi chắc chắn xảy ra.',1,'Without that information, they might replace a part that was working correctly.')
])

make('room-for-a-change-of-plan','Room for a Change of Plan','B1','Du lịch & trải nghiệm','Một nhóm bạn học cách đổi kế hoạch chuyến đi mà không bỏ mục tiêu chính.',[
"Before their weekend trip, three friends created a timetable for almost every hour. They wanted to visit a museum, walk by the river and try a small restaurant recommended by a friend. The plan looked efficient on paper. However, they had left very little room for delays or unexpected opportunities.",
"On Saturday morning, their train arrived late. The first museum visit would therefore overrun the time they had reserved for lunch. At first, they tried to move every activity forward. This made the afternoon feel even more crowded. Eventually, they decided to leave out one shop that none of them particularly wanted to visit.",
"Later, they noticed a short walking tour starting near the river. On the spur of the moment, they joined it. The guide explained the stories behind a few old buildings, and the friends asked questions they would not have thought of on their own. The tour was not in their original plan, but it became one of their favourite experiences.",
"On Sunday, one friend felt tired and chose to pull out of the morning walk. The others went ahead and met her at lunch. Nobody treated the change as a failure. They returned home with fewer photographs than expected, but with a clearer idea of what made a trip enjoyable for them: shared choices, not a perfectly completed timetable."
],[
"Trước chuyến đi cuối tuần, ba người bạn lập lịch gần như từng giờ. Họ muốn thăm bảo tàng, đi dọc sông và thử một nhà hàng nhỏ được bạn giới thiệu. Kế hoạch có vẻ hiệu quả trên giấy. Tuy nhiên, họ chừa quá ít thời gian cho chậm trễ hoặc cơ hội bất ngờ.",
"Sáng thứ Bảy, tàu đến muộn. Vì vậy, chuyến thăm bảo tàng đầu tiên sẽ lấn vào thời gian đã dành cho bữa trưa. Lúc đầu, họ cố dời tất cả hoạt động về sau. Điều này khiến buổi chiều còn chật chội hơn. Cuối cùng, họ bỏ một cửa hàng mà không ai đặc biệt muốn đến.",
"Sau đó, họ thấy một tour đi bộ ngắn sắp bắt đầu gần sông. Theo hứng ngay lúc ấy, họ tham gia. Hướng dẫn viên kể chuyện phía sau vài tòa nhà cũ, và họ hỏi những câu mà nếu tự đi thì chưa chắc đã nghĩ tới. Tour không có trong lịch ban đầu nhưng trở thành một trải nghiệm họ thích nhất.",
"Chủ nhật, một người thấy mệt nên rút khỏi buổi đi bộ sáng. Hai người kia vẫn đi và gặp cô vào bữa trưa. Không ai coi thay đổi là thất bại. Họ về với ít ảnh hơn dự tính nhưng hiểu rõ hơn điều làm chuyến đi vui: cùng lựa chọn chứ không phải hoàn tất một lịch trình hoàn hảo."
],[
('efficient','adj','hiệu quả về cách sử dụng thời gian/nguồn lực',['well organised'],'using time or resources without much waste',0,'Efficient không tự bảo đảm kết quả đáng mong muốn; khác effective.'),
('overrun','v','kéo dài vượt quá thời gian dự kiến',['run beyond the allotted time'],'take longer than the time allowed',1,'Không dùng nghĩa tràn ngập/chiếm đóng trong câu này.'),
('leave out','phrase','bỏ ra, không đưa vào',['omit'],'not include something',1,''),
('On the spur of the moment','phrase','ngẫu hứng, không có kế hoạch từ trước',['spontaneously'],'without planning it in advance',2,'Cụm chuẩn dùng on, không phải in the spur of the moment.'),
('pull out of','phrase','rút khỏi việc tham gia',['withdraw from'],'stop taking part in something',3,'Không đồng nghĩa với step down trong mọi ngữ cảnh; step down thường là rời chức vụ.'),
('went ahead','phrase','vẫn tiến hành như dự định',['proceeded'],'continued with a plan',3,'Past tense của go ahead.')
],[
('fewer + plural countable noun','fewer photographs than expected','Fewer đi với danh từ đếm được số nhiều; less thường với danh từ không đếm được.','We took fewer bags this time.','Lần này chúng tôi mang ít túi hơn.'),
('not ... but ...','but with a clearer idea of what made a trip enjoyable','Sự tương phản chuyển trọng tâm từ số ảnh sang hiểu biết về trải nghiệm.','I want fewer tasks but better results.','Tôi muốn ít việc hơn nhưng kết quả tốt hơn.')
],[
('main_idea','What lesson do the friends take from the trip?',['Every hour must be planned','A flexible plan can support an enjoyable trip','Unexpected activities should be avoided','Taking photos is the only purpose of travel'],1,3,'shared choices, not a perfectly completed timetable.','Câu kết nhấn mạnh lựa chọn chung thay vì hoàn thành lịch tuyệt đối.'),
('detail','Which activity did they join without planning it in advance?',['A cooking class','A morning train journey','A short walking tour','A visit to a shop'],2,2,'On the spur of the moment, they joined it.','It chỉ short walking tour ở câu trước.'),
('tfng','All three friends took part in the Sunday morning walk.',['TRUE','FALSE','NOT GIVEN'],1,3,'one friend felt tired and chose to pull out of the morning walk.','Một người rút khỏi nên không phải cả ba đều đi.'),
('vocabulary','“Overrun” refers here to:',['ending earlier than planned','taking longer than the scheduled time','running faster than someone','paying less than expected'],1,1,'overrun the time they had reserved for lunch.','Overrun nói về việc vượt thời lượng, không phải chạy nhanh.')
],[
('“Pull out” có bằng “step down” không?','Trong bài, pull out of the walk là rút khỏi một hoạt động. Step down thường là rời chức vụ hoặc từ chức. Không nên dùng step down of the walk.',3,'pull out of the morning walk.'),
('“It” ở “they joined it” thay cho từ nào?','It thay cho a short walking tour, không phải river. Đọc câu liền trước giúp xác định đúng đại từ.',2,'they noticed a short walking tour starting near the river. On the spur of the moment, they joined it.')
])

make('the-useful-feature','The Useful Feature','B2','Công nghệ & thiết kế','Nhóm phát triển phát hiện số lượt nhấn không đủ để đánh giá ích lợi của một tính năng.',[
"A student team devised a reading application with an unusual feature: every unfamiliar word opened a colourful animation. During early demonstrations, visitors clicked repeatedly and praised the design. The team interpreted this enthusiasm as evidence that the feature supported learning. Yet the demonstrations measured immediate attention, not whether readers remembered words later.",
"To investigate further, the students invited a small group to read two short passages. One version included the animations; the other displayed a simple explanation. The comparison was not a rigorous experiment: the passages were different, and participants could choose which version to try first. Nevertheless, several comments raised a pertinent concern. Readers sometimes lost their place after closing an animation.",
"The prevailing assumption within the team had been that more interaction meant more learning. They now recognised that this reasoning was flawed. A high click count could reflect curiosity, confusion or repeated attempts to dismiss a window. It did not, by itself, distinguish between these possibilities. The students could not claim that the simpler version produced better learning either; their observations did not establish that result.",
"Rather than abandon every novel idea, the team made a deliberate change. Animations became optional, and readers could save a word without leaving the paragraph. The team planned a fairer comparison using the same reading material. Their central question had shifted from whether a feature looked impressive to whether it helped someone complete a reading task without unnecessary interruption."
],[
"Một nhóm sinh viên thiết kế ứng dụng đọc với tính năng khác lạ: mỗi từ chưa biết mở ra hoạt ảnh nhiều màu. Trong các buổi giới thiệu ban đầu, khách nhấn liên tục và khen thiết kế. Nhóm xem sự hào hứng là bằng chứng tính năng giúp học. Nhưng buổi giới thiệu đo sự chú ý tức thời, không phải khả năng nhớ từ sau đó.",
"Để tìm hiểu thêm, nhóm mời một số người đọc hai bài ngắn. Một phiên bản có hoạt ảnh; bản kia chỉ hiện lời giải thích đơn giản. Đây không phải thí nghiệm chặt chẽ: hai bài khác nhau, người tham gia còn được chọn thử bản nào trước. Dù vậy, vài nhận xét nêu lên mối lo liên quan trực tiếp: đôi khi người đọc mất chỗ đang đọc sau khi đóng hoạt ảnh.",
"Giả định phổ biến trong nhóm là tương tác nhiều hơn đồng nghĩa học nhiều hơn. Giờ họ nhận ra cách suy luận ấy có thiếu sót. Lượt nhấn cao có thể do tò mò, bối rối hoặc nhiều lần cố đóng cửa sổ. Tự nó không phân biệt được các khả năng ấy. Nhóm cũng không thể khẳng định bản đơn giản giúp học tốt hơn; quan sát chưa xác lập kết quả đó.",
"Thay vì bỏ mọi ý tưởng mới, nhóm chủ động điều chỉnh. Hoạt ảnh trở thành tùy chọn và người đọc có thể lưu từ mà không rời đoạn. Nhóm dự định so sánh công bằng hơn với cùng tài liệu đọc. Câu hỏi chính chuyển từ tính năng có ấn tượng hay không sang việc nó có giúp hoàn thành nhiệm vụ đọc mà không gây gián đoạn thừa hay không."
],[
('devised','v','nghĩ ra, thiết kế một cách làm',['designed','developed'],'created a plan or solution through thought',0,''),
('rigorous','adj','chặt chẽ, kỹ lưỡng về phương pháp',['thorough','careful'],'carried out with strict attention to method',1,''),
('prevailing','adj','phổ biến hoặc chiếm ưu thế trong bối cảnh đó',['dominant','widely held'],'held by most people in the relevant group',2,'Không đồng nghĩa với đúng. Giới hạn ở within the team trong bài.'),
('flawed','adj','có thiếu sót, sai sót trong lập luận',['faulty','unsound'],'containing an error or weakness',2,'Flawed reasoning tự nhiên; defective thường dùng về thứ không hoạt động đúng, không thay thế máy móc.'),
('novel','adj','mới, khác những gì quen thuộc',['new','original'],'new and unusual',3,'Ở đây là tính từ; novel (n) mới là tiểu thuyết.'),
('deliberate','adj','có chủ đích, đã cân nhắc',['intentional','considered'],'chosen intentionally rather than accidentally',3,'Không nhầm động từ deliberate: cân nhắc/thảo luận kỹ.')
],[
('not whether ...','not whether readers remembered words later.','Phủ định chính xác thứ đã được đo: sự chú ý được đo, còn khả năng ghi nhớ sau đó thì không.','The survey measured interest, not whether people actually bought the product.','Khảo sát đo sự quan tâm chứ không đo liệu mọi người thực sự mua sản phẩm hay không.'),
('did not, by itself, ...','It did not, by itself, distinguish between these possibilities.','By itself = chỉ riêng nó. Câu không nói số lượt nhấn vô dụng hoàn toàn, mà nói nó không đủ để phân biệt các nguyên nhân.','A high score does not, by itself, explain the result.','Chỉ riêng điểm cao không giải thích được kết quả.')
],[
('main_idea','What is the main point of the passage?',['Animations always prevent learning','All new features should be removed','Popular interactions are not sufficient evidence of learning value','A simple interface guarantees better test scores'],2,2,'A high click count could reflect curiosity, confusion or repeated attempts to dismiss a window.','Cùng số lượt nhấn có thể phản ánh nhiều nguyên nhân, không đủ chứng minh giá trị học tập.'),
('detail','Why was the initial comparison not rigorous?',['It used different passages and allowed participants to choose the order','Nobody participated','Only one version existed','The team had no application'],0,1,'the passages were different, and participants could choose which version to try first.','Cả hai giới hạn phương pháp được nêu trực tiếp.'),
('tfng','The observations established that the simpler version led to better learning.',['TRUE','FALSE','NOT GIVEN'],1,2,'their observations did not establish that result.','Đề hỏi đã xác lập kết quả hay chưa, và bài nói rõ chưa. Không suy diễn thành bản đơn giản chắc chắn kém hơn.'),
('vocabulary','In this context, “flawed” describes reasoning that:',['is very popular','contains a weakness or error','has been repaired physically','has never been discussed'],1,2,'this reasoning was flawed.','Flawed nói chất lượng lập luận có thiếu sót, không phải mức phổ biến.')
],[
('Vì sao nhiều lượt nhấn chưa chắc là học tốt?','Theo bài, lượt nhấn có thể xuất phát từ tò mò, bối rối hoặc cố đóng cửa sổ. Đây là nhiều cách giải thích cho cùng số liệu; chưa có phép đo ghi nhớ để chọn một cách.',2,'A high click count could reflect curiosity, confusion or repeated attempts to dismiss a window.'),
('“Flawed” có bằng “defective” tuyệt đối không?','Cả hai đều liên quan đến lỗi, nhưng không thay thế trong mọi kết hợp. Flawed reasoning là lập luận có thiếu sót; defective equipment thường là thiết bị lỗi/không hoạt động đúng.',2,'this reasoning was flawed.')
])

make('the-empty-shop','The Empty Shop','B2','Không gian đô thị','Một mặt bằng bỏ trống được thử dùng làm nơi học chung với kỳ vọng có giới hạn.',[
"An empty shop stood between a bakery and a bus stop for nearly two years. A residents' group saw it as an untapped resource: a place that might host quiet study sessions in the morning and practical workshops in the evening. Their proposal was bold, but it was not a plan to solve every problem in the neighbourhood with a single room.",
"Before seeking funding, the group asked who would administer the space. Enthusiasm alone would not open the doors, maintain a booking calendar or respond to complaints. A volunteer coordinator agreed to organise a three-month trial, provided that other members shared the routine work. The group also drew up rules in accordance with the conditions set by the building's owner.",
"The first timetable proved unrealistic. A craft session regularly overran, delaying the study group that followed. Rather than blame the participants, the organisers amended the timetable and allowed a gap between activities. They discovered that a flexible room still needed clear arrangements. Flexibility did not mean that every activity could happen at any time.",
"At the end of the trial, a sizeable number of residents wanted the project to continue. The organisers welcomed the interest but resisted describing the trial as a monumental success. They had not yet secured funding for another year, and several volunteers were about to leave. What they had demonstrated was narrower: under specific conditions, the room could serve more than one useful purpose."
],[
"Một cửa hàng bỏ trống nằm giữa tiệm bánh và trạm xe buýt gần hai năm. Nhóm cư dân xem đó là nguồn lực chưa khai thác: nơi có thể học yên tĩnh buổi sáng và tổ chức hoạt động thực hành buổi tối. Đề xuất táo bạo nhưng không phải kế hoạch giải quyết mọi vấn đề của khu dân cư bằng một căn phòng.",
"Trước khi xin kinh phí, nhóm hỏi ai sẽ quản lý không gian. Chỉ nhiệt tình không đủ để mở cửa, duy trì lịch đặt chỗ hay giải quyết phàn nàn. Một điều phối viên tình nguyện đồng ý tổ chức thử ba tháng với điều kiện các thành viên khác chia sẻ việc thường ngày. Nhóm cũng soạn quy định tuân theo điều kiện chủ tòa nhà đặt ra.",
"Lịch đầu tiên không thực tế. Buổi thủ công thường kéo quá giờ, làm nhóm học sau đó bị trễ. Thay vì trách người tham gia, ban tổ chức sửa lịch và chừa khoảng đệm giữa các hoạt động. Họ nhận ra phòng đa năng vẫn cần cách tổ chức rõ ràng. Linh hoạt không có nghĩa hoạt động nào cũng diễn ra lúc nào cũng được.",
"Cuối đợt thử, số cư dân đáng kể muốn tiếp tục. Nhóm hoan nghênh sự quan tâm nhưng không vội gọi thử nghiệm là thành công cực kỳ lớn. Họ chưa có kinh phí chắc chắn cho năm nữa và vài tình nguyện viên sắp rời đi. Điều đã chứng minh hẹp hơn: trong điều kiện cụ thể, căn phòng có thể phục vụ hơn một mục đích hữu ích."
],[
('untapped','adj','chưa được khai thác hoặc tận dụng',['unexploited','unused'],'available but not yet made use of',0,''),
('bold','adj','táo bạo, dám thử điều khó',['daring'],'willing to attempt something ambitious',0,'Không phải kiểu chữ in đậm trong ngữ cảnh này.'),
('administer','v','quản lý, điều hành',['manage'],'organise and run an activity or place',1,'Administer có nhiều nghĩa; ở đây không liên quan đến cấp thuốc.'),
('in accordance with','phrase','theo đúng, phù hợp với quy định/điều kiện',['in conformity with'],'following the requirements of',1,'Thường trang trọng và gắn với quy định/hướng dẫn.'),
('amended','v','đã sửa đổi để điều chỉnh/cải thiện',['revised'],'made changes to a document or arrangement',2,''),
('sizeable','adj','khá lớn, đáng kể về quy mô',['considerable','substantial'],'fairly large in amount or number',3,'Không tự mang mức độ cực lớn như monumental.')
],[
('provided that + clause','provided that other members shared the routine work.','Nêu điều kiện: với điều kiện những người khác cùng chia sẻ việc. Không phải khẳng định điều kiện tự động được đáp ứng.','You can borrow it provided that you return it tomorrow.','Bạn có thể mượn với điều kiện trả ngày mai.'),
('what-clause làm chủ ngữ','What they had demonstrated was narrower','What they had demonstrated = điều họ đã chứng minh. Cả mệnh đề làm chủ ngữ của was.','What we need is a clear plan.','Điều chúng ta cần là một kế hoạch rõ ràng.')
],[
('main_idea','Which statement best captures the passage?',['A shared space requires practical organisation as well as enthusiasm','An empty shop can solve all neighbourhood problems','Volunteers never need funding','Flexible spaces should have no timetable'],0,2,'a flexible room still needed clear arrangements.','Cả bài nhấn mạnh quản lý, điều kiện, lịch và giới hạn kết luận.'),
('detail','What change followed the craft sessions running late?',['The study group was permanently banned','A gap was added between activities','The building was sold','All sessions became shorter than ten minutes'],1,2,'allowed a gap between activities.','Nhóm sửa lịch và chừa khoảng đệm giữa các hoạt động.'),
('tfng','Funding for another year had already been secured at the end of the trial.',['TRUE','FALSE','NOT GIVEN'],1,3,'They had not yet secured funding for another year','Had not yet phủ định việc đã có nguồn kinh phí chắc chắn.'),
('vocabulary','Which phrase best explains “untapped resource”?',['A resource already used completely','A resource whose ownership is unknown','A resource not yet put to use','A resource that cannot be used'],2,0,'an untapped resource','Chưa khai thác không có nghĩa không thể khai thác.')
],[
('“Sizeable” và “monumental” khác nhau ở đây ra sao?','Sizeable nói lượng cư dân khá lớn. Monumental success nhấn mạnh thành công cực kỳ lớn/quan trọng; nhóm chủ động tránh mức khẳng định đó vì còn thiếu kinh phí và nhân lực.',3,'resisted describing the trial as a monumental success.'),
('“Flexibility did not mean ...” đang phản bác gì?','Nó phản bác việc đánh đồng linh hoạt với không có giới hạn. Phòng dùng cho nhiều mục đích vẫn phải có lịch rõ ràng.',2,'Flexibility did not mean that every activity could happen at any time.')
])

make('changing-the-club-rules','Changing the Club Rules','B2','Thể thao & tổ chức','Một câu lạc bộ cân nhắc sửa quy tắc quen thuộc để phù hợp với thành viên mới.',[
"For years, it was customary for members of a small sports club to practise at the same time every Saturday. The arrangement suited the founding members, most of whom lived nearby. As the club grew, however, several newcomers found that the fixed time conflicted with work or family commitments. They asked whether the schedule could be reconsidered.",
"The committee initially defended the conventional timetable. It was familiar, and changing it might inconvenience people who had attended for years. But a member pointed out that this argument overlooked those who could never attend in the first place. The attendance records showed who came, not everyone who wanted to come. Treating the records as a complete picture would therefore be misleading.",
"After a discussion, the committee devised a trial with two alternative sessions. The change was in line with the club's stated aim of widening participation, although it required additional volunteer time. Members were asked to report difficulties as well as benefits. The committee wanted feedback that could challenge the proposal, not simply praise it.",
"When the chair decided to step down for personal reasons, another member agreed to lead the trial. This did not mean that the project had been abandoned. At the end of two months, the club retained one additional session and reinstated the original starting time for the other. The final arrangement was a compromise rather than a complete rejection of the old routine."
],[
"Trong nhiều năm, thành viên một câu lạc bộ thể thao nhỏ có lệ tập cùng một giờ mỗi thứ Bảy. Cách này phù hợp với thành viên sáng lập, phần lớn sống gần đó. Nhưng khi câu lạc bộ phát triển, vài người mới thấy giờ cố định xung đột công việc hoặc trách nhiệm gia đình. Họ hỏi liệu có thể xem lại lịch không.",
"Ban đầu, ban điều hành bảo vệ lịch truyền thống. Nó quen thuộc và thay đổi có thể bất tiện cho người đã tham gia nhiều năm. Nhưng một thành viên chỉ ra rằng lập luận bỏ qua người không bao giờ đến được ngay từ đầu. Danh sách điểm danh cho biết ai đã đến, không phải tất cả ai muốn đến. Vì thế, xem đó là bức tranh đầy đủ sẽ gây hiểu sai.",
"Sau thảo luận, ban điều hành nghĩ ra đợt thử hai buổi thay thế nhau. Điều chỉnh phù hợp với mục tiêu mở rộng người tham gia, dù cần thêm thời gian tình nguyện. Thành viên được đề nghị báo cả khó khăn lẫn lợi ích. Ban muốn phản hồi có thể chất vấn đề xuất, không chỉ khen nó.",
"Khi chủ nhiệm quyết định rời vị trí vì lý do cá nhân, thành viên khác nhận dẫn dắt thử nghiệm. Điều đó không có nghĩa dự án bị bỏ. Sau hai tháng, câu lạc bộ giữ một buổi bổ sung và khôi phục giờ bắt đầu cũ cho buổi còn lại. Cách cuối cùng là sự dung hòa chứ không phủ nhận hoàn toàn nếp cũ."
],[
('customary','adj','theo lệ thường, theo thói quen đã có',['usual','traditional'],'normally done in a particular group',0,'Customary nhấn mạnh tập quán/lệ thường; conventional nhấn mạnh cách được chấp nhận phổ biến.'),
('conventional','adj','theo cách quen thuộc, truyền thống',['traditional','established'],'following an established way of doing things',1,'Không mặc nhiên có nghĩa lỗi thời hoặc sai.'),
('overlooked','v','đã bỏ sót, không tính đến',['failed to consider'],'did not notice or take account of',1,'Không phải nghĩa nhìn ra một cảnh quan.'),
('in line with','phrase','phù hợp, nhất quán với',['consistent with'],'agreeing with an aim or approach',2,'Không phải lúc nào cũng hàm ý tuân thủ quy định chặt như in accordance with.'),
('step down','phrase','rời chức vụ, từ chức',['resign'],'leave a position of responsibility',3,'Không dùng thay pull out of a walk/match một cách máy móc.'),
('reinstated','v','khôi phục lại điều đã thay đổi/bãi bỏ',['restored'],'put something back into its former position',3,'Động từ gốc: reinstate, không phải reinsate.')
],[
('most of whom','most of whom lived nearby','Mệnh đề quan hệ bổ sung cho founding members; whom thay người sau giới từ of.','I met five students, two of whom study IT.','Tôi gặp năm sinh viên, trong đó hai người học CNTT.'),
('not simply ...','not simply praise it.','Not simply hạn chế ý chỉ khen; không nói rằng lời khen bị cấm hoàn toàn.','We need evidence, not simply opinions.','Chúng ta cần bằng chứng, không chỉ ý kiến.')
],[
('main_idea','What is the central issue in the passage?',['Replacing every member of the club','Balancing an established routine with wider access','Removing all volunteer work','Choosing a new type of sport'],1,3,'a compromise rather than a complete rejection of the old routine.','Nhóm điều chỉnh lịch để dung hòa thói quen cũ và nhu cầu mới.'),
('detail','Why could attendance records give an incomplete picture?',['They included only people who actually came','They recorded every person in the city','They contained no dates','They were all destroyed'],0,1,'The attendance records showed who came, not everyone who wanted to come.','Người muốn đến nhưng không thể đến không hiện đầy đủ trong số liệu.'),
('tfng','The trial was abandoned when the chair stepped down.',['TRUE','FALSE','NOT GIVEN'],1,3,'another member agreed to lead the trial.','Có người khác tiếp tục phụ trách; bài còn nói rõ dự án không bị bỏ.'),
('vocabulary','“Reinstated” means the starting time was:',['removed permanently','put back as it had been before','kept secret','moved to another building'],1,3,'reinstated the original starting time','Khôi phục giờ ban đầu, không phải tạo giờ hoàn toàn mới.')
],[
('“Customary” có đồng nghĩa tuyệt đối với “conventional” không?','Hai từ gần nghĩa trong bài nhưng trọng tâm khác. Customary: việc nhóm thường làm theo lệ. Conventional: cách được xem là quen thuộc/truyền thống. Một sự việc customary không tự động được mọi nơi chấp nhận.',0,'it was customary for members of a small sports club to practise'),
('Chủ nhiệm “step down” thì dự án có ngừng không?','Không suy ra như vậy. Step down chỉ hành động rời chức vụ của một người; đoạn nói người khác nhận phụ trách nên dự án vẫn tiếp tục.',3,'another member agreed to lead the trial.')
])

make('a-slower-workshop','A Slower Workshop','B2','Nghệ thuật & kinh doanh','Một xưởng gốm điều chỉnh quy mô để giữ chất lượng thay vì nhận mọi đơn hàng.',[
"At a small ceramics workshop, orders increased sharply after a photograph of a blue bowl was shared online. The owner, Mara, welcomed the attention. She had spent years developing a recognisable style and hoped that the new interest would support the business. Soon, however, the prospect of accepting every order began to worry her.",
"The material was malleable when wet, but the work still demanded care. Each piece had to pass through several stages, and some would need to be made again. Mara could devise a faster way to arrange her tools, but she could not remove every waiting period from the process. A relentless schedule left her tired and made small errors more frequent.",
"One customer offered to commission a large collection for a hotel. It was a substantial undertaking for a workshop with only two people. Mara considered hiring temporary help, then calculated how much teaching and supervision would be required. She declined the proposed deadline rather than promise something she could not deliver. The customer later agreed to a smaller order with a longer schedule.",
"Mara also introduced occasional classes. These provided an additional source of income, but she did not regard teaching as effortless. Explaining a familiar movement to a beginner required its own preparation. By the end of the year, the workshop produced fewer items than its busiest month had suggested it might. Mara nevertheless considered the business stronger: she could explain its limits and choose work in line with them."
],[
"Tại xưởng gốm nhỏ, đơn đặt hàng tăng mạnh sau khi ảnh chiếc bát xanh được chia sẻ trên mạng. Chủ xưởng Mara đón nhận sự chú ý. Cô đã dành nhiều năm tạo phong cách dễ nhận ra và hy vọng sự quan tâm mới giúp việc kinh doanh. Nhưng rồi viễn cảnh nhận tất cả đơn bắt đầu khiến cô lo.",
"Vật liệu dễ tạo hình khi ướt, nhưng công việc vẫn cần cẩn thận. Mỗi sản phẩm qua nhiều công đoạn và một số phải làm lại. Mara có thể nghĩ ra cách xếp dụng cụ nhanh hơn nhưng không thể xóa mọi khoảng chờ trong quy trình. Lịch làm việc liên tục không ngơi khiến cô mệt và sai sót nhỏ xảy ra thường xuyên hơn.",
"Một khách muốn đặt làm bộ sưu tập lớn cho khách sạn. Đây là công việc đáng kể đối với xưởng chỉ có hai người. Mara cân nhắc thuê người tạm thời rồi tính thời gian cần dạy và giám sát. Cô từ chối hạn giao đề xuất thay vì hứa điều không thể thực hiện. Sau đó khách đồng ý đơn nhỏ hơn với lịch dài hơn.",
"Mara cũng mở lớp thỉnh thoảng. Chúng mang lại nguồn thu thêm nhưng cô không xem dạy học là việc dễ dàng không tốn sức. Giải thích động tác quen thuộc cho người mới cần chuẩn bị riêng. Cuối năm, xưởng làm ít đồ hơn mức tháng bận nhất từng khiến người ta kỳ vọng. Dù vậy, Mara coi doanh nghiệp vững hơn: cô có thể nói rõ giới hạn và chọn việc phù hợp."
],[
('the prospect of','phrase','viễn cảnh, khả năng sắp phải/làm điều gì',['the possibility of'],'the thought of something that may happen',0,'Sau of dùng danh từ hoặc V-ing. Prospect không có nghĩa chắc chắn sẽ xảy ra.'),
('malleable','adj','dễ uốn, dễ tạo hình',['easy to shape'],'able to be shaped without difficulty',1,'Nghĩa vật lý trong bài; đôi khi dùng bóng cho người/ý tưởng dễ chịu ảnh hưởng.'),
('relentless','adj','liên tục khắc nghiệt, không ngơi nghỉ',['unremitting'],'continuing intensely without a break',1,'Sắc thái mạnh; không đồng nghĩa đơn giản với hardworking.'),
('commission','v','đặt làm sản phẩm hoặc tác phẩm',['order specially'],'pay someone to create something for a purpose',2,'Ở đây là động từ đặt làm; commission (n) còn có thể là tiền hoa hồng/ủy ban.'),
('undertaking','n','công việc hoặc dự án đòi hỏi nỗ lực',['project','task'],'a piece of work that requires effort',2,'Viết undertaking, không phải undetaking. Trong ngữ cảnh khác còn nghĩa cam kết.'),
('supervision','n','sự giám sát, hướng dẫn công việc',['oversight'],'watching and guiding how work is done',2,'Không nhầm overlook = bỏ sót. Oversee = giám sát.')
],[
('the prospect of + V-ing','the prospect of accepting every order','Cụm danh từ nói về viễn cảnh thực hiện một việc. Of là giới từ nên dùng accepting.','The prospect of studying abroad excites her.','Viễn cảnh đi du học khiến cô ấy hào hứng.'),
('rather than + V','rather than promise something she could not deliver.','Đặt hai lựa chọn đối lập: từ chối thời hạn thay vì hứa điều không thể làm.','I asked for help rather than guess.','Tôi hỏi giúp đỡ thay vì đoán.')
],[
('main_idea','Why did Mara change the way she accepted work?',['To stop making ceramics entirely','To work within realistic limits while maintaining the business','To accept every deadline without question','To remove the need for preparation'],1,3,'she could explain its limits and choose work in line with them.','Câu kết nhấn mạnh hiểu giới hạn và chọn công việc phù hợp.'),
('detail','How did the hotel order change?',['It became larger and more urgent','It was replaced by a free class','It became smaller with more time allowed','It was accepted with the original deadline'],2,2,'a smaller order with a longer schedule.','Hai thay đổi là giảm số lượng và kéo dài thời gian.'),
('tfng','The classes became the workshop’s largest source of income.',['TRUE','FALSE','NOT GIVEN'],2,3,'These provided an additional source of income','Additional chỉ nguồn bổ sung; bài không cho tỷ trọng để xác nhận hay bác bỏ largest.'),
('vocabulary','Here, “commission” means to:',['pay someone to make something specially','cancel a payment','join a government committee','earn a percentage from a sale'],0,2,'commission a large collection for a hotel.','Commission là động từ đặt làm bộ sản phẩm, không phải danh từ tiền hoa hồng.')
],[
('“Commission” ở đây có phải tiền hoa hồng không?','Không. Nó đứng sau to và nhận tân ngữ a large collection, nên là động từ đặt làm. Nghĩa danh từ tiền hoa hồng thường thấy trong earn a commission.',2,'offered to commission a large collection for a hotel.'),
('Vì sao ít sản phẩm hơn mà Mara vẫn thấy doanh nghiệp mạnh hơn?','Đây là đánh giá của nhân vật dựa trên việc hiểu giới hạn và chọn đơn phù hợp, không phải kết luận sản lượng ít luôn làm doanh nghiệp mạnh.',3,'Mara nevertheless considered the business stronger: she could explain its limits and choose work in line with them.')
])

for lesson in LESSONS:
    (OUT/(lesson['slug']+'.json')).write_text(json.dumps(lesson,ensure_ascii=False,indent=2),encoding='utf-8')
print('Authored',len(LESSONS),'lessons,',sum(len(x['text'].split()) for x in LESSONS),'words')
print([(x['level'],x['slug'],len(x['text'].split())) for x in LESSONS])
