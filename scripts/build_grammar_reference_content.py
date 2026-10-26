"""Rebuild authored grammar reference data; no network or model calls."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data'

# Inflections are linguistic facts. Meanings, notes and teaching examples are original.
VERBS = '''arise|arose|arisen|phát sinh
awake|awoke|awoken|thức giấc
be|was/were|been|là; ở
bear|bore|borne/born|chịu đựng; mang
beat|beat|beaten|đánh; đánh bại
become|became|become|trở thành
begin|began|begun|bắt đầu
bend|bent|bent|uốn cong
bet|bet|bet|đánh cược
bind|bound|bound|buộc; gắn kết
bite|bit|bitten|cắn
bleed|bled|bled|chảy máu
blow|blew|blown|thổi
break|broke|broken|làm vỡ; hỏng
breed|bred|bred|nuôi sinh sản
bring|brought|brought|mang đến
broadcast|broadcast|broadcast|phát sóng
build|built|built|xây dựng
burn|burned/burnt|burned/burnt|đốt; cháy
burst|burst|burst|vỡ tung
buy|bought|bought|mua
catch|caught|caught|bắt; đón kịp
choose|chose|chosen|chọn
cling|clung|clung|bám chặt
come|came|come|đến
cost|cost|cost|có giá
creep|crept|crept|bò; rón rén đi
cut|cut|cut|cắt
deal|dealt|dealt|xử lý; giao dịch
dig|dug|dug|đào
do|did|done|làm
draw|drew|drawn|vẽ; kéo
dream|dreamed/dreamt|dreamed/dreamt|mơ
drink|drank|drunk|uống
drive|drove|driven|lái xe
eat|ate|eaten|ăn
fall|fell|fallen|rơi; ngã
feed|fed|fed|cho ăn
feel|felt|felt|cảm thấy
fight|fought|fought|chiến đấu; tranh cãi
find|found|found|tìm thấy
flee|fled|fled|chạy trốn
fly|flew|flown|bay
forbid|forbade|forbidden|cấm
forget|forgot|forgotten|quên
forgive|forgave|forgiven|tha thứ
freeze|froze|frozen|đóng băng
get|got|got/gotten|nhận; trở nên
give|gave|given|cho
go|went|gone|đi
grow|grew|grown|lớn lên; trồng
hang|hung|hung|treo
have|had|had|có
hear|heard|heard|nghe thấy
hide|hid|hidden|giấu; trốn
hit|hit|hit|đánh; va vào
hold|held|held|cầm; tổ chức
hurt|hurt|hurt|làm đau
keep|kept|kept|giữ
kneel|knelt/kneeled|knelt/kneeled|quỳ
know|knew|known|biết
lay|laid|laid|đặt; để
lead|led|led|dẫn dắt
lean|leaned/leant|leaned/leant|dựa; nghiêng
learn|learned/learnt|learned/learnt|học
leave|left|left|rời đi; để lại
lend|lent|lent|cho mượn
let|let|let|cho phép
lie|lay|lain|nằm
light|lit/lighted|lit/lighted|thắp sáng
lose|lost|lost|mất; thua
make|made|made|làm; tạo ra
mean|meant|meant|có nghĩa là
meet|met|met|gặp
mistake|mistook|mistaken|nhầm lẫn
overcome|overcame|overcome|vượt qua
pay|paid|paid|trả tiền
prove|proved|proved/proven|chứng minh
put|put|put|đặt
quit|quit|quit|bỏ; nghỉ
read|read|read|đọc
ride|rode|ridden|đi xe; cưỡi
ring|rang|rung|reo; gọi điện
rise|rose|risen|tăng; mọc lên
run|ran|run|chạy
say|said|said|nói
see|saw|seen|nhìn thấy
seek|sought|sought|tìm kiếm
sell|sold|sold|bán
send|sent|sent|gửi
set|set|set|đặt; thiết lập
shake|shook|shaken|lắc
shine|shone/shined|shone/shined|chiếu sáng; đánh bóng
shoot|shot|shot|bắn; quay phim
show|showed|shown|cho xem
shrink|shrank|shrunk|co lại
shut|shut|shut|đóng
sing|sang|sung|hát
sink|sank|sunk|chìm
sit|sat|sat|ngồi
sleep|slept|slept|ngủ
slide|slid|slid|trượt
smell|smelled/smelt|smelled/smelt|ngửi; có mùi
speak|spoke|spoken|nói
spell|spelled/spelt|spelled/spelt|đánh vần
spend|spent|spent|tiêu tiền; dành thời gian
spill|spilled/spilt|spilled/spilt|làm đổ
spin|spun|spun|quay
split|split|split|chia; tách
spread|spread|spread|lan; trải ra
stand|stood|stood|đứng
steal|stole|stolen|ăn cắp
stick|stuck|stuck|dính; mắc kẹt
sting|stung|stung|đốt; chích
strike|struck|struck|đánh; đình công
swear|swore|sworn|thề
sweep|swept|swept|quét
swim|swam|swum|bơi
swing|swung|swung|đung đưa
take|took|taken|lấy; mang
teach|taught|taught|dạy
tear|tore|torn|xé
tell|told|told|kể; bảo
think|thought|thought|nghĩ
throw|threw|thrown|ném
understand|understood|understood|hiểu
wake|woke|woken|thức dậy
wear|wore|worn|mặc; đeo
weep|wept|wept|khóc
win|won|won|thắng
withdraw|withdrew|withdrawn|rút lại; rút tiền
write|wrote|written|viết'''
NOTES = {
    'be': 'V2: I/he/she/it → was; you/we/they → were.',
    'bear': 'Born dùng khi nói được sinh ra (was born); borne dùng cho các nghĩa khác.',
    'cost': 'Cost–cost–cost khi nói có giá. Costed dùng khi tính hoặc dự toán chi phí.',
    'get': 'V3 got thường dùng trong Anh–Anh; gotten phổ biến trong Anh–Mỹ khi nói nhận được hoặc trở nên. Have got (có) vẫn dùng got.',
    'hang': 'Hung cho nghĩa treo đồ vật. Hanged thường dùng cho nghĩa hành hình bằng treo cổ.',
    'lie': 'Đây là lie = nằm. Lie = nói dối là động từ có quy tắc: lied–lied. Lay = đặt có dạng laid–laid.',
    'lay': 'Lay thường cần tân ngữ: lay the book on the desk. Lie = nằm: lie–lay–lain.',
    'read': 'Cùng cách viết; V1 đọc /riːd/, V2 và V3 đọc /red/.',
    'shine': 'Shone thường chỉ phát sáng; shined thường dùng khi đánh bóng một vật. Cách dùng còn tùy biến thể tiếng Anh.',
    'strike': 'Stricken còn được dùng trong một số cụm chỉ bị tác động nặng, như grief-stricken.',
    'show': 'Shown là V3 thông dụng; showed cũng có thể dùng làm V3 trong một số cách dùng Anh–Mỹ.'
}

def tense(id, title, uses, forms, signals, example, translation, note, lesson=None):
    return dict(id=id, title=title, uses=uses, forms=dict(zip(('affirmative','negative','question'),forms)),
                signals=[dict(zip(('word','meaning'),s)) for s in signals], example=example,
                translation_vi=translation, note=note, lesson_id=lesson)

TENSES = [
    tense('present-simple','Hiện tại đơn',
          ['Thói quen hoặc việc lặp lại.', 'Sự thật, đặc điểm hoặc trạng thái hiện tại.'],
          ['S + V / V-s, -es','S + do/does not + V','Do/Does + S + V?'],
          [('usually, often, sometimes','Tần suất: thường, hay, đôi khi.'),('every day / on Mondays','Việc lặp lại hằng ngày / mỗi thứ Hai.')],
          'Mai walks to work every morning.','Mai đi bộ đi làm mỗi sáng.',
          'V là động từ nguyên mẫu; S là chủ ngữ. Với be, dùng am/is/are, không dùng do/does. He/she/it đi với V-s/-es trong câu khẳng định.', 'a1-present-simple'),
    tense('present-continuous','Hiện tại tiếp diễn',
          ['Việc đang diễn ra lúc nói hoặc quanh thời điểm hiện tại.', 'Tình huống tạm thời; kế hoạch tương lai đã sắp xếp.'],
          ['S + am/is/are + V-ing','S + am/is/are not + V-ing','Am/Is/Are + S + V-ing?'],
          [('now, right now, at the moment','Việc đang diễn ra.'),('this week / these days','Giai đoạn tạm thời quanh hiện tại.')],
          'Mai is working from home this week.','Tuần này Mai đang làm việc ở nhà.',
          'Các động từ chỉ trạng thái như know, believe, own thường dùng hiện tại đơn trong nghĩa này. Không phải cứ thấy now là dùng tiếp diễn.', 'a2-present-continuous'),
    tense('present-perfect','Hiện tại hoàn thành',
          ['Trải nghiệm tính đến hiện tại, không nói rõ thời điểm đã kết thúc.', 'Việc đã xảy ra nhưng kết quả còn liên quan đến hiện tại.', 'Trạng thái bắt đầu trong quá khứ và vẫn tiếp tục.'],
          ['S + have/has + V3','S + have/has not + V3','Have/Has + S + V3?'],
          [('ever / never','Đã từng / chưa từng, khi nói về trải nghiệm.'),('just / already / yet','Vừa mới / đã rồi / chưa hoặc chưa vậy; yet thường ở cuối câu hỏi hoặc câu phủ định.'),('since / for','Since + mốc bắt đầu; for + khoảng thời gian.'),('so far / this week','Tính đến nay / tuần này khi khoảng thời gian vẫn đang tiếp diễn.')],
          'I have lived here since 2021.','Tôi sống ở đây từ năm 2021 đến nay.',
          'I/you/we/they dùng have; he/she/it dùng has. V3 là quá khứ phân từ: worked hoặc gone, seen… Khi nêu thời điểm đã kết thúc như yesterday, dùng quá khứ đơn.', 'b1-present-perfect'),
    tense('present-perfect-continuous','Hiện tại hoàn thành tiếp diễn',
          ['Nhấn mạnh hoạt động kéo dài từ trước đến nay.', 'Hoạt động vừa dừng và còn dấu hiệu ở hiện tại.'],
          ['S + have/has been + V-ing','S + have/has not been + V-ing','Have/Has + S + been + V-ing?'],
          [('for / since / how long','Khoảng thời gian / mốc bắt đầu / câu hỏi kéo dài bao lâu.'),('all morning / recently','Cả buổi sáng / gần đây, khi nhấn mạnh hoạt động.')],
          'I have been painting the kitchen all morning.','Tôi sơn bếp suốt từ sáng đến giờ.',
          'Thì này tập trung vào quá trình, không khẳng định công việc đã xong. Với know hoặc own ở nghĩa trạng thái, thường dùng hiện tại hoàn thành đơn.'),
    tense('past-simple','Quá khứ đơn',
          ['Sự việc hoặc thói quen thuộc một khoảng thời gian đã kết thúc.', 'Kể các sự việc nối tiếp trong quá khứ.'],
          ['S + V2 / V-ed','S + did not + V','Did + S + V?'],
          [('yesterday / last week / in 2020','Thời điểm hoặc khoảng thời gian đã kết thúc.'),('two days ago','Cách đây hai ngày.')],
          'We visited Hue last summer.','Chúng tôi đến Huế hè năm ngoái.',
          'Sau did/did not dùng V nguyên mẫu: Did she go?, không phải Did she went? Với be, dùng was/were và đảo lên đầu câu hỏi.', 'a2-past-simple'),
    tense('past-continuous','Quá khứ tiếp diễn',
          ['Việc đang diễn ra tại một thời điểm trong quá khứ.', 'Bối cảnh đang tiếp diễn khi một sự việc khác xảy ra.'],
          ['S + was/were + V-ing','S + was/were not + V-ing','Was/Were + S + V-ing?'],
          [('at 8 p.m. yesterday','Một mốc quá khứ, khi nhấn mạnh việc đang diễn ra lúc đó.'),('while / when','Nối các sự việc; phải xem việc nào đang diễn ra, việc nào xảy đến.')],
          'I was cooking when the phone rang.','Tôi đang nấu ăn thì điện thoại reo.',
          'I/he/she/it dùng was; you/we/they dùng were. While và when không tự quyết định thì của động từ.', 'b1-past-continuous'),
    tense('past-perfect','Quá khứ hoàn thành',
          ['Việc đã hoàn tất trước một mốc hoặc một sự việc khác trong quá khứ.', 'Làm rõ thứ tự trước–sau khi kể chuyện quá khứ.'],
          ['S + had + V3','S + had not + V3','Had + S + V3?'],
          [('by the time / already','Đến lúc một việc quá khứ xảy ra, việc kia đã xong.'),('before / after','Gợi quan hệ trước–sau; không phải lúc nào cũng bắt buộc dùng had.')],
          'When I arrived, the meeting had started.','Khi tôi đến, cuộc họp đã bắt đầu rồi.',
          'Dùng had cho mọi chủ ngữ. Cần một điểm nhìn trong quá khứ; không dùng chỉ vì sự việc xảy ra rất lâu trước đây.', 'b2-past-perfect'),
    tense('past-perfect-continuous','Quá khứ hoàn thành tiếp diễn',
          ['Nhấn mạnh một hoạt động đã kéo dài đến trước một mốc trong quá khứ.', 'Giải thích nguyên nhân của tình trạng ở thời điểm quá khứ.'],
          ['S + had been + V-ing','S + had not been + V-ing','Had + S + been + V-ing?'],
          [('for two hours / since morning','Khoảng thời gian tính đến một mốc quá khứ.'),('before / when','Mốc quá khứ mà hoạt động đã kéo dài đến trước đó.')],
          'We had been walking for hours, so we were tired.','Chúng tôi đã đi bộ hàng giờ nên lúc đó rất mệt.',
          'Dùng để nhấn mạnh quá trình trước mốc quá khứ. Với trạng thái như know, thường dùng had known.'),
    tense('future-simple','Tương lai đơn · will',
          ['Dự đoán, lời hứa hoặc lời đề nghị giúp đỡ.', 'Quyết định ngay lúc nói.'],
          ['S + will + V','S + will not (won’t) + V','Will + S + V?'],
          [('tomorrow / next week','Mốc tương lai; cũng có thể đi với các cách diễn đạt tương lai khác.'),('I think / probably','Thường gặp khi đưa ra dự đoán.')],
          'That bag looks heavy. I will carry it for you.','Túi đó có vẻ nặng. Để tôi xách giúp bạn.',
          'Kế hoạch đã có thường dùng be going to; lịch hẹn đã thu xếp có thể dùng hiện tại tiếp diễn. Không chọn will chỉ vì thấy tomorrow.', 'a2-future'),
    tense('future-continuous','Tương lai tiếp diễn',
          ['Việc sẽ đang diễn ra tại một thời điểm trong tương lai.'],
          ['S + will be + V-ing','S + will not be + V-ing','Will + S + be + V-ing?'],
          [('at this time tomorrow','Vào giờ này ngày mai.'),('at 9 a.m. next Monday','Một mốc tương lai, khi nhấn mạnh quá trình đang diễn ra.')],
          'At this time tomorrow, I will be flying to Hanoi.','Giờ này ngày mai, tôi sẽ đang bay đến Hà Nội.',
          'Hình dung bạn dừng thời gian ở mốc tương lai đó: hoạt động nào sẽ đang diễn ra?'),
    tense('future-perfect','Tương lai hoàn thành',
          ['Việc sẽ hoàn tất trước hoặc chậm nhất vào một mốc tương lai.'],
          ['S + will have + V3','S + will not have + V3','Will + S + have + V3?'],
          [('by Friday / by then','Chậm nhất vào thứ Sáu / đến lúc đó.'),('by the time + hiện tại đơn','Mốc tương lai trong mệnh đề thời gian.')],
          'By Friday, I will have finished the report.','Đến thứ Sáu, tôi sẽ làm xong báo cáo.',
          'Trong mệnh đề thời gian chỉ tương lai sau by the time, thường dùng hiện tại đơn: by the time you arrive.'),
    tense('future-perfect-continuous','Tương lai hoàn thành tiếp diễn',
          ['Nhấn mạnh hoạt động sẽ kéo dài được bao lâu tính đến một mốc tương lai.'],
          ['S + will have been + V-ing','S + will not have been + V-ing','Will + S + have been + V-ing?'],
          [('for + khoảng thời gian, by + mốc','Kết hợp khoảng thời gian với điểm nhìn trong tương lai.')],
          'By noon, we will have been travelling for six hours.','Đến trưa, chúng tôi sẽ đi được sáu tiếng liên tục.',
          'Thường dùng khi thời lượng của hoạt động là điều muốn nhấn mạnh. Không cần dùng cấu trúc dài này nếu câu đơn giản hơn đã diễn đạt đúng ý.')
]

def comparison(id, title, tip, left, right):
    def side(row): return dict(zip(('title','use','example','translation_vi'),row))
    return dict(id=id,title=title,tip=tip,sides=[side(left),side(right)])

COMPARISONS = [
    comparison('present-simple-continuous','Hiện tại đơn hay hiện tại tiếp diễn?',
        'Hỏi: đây là thói quen nói chung, hay việc đang diễn ra / chỉ tạm thời?',
        ['Hiện tại đơn','Thói quen ổn định.','I work in the office.','Tôi làm việc ở văn phòng (thường lệ).'],
        ['Hiện tại tiếp diễn','Tình huống tạm thời.','I am working from home this week.','Tuần này tôi đang làm việc ở nhà.']),
    comparison('past-simple-present-perfect','Quá khứ đơn hay hiện tại hoàn thành?',
        'Nếu thời điểm đã kết thúc là trọng tâm, dùng quá khứ đơn. Nếu nhìn từ hiện tại vào trải nghiệm, kết quả hoặc trạng thái còn tiếp tục, cân nhắc hiện tại hoàn thành.',
        ['Quá khứ đơn','Khoảng thời gian đã kết thúc.','I lived in Hue for three years.','Tôi từng sống ở Huế ba năm (nay không còn sống ở đó).'],
        ['Hiện tại hoàn thành','Trạng thái vẫn tiếp tục đến nay.','I have lived in Hue for three years.','Tôi sống ở Huế được ba năm rồi (hiện vẫn ở đó).']),
    comparison('past-simple-continuous','Quá khứ đơn hay quá khứ tiếp diễn?',
        'Trong “I was cooking when the phone rang”, nấu ăn là việc đang diễn ra; điện thoại reo là sự việc xảy đến. Đừng chỉ nhìn when hoặc while để chọn thì.',
        ['Quá khứ đơn','Kể một sự việc đã xảy ra.','The phone rang at eight.','Điện thoại reo lúc tám giờ.'],
        ['Quá khứ tiếp diễn','Tả việc đang diễn ra tại một mốc.','I was cooking at eight.','Lúc tám giờ, tôi đang nấu ăn.']),
    comparison('past-simple-perfect','Quá khứ đơn hay quá khứ hoàn thành?',
        'Chọn mốc quá khứ trước, rồi hỏi việc nào đã xảy ra trước mốc đó. Không phải câu nào có hai hành động quá khứ cũng cần had.',
        ['Quá khứ đơn','Kể sự việc ở mốc chính.','When I arrived, the meeting started.','Khi tôi đến, cuộc họp bắt đầu.'],
        ['Quá khứ hoàn thành','Sự việc đã xảy ra trước mốc chính.','When I arrived, the meeting had started.','Khi tôi đến, cuộc họp đã bắt đầu rồi.']),
    comparison('perfect-simple-continuous','Hoàn thành đơn hay hoàn thành tiếp diễn?',
        'Bạn muốn nhấn mạnh kết quả / số lượng hay quá trình / thời lượng? Một số câu với live hoặc work dùng được cả hai, tùy trọng tâm.',
        ['Hiện tại hoàn thành','Kết quả đã đạt được.','I have painted the kitchen.','Tôi sơn xong bếp rồi.'],
        ['Hiện tại hoàn thành tiếp diễn','Quá trình; chưa nói rõ đã xong hay chưa.','I have been painting the kitchen all morning.','Tôi sơn bếp suốt từ sáng đến giờ.']),
    comparison('will-going-to','Will, going to hay hiện tại tiếp diễn?',
        'Will thường cho quyết định ngay lúc nói; going to thường cho ý định có sẵn hoặc dự đoán dựa trên dấu hiệu. Với lịch hẹn đã thu xếp: “I am meeting Lan at six.” Các cách dùng có thể giao nhau tùy ngữ cảnh.',
        ['Will','Quyết định lúc nói hoặc đề nghị giúp.','I will call the restaurant for you.','Để tôi gọi nhà hàng giúp bạn.'],
        ['Be going to','Ý định đã có từ trước.','I am going to call the restaurant tonight.','Tối nay tôi định gọi nhà hàng.'])
]

LESSON_GUIDES = {
    'a1-present-simple': (['present-simple'], ['present-simple-continuous']),
    'a2-present-continuous': (['present-continuous'], ['present-simple-continuous']),
    'a2-past-simple': (['past-simple'], ['past-simple-present-perfect','past-simple-continuous']),
    'a2-future': (['future-simple'], ['will-going-to']),
    'b1-present-perfect': (['present-perfect'], ['past-simple-present-perfect','perfect-simple-continuous']),
    'b1-past-continuous': (['past-continuous'], ['past-simple-continuous']),
    'b2-past-perfect': (['past-perfect'], ['past-simple-perfect']),
}

def build():
    verbs=[]
    for line in VERBS.splitlines():
        base,past,participle,meaning=line.split('|')
        verbs.append(dict(base=base,past=past.split('/'),participle=participle.split('/'),meaning_vi=meaning,note=NOTES.get(base,'')))
    data=dict(version=1,verbs=verbs,tenses=TENSES,comparisons=COMPARISONS,lesson_guides={
        k:dict(tenses=v[0],comparisons=v[1]) for k,v in LESSON_GUIDES.items()}, source_urls=[
        'https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference/irregular-verbs',
        'https://dictionary.cambridge.org/grammar/british-grammar/table-of-irregular-verbs',
        'https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/present-perfect-simple-continuous'])
    (ROOT/'grammar_reference.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {len(verbs)} verbs, {len(TENSES)} tense summaries and {len(COMPARISONS)} comparisons.')

if __name__ == '__main__': build()
