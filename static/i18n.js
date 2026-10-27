'use strict';
/* Local interface dictionaries only. Learning passages, answers and user input are never translated. */
(()=>{
const languages=['vi','en','fr','zh'];
const rows=[
['skip','Đến nội dung chính','Skip to content','Aller au contenu','跳转到正文'],
['login','Đăng nhập →','Sign in →','Se connecter →','登录 →'],
['nav.library','Thư viện','Library','Bibliothèque','阅读库'],
['nav.practice','IELTS & TOEIC','IELTS & TOEIC','IELTS & TOEIC','IELTS 与 TOEIC'],
['nav.method','Cách học','How it works','Comment apprendre','学习方法'],
['hero.chip','Một thói quen nhỏ. Một thế giới rộng hơn.','A small habit. A bigger world.','Une petite habitude. Un monde plus grand.','一个小习惯，一个更大的世界。'],
['hero.title1','Đọc một chút.','Read a little.','Lisez un peu.','每天读一点。'],
['hero.title2','Tiến xa mỗi ngày.','Grow every day.','Avancez chaque jour.','每天进一步。'],
['hero.copy','Khám phá những câu chuyện vừa sức, hiểu từ trong ngữ cảnh và nhớ lâu hơn. Từ bài đọc đầu tiên đến hành trình IELTS của bạn.','Discover stories at your level, learn words in context and remember more. From your first reading to your IELTS journey.','Découvrez des histoires à votre niveau, apprenez les mots en contexte et retenez-les. De votre première lecture à votre parcours IELTS.','发现适合自己水平的故事，在语境中理解词汇并加深记忆。从第一篇阅读开始，逐步走向雅思学习。'],
['hero.start','Tìm bài đọc của bạn ↗','Find your next read ↗','Trouvez votre lecture ↗','找到适合你的文章 ↗'],
['hero.practice','Luyện IELTS & TOEIC','Practise IELTS & TOEIC','Préparer IELTS et TOEIC','练习 IELTS 与 TOEIC'],
['hero.caption','Có bản dịch, câu hỏi và lời giải trong từng bài.','Translations, questions and explanations in every lesson.','Traductions, questions et explications dans chaque leçon.','每篇文章均配有翻译、问题和解析。'],
['demo.label','MỘT TRANG SÁCH, MỘT ĐIỀU MỚI','A NEW PAGE, A NEW DISCOVERY','UNE PAGE, UNE DÉCOUVERTE','读一页，发现新知'],
['demo.meaning','tò mò, muốn tìm hiểu','wanting to know or learn more','curieux, qui souhaite en savoir plus','好奇的，想了解更多的'],
['demo.save','+ Thử lưu từ','+ Try saving','+ Essayer','+ 试着保存'],
['demo.saved','✓ Đã thử lưu','✓ Tried it','✓ Essayé','✓ 已体验'],
['demo.caption','Thử một thao tác nhỏ trong hành trình học.','Try one small step in your learning journey.','Essayez un premier geste pour apprendre.','体验学习过程中的一小步。'],
['demo.done','Đây là bản minh họa. Đăng nhập để lưu vào kho từ của bạn.','This is a demo. Sign in to save words to your vocabulary.','Ceci est une démo. Connectez-vous pour enregistrer vos mots.','这是演示。登录后即可保存到你的词库。'],
['stats.readings','bài đọc theo trình độ','graded reading lessons','lectures par niveau','分级阅读文章'],
['stats.levels','từ cơ bản đến nâng cao','from beginner to advanced','du débutant à avancé','从入门到高级'],
['stats.ielts','bài luyện IELTS Reading','IELTS reading exercises','lectures IELTS','雅思阅读练习'],
['stats.toeic','bộ luyện TOEIC','TOEIC practice sets','séries TOEIC','TOEIC 练习套题'],
['library.eyebrow','BẮT ĐẦU TỪ NƠI BẠN ĐANG ĐỨNG','START WHERE YOU ARE','COMMENCEZ À VOTRE NIVEAU','从你现在的水平开始'],
['library.title','Một bài đọc vừa sức với bạn.','A good read at your level.','Une lecture à votre portée.','找到适合你的阅读。'],
['library.copy','Chọn trình độ và tìm một bài bạn muốn đọc hôm nay.','Choose a level and find something you want to read today.','Choisissez un niveau et une lecture pour aujourd’hui.','选择级别，找一篇今天想读的文章。'],
['level.a1','Khởi đầu','Beginner','Débutant','入门'],['level.a2','Nền tảng','Elementary','Élémentaire','基础'],['level.b1','Tự tin','Intermediate','Intermédiaire','中级'],['level.b2','Bứt phá','Upper intermediate','Intermédiaire avancé','中高级'],['level.c1','Nâng cao','Advanced','Avancé','高级'],
['level.a1copy','Câu ngắn, ý rõ ràng','Short, clear sentences','Des phrases simples','简短清晰的句子'],['level.a2copy','Chuyện đời thường','Everyday stories','La vie quotidienne','日常生活故事'],['level.b1copy','Kết nối các ý','Connecting ideas','Relier les idées','连接观点'],['level.b2copy','Đọc sâu, hiểu rộng','Read between the lines','Lire entre les lignes','深入理解'],['level.c1copy','Ý nghĩa và lập luận','Meaning and argument','Sens et argumentation','含义与论证'],
['filter.general','Đọc hằng ngày','Everyday reading','Lecture quotidienne','日常阅读'],['filter.allLevels','Mọi trình độ','All levels','Tous les niveaux','所有级别'],
['library.search','Tìm bài đọc hoặc chủ đề…','Search readings or topics…','Rechercher une lecture ou un thème…','搜索文章或主题…'],
['library.count','{count} bài phù hợp','{count} readings found','{count} lectures trouvées','找到 {count} 篇文章'],
['library.empty','Chưa có bài phù hợp. Thử trình độ hoặc từ khóa khác nhé.','No matching readings. Try another level or search term.','Aucune lecture trouvée. Essayez un autre niveau ou mot-clé.','暂无匹配文章，请尝试其他级别或关键词。'],
['library.more','Xem thêm bài đọc ↓','Show more readings ↓','Voir plus de lectures ↓','查看更多文章 ↓'],
['library.preparing','Thư viện đang được chuẩn bị.','The library is being prepared.','La bibliothèque est en préparation.','阅读库正在准备中。'],
['estimated','ước lượng','estimated','estimé','估计'],['reading.short','Đọc mỗi ngày','Daily reading','Lecture du jour','每日阅读'],['words','từ','words','mots','词'],['questions','câu hỏi','questions','questions','道题'],['vocabItems','mục từ','vocabulary items','mots à apprendre','个词汇'],
['card.support','Bản dịch & lời giải có sẵn','Translation & explanations','Traduction et explications','附翻译与解析'],['card.start','Bắt đầu đọc →','Start reading →','Commencer →','开始阅读 →'],
['practice.eyebrow','MỘT MỤC TIÊU. MỘT BƯỚC TIẾN.','ONE GOAL. ONE STEP FORWARD.','UN OBJECTIF. UN PAS EN AVANT.','一个目标，一步进展'],['practice.title','Luyện đúng hướng bạn cần.','Practise with a purpose.','Entraînez-vous avec un objectif.','朝着你的目标练习。'],
['ielts.chip','Đọc học thuật · B1–C1','Academic reading · B1–C1','Lecture académique · B1–C1','学术阅读 · B1–C1'],
['ielts.copy','Luyện tìm bằng chứng, phân biệt True / False / Not Given và chọn đáp án. Mỗi bài đều có lời giải để hiểu vì sao.','Find evidence, practise True / False / Not Given and multiple choice. Understand the reasoning behind each answer.','Repérez les preuves, travaillez True / False / Not Given et les QCM. Comprenez le raisonnement derrière chaque réponse.','练习定位证据、判断 True / False / Not Given 和选择题。通过解析理解每个答案的依据。'],
['ielts.start','Khám phá IELTS →','Explore IELTS →','Découvrir IELTS →','探索雅思阅读 →'],
['ielts.note','Bài luyện kỹ năng tự biên soạn, không phải đề thi chính thức hay bài thi thử đầy đủ; không quy đổi band.','Original skill exercises, not official papers or full mock tests. Scores are not converted to IELTS bands.','Exercices originaux, ni sujets officiels ni examens blancs complets. Les scores ne sont pas convertis en bandes IELTS.','原创技能练习，非官方试题或完整模拟考试，分数不换算为雅思等级。'],
['toeic.chip','Tiếng Anh trong công việc','English for the workplace','L’anglais au travail','职场英语'],
['toeic.copy','Củng cố ngữ pháp và từ vựng với Part 5–6, rồi luyện đọc email, thông báo và văn bản với Part 7.','Build grammar and vocabulary with Parts 5–6, then practise emails, notices and texts in Part 7.','Consolidez grammaire et vocabulaire avec les parties 5–6, puis lisez e-mails, annonces et textes dans la partie 7.','通过 Part 5–6 巩固语法和词汇，再通过 Part 7 练习邮件、通知和文章阅读。'],
['toeic.start','Luyện TOEIC →','Practise TOEIC →','Pratiquer le TOEIC →','开始 TOEIC 练习 →'],['toeic.note','Nội dung tự biên soạn, không phải đề ETS chính thức.','Original practice content, not official ETS test material.','Contenu original, non issu des tests officiels ETS.','原创练习内容，非 ETS 官方试题。'],['preview','Xem các bài','Browse exercises','Voir les exercices','浏览练习'],
['method.eyebrow','ÍT MỖI NGÀY. NHỚ LÂU HƠN.','A LITTLE EACH DAY. REMEMBER MORE.','UN PEU CHAQUE JOUR. RETENEZ PLUS.','每天一点，记得更久'],['method.title','Biến điều vừa đọc thành điều bạn nhớ.','Turn what you read into what you remember.','Retenez ce que vous venez de lire.','让读过的内容成为记住的知识。'],
['method.read','Đọc theo nhịp của bạn','Read at your own pace','Lisez à votre rythme','按自己的节奏阅读'],['method.readCopy','Đọc tiếng Anh trước, mở bản dịch khi cần. Từng đoạn ngắn giúp bạn không bị ngợp.','Read in English first and reveal the translation when needed. Short paragraphs keep it manageable.','Lisez d’abord en anglais et affichez la traduction si besoin. Avancez paragraphe par paragraphe.','先读英语，需要时再查看翻译。短段落让阅读更轻松。'],
['method.save','Giữ lại từ có ý nghĩa','Keep the words that matter','Gardez les mots utiles','留下有意义的词汇'],['method.saveCopy','Bôi đen từ ngay trong bài để lưu cả nghĩa lẫn ngữ cảnh. Không cần chép sang một ứng dụng khác.','Select a word in the text to save its meaning and context. No need to copy it into another app.','Sélectionnez un mot pour garder son sens et son contexte. Inutile de le recopier ailleurs.','在文章中选中词汇，保存含义和语境，无需复制到其他应用。'],
['method.review','Gặp lại trước khi quên','Meet them again before you forget','Révisez avant d’oublier','在遗忘前再次相遇'],['method.reviewCopy','Ôn bằng flashcard và bài tập. Lịch ôn thay đổi theo mức ghi nhớ của chính bạn.','Review with flashcards and exercises. Your schedule adapts to how well you remember.','Révisez avec des cartes et des exercices. Le calendrier s’adapte à votre mémorisation.','通过闪卡和练习复习，复习计划会根据你的记忆情况调整。'],
['cta.eyebrow','BÀI ĐỌC TIẾP THEO ĐANG CHỜ','YOUR NEXT READ IS WAITING','VOTRE PROCHAINE LECTURE VOUS ATTEND','下一篇阅读正等着你'],['cta.title','Bắt đầu từ một trang, hôm nay.','Start with one page, today.','Commencez par une page, aujourd’hui.','今天，从一页开始。'],['cta.copy','Đăng nhập để giữ bài đã đọc, từ đã lưu và những bước tiến nhỏ của bạn.','Sign in to keep your readings, saved words and small steps forward.','Connectez-vous pour conserver vos lectures, vos mots et vos progrès.','登录以保存已读文章、词汇和点滴进步。'],['cta.start','Vào không gian học ↗','Enter your learning space ↗','Accéder à mon espace ↗','进入学习空间 ↗'],
['footer','Đọc. Khám phá. Ghi nhớ.','Read. Discover. Remember.','Lire. Découvrir. Retenir.','阅读。探索。记忆。'],['footer.link','Tìm câu chuyện tiếp theo ↑','Find your next story ↑','Trouver la prochaine histoire ↑','寻找下一个故事 ↑'],
['auth.eyebrow','MỖI LẦN TRỞ LẠI, MỘT BƯỚC XA HƠN','EVERY RETURN IS A STEP FORWARD','CHAQUE RETOUR EST UN PAS EN AVANT','每次回来，都更进一步'],['auth.storyTitle','Thế giới rộng hơn qua từng trang đọc.','A bigger world, one page at a time.','Un monde plus grand, page après page.','每读一页，世界就更宽广。'],['auth.storyCopy','Một câu chuyện mới, vài từ đáng nhớ. Không gian học của bạn luôn sẵn sàng khi bạn trở lại.','A new story, a few words worth keeping. Your learning space is ready whenever you return.','Une nouvelle histoire, quelques mots à retenir. Votre espace vous attend à chaque retour.','一个新故事，几个值得记住的词。你的学习空间随时等你回来。'],
['auth.welcome','CHÀO MỪNG BẠN TRỞ LẠI','WELCOME BACK','BON RETOUR','欢迎回来'],['auth.title','Tiếp tục hành trình của bạn.','Pick up where you left off.','Reprenez votre parcours.','继续你的学习之旅。'],['auth.copy','Đăng nhập để mở bài đọc, kho từ và lịch ôn dành riêng cho bạn.','Sign in to your readings, vocabulary and personal review schedule.','Connectez-vous à vos lectures, votre vocabulaire et vos révisions.','登录查看你的文章、词库和个人复习计划。'],['auth.email','Địa chỉ email','Email address','Adresse e-mail','电子邮箱'],['auth.password','Mật khẩu','Password','Mot de passe','密码'],['auth.show','Hiện','Show','Voir','显示'],['auth.hide','Ẩn','Hide','Masquer','隐藏'],['auth.submit','Đăng nhập và bắt đầu học →','Sign in and start learning →','Se connecter et apprendre →','登录并开始学习 →'],
['auth.noAccount','Bạn chưa có tài khoản hoặc quên mật khẩu?','Need an account or a password reset?','Besoin d’un compte ou d’un nouveau mot de passe ?','需要账号或重置密码？'],['auth.contact','Liên hệ người đã giới thiệu LexiRead cho bạn để được cấp tài khoản hoặc hỗ trợ đặt lại mật khẩu.','Contact the person who introduced you to LexiRead for an account or help resetting your password.','Contactez la personne qui vous a présenté LexiRead pour obtenir un compte ou réinitialiser votre mot de passe.','请联系向你介绍 LexiRead 的人，获取账号或密码重置帮助。'],['auth.back','← Quay lại khám phá thư viện','← Back to the library','← Retour à la bibliothèque','← 返回阅读库'],['auth.error','Email hoặc mật khẩu chưa đúng. Hãy kiểm tra và thử lại nhé.','The email or password is incorrect. Please check and try again.','L’e-mail ou le mot de passe est incorrect. Vérifiez et réessayez.','邮箱或密码不正确，请检查后重试。'],['auth.throttled','Bạn đã thử đăng nhập quá nhiều lần. Vui lòng thử lại sau 15 phút.','Too many sign-in attempts. Please try again in 15 minutes.','Trop de tentatives. Réessayez dans 15 minutes.','登录尝试过多，请在 15 分钟后重试。'],
['app.contentLanguage','Ngôn ngữ giao diện thay đổi; bài học tiếng Anh và giải thích tiếng Việt được giữ nguyên.','The interface language changes; English lessons and Vietnamese explanations stay unchanged.','La langue de l’interface change ; les leçons en anglais et les explications en vietnamien sont conservées.','仅切换界面语言；英语课文和越南语解析保持不变。'],
['app.ieltsTitle','Luyện IELTS Reading','IELTS Reading practice','Entraînement IELTS Reading','雅思阅读练习'],['app.ieltsLead','Đọc có chiến lược. Trả lời có bằng chứng.','Read strategically. Answer with evidence.','Lisez avec méthode. Répondez avec des preuves.','有策略地阅读，有依据地作答。'],['app.ieltsSkills','Bắt đầu với một bài, đọc kỹ và đối chiếu lời giải. Tiến độ và từ vựng được lưu cùng tài khoản học của bạn.','Start with one passage, read closely and review the explanations. Progress and vocabulary stay in your learning account.','Commencez par un texte et étudiez les explications. Vos progrès et votre vocabulaire sont conservés dans votre compte.','从一篇文章开始，仔细阅读并核对解析。进度和词汇会保存在你的学习账号中。'],
];
// Existing screens use Vietnamese source labels. Exact matches avoid changing learning content.
const legacy=[
["Chọn bộ từ, học qua ví dụ và lưu vào kho riêng.","Choose a collection, learn through examples and save your words.","Choisissez une collection, apprenez avec des exemples et gardez vos mots.","选择词集，通过例句学习并保存单词。"],
["Làm quen với động từ be, đại từ và câu đơn.","Get familiar with the verb be, pronouns and simple sentences.","Familiarisez-vous avec le verbe être, les pronoms et les phrases simples.","熟悉动词 be、代词和简单句子。"],
["Chọn một bộ từ về sinh hoạt hằng ngày.","Choose a set of words about daily activities.","Choisissez un ensemble de mots sur les activités quotidiennes.","选择一组有关日常活动的单词。"],
["Chọn bài pre-A1 hoặc A1.","Select lesson pre-A1 or A1.","Sélectionnez la leçon pré-A1 ou A1.","选择 A1 前或 A1 课程。"],
["Ôn thì quá khứ, cách nói về tương lai và câu so sánh.","Review the past tense, how to talk about the future and comparative sentences.","Revoyez le passé, comment parler du futur et les phrases comparatives.","复习过去时，如何谈论将来时和比较句。"],
["Chọn bài A2.","Choose lesson A2.","Choisissez la leçon A2.","选择课程 A2。"],
["Lưu cả cụm từ và câu ví dụ.","Save both phrases and example sentences.","Enregistrez les phrases et les exemples de phrases.","保存短语和例句。"],
["Xem lại câu điều kiện, câu bị động và mệnh đề quan hệ.","Review conditional sentences, passive sentences and relative clauses.","Révisez les peines avec sursis, les peines passives et les clauses relatives.","复习条件句、被动句和关系从句。"],
["IELTS: bắt đầu với True / False / Not Given.","IELTS: starts with True / False / Not Given.","IELTS : commence par Vrai / Faux / Non donné.","雅思：以 True / False / Not Give 开头。"],
["Chọn bài B1.","Choose lesson B1.","Choisissez la leçon B1.","选择课程 B1。"],
["Ôn câu điều kiện, động từ khuyết thiếu và cách nối ý.","Review conditional sentences, modal verbs and how to connect ideas.","Révisez les phrases avec sursis, les verbes modaux et comment relier les idées.","复习条件句、情态动词以及如何连接思想。"],
["IELTS: nhận ra cách diễn đạt tương đương và ý chính từng đoạn.","IELTS: recognize equivalent expressions and main ideas in each paragraph.","IELTS : reconnaître les expressions équivalentes et les idées principales dans chaque paragraphe.","雅思：识别每个段落中的等效表达和主要思想。"],
["Học từ theo chủ đề và các từ thường đi cùng nhau (collocations).","Learn words by topic and words that often go together (collocations).","Apprenez des mots par sujet et des mots qui vont souvent ensemble (collocations).","按主题学习单词和经常在一起的单词（搭配）。"],
["Học đảo ngữ, câu nhấn mạnh và cách diễn đạt mức độ chắc chắn.","Learn inversions, emphatic sentences and how to express degrees of certainty.","Apprenez les inversions, les phrases emphatiques et comment exprimer les degrés de certitude.","学习倒装句、强调句以及如何表达确定程度。"],
["Đối chiếu định nghĩa, ví dụ và các từ thường đi cùng nhau.","Compare definitions, examples, and words that often go together.","Comparez les définitions, les exemples et les mots qui vont souvent ensemble.","比较经常一起使用的定义、示例和单词。"],
["Góc của bạn", "Your space", "Votre espace", "我的空间"],
["Tài khoản và dữ liệu học, gọn trong một chỗ.", "Your account and learning data, in one place.", "Votre compte et vos données, au même endroit.", "账户与学习数据，一处管理。"],
["TÀI KHOẢN", "YOUR ACCOUNT", "VOTRE COMPTE", "账户"],
["Học theo nhịp của riêng bạn.", "Learn at your own pace.", "Apprenez à votre rythme.", "按自己的节奏学习。"],
["Đổi mật khẩu →", "Change password →", "Changer le mot de passe →", "修改密码 →"],
["Khám phá cách học →", "Explore study tips →", "Découvrir les méthodes →", "探索学习方法 →"],
["Giữ lại hành trình học", "Keep your learning journey", "Gardez votre parcours", "保存学习记录"],
["Tải bài đọc, kho từ và tiến độ của bạn.", "Download your readings, vocabulary and progress.", "Téléchargez vos lectures, votre vocabulaire et vos progrès.", "下载文章、词库和学习进度。"],
["Tải bản sao dữ liệu", "Download a backup", "Télécharger une sauvegarde", "下载备份"],
["Xuất danh sách từ", "Export vocabulary", "Exporter le vocabulaire", "导出单词"],
["Khôi phục từ bản sao", "Restore a backup", "Restaurer une sauvegarde", "从备份恢复"],
["Gộp dữ liệu vào kho hiện có, giữ nguyên tiến độ.", "Add to your library while keeping your progress.", "Ajoutez vos données sans perdre vos progrès.", "合并至现有词库，保留学习进度。"],
["Chọn file để khôi phục", "Choose a backup file", "Choisir une sauvegarde", "选择备份文件"],
["JSON hoặc CSV · Tối đa 8 MB", "JSON or CSV · Up to 8 MB", "JSON ou CSV · 8 Mo maximum", "JSON 或 CSV · 最大 8 MB"],
["Khôi phục dữ liệu", "Restore data", "Restaurer les données", "恢复数据"],
["Quyền riêng tư & dữ liệu", "Privacy & data", "Confidentialité et données", "隐私与数据"],
["Kho từ và bài đọc riêng chỉ hiển thị trong tài khoản của bạn.", "Your personal words and readings are private to your account.", "Vos mots et lectures personnels restent privés dans votre compte.", "私人词库和文章仅在你的账户中显示。"],
["Bản sao không chứa mật khẩu. Hãy giữ riêng nếu có nội dung cá nhân.", "Backups exclude passwords. Keep them private if they contain personal content.", "Les sauvegardes ne contiennent pas de mot de passe. Gardez-les privées si elles contiennent des données personnelles.", "备份不含密码。若含个人内容，请妥善保管。"],
["Trợ lý chỉ nhận nội dung bạn đồng ý gửi. Bạn có thể sửa lại gợi ý trong kho từ.", "The assistant only receives content you agree to send. You can edit its suggestions in your vocabulary.", "L’assistant ne reçoit que le contenu que vous acceptez d’envoyer. Vous pouvez modifier ses suggestions dans votre vocabulaire.", "助手只接收你同意发送的内容。你可以在词库中修改建议。"],
["DÀNH CHO BẠN", "FOR YOU", "POUR VOUS", "为你推荐"],
["Xem thêm gợi ý", "More study tips", "Plus de conseils", "更多学习建议"],
['Tổng quan','Overview','Vue d’ensemble','概览'],['Thư viện luyện đọc','Reading library','Bibliothèque de lecture','阅读库'],['Luyện IELTS Reading','IELTS Reading practice','Entraînement IELTS Reading','雅思阅读练习'],['Luyện TOEIC Reading','TOEIC Reading practice','Entraînement TOEIC Reading','TOEIC 阅读练习'],['Bài đọc của tôi','My readings','Mes lectures','我的文章'],['Kho từ của tôi','My vocabulary','Mon vocabulaire','我的词库'],['Luyện nhớ từ','Vocabulary practice','Réviser le vocabulaire','词汇练习'],['Thống kê truy cập','Visit statistics','Statistiques de visites','访问统计'],['Cài đặt & dữ liệu','Settings & data','Réglages et données','设置与数据'],['KHÔNG GIAN HỌC','LEARNING SPACE','ESPACE D’APPRENTISSAGE','学习空间'],['Đăng xuất','Sign out','Déconnexion','退出登录'],['Đóng','Close','Fermer','关闭'],['Hủy','Cancel','Annuler','取消'],['Lưu','Save','Enregistrer','保存'],['Xóa','Delete','Supprimer','删除'],['Sửa','Edit','Modifier','编辑'],['Lọc','Filter','Filtrer','筛选'],['Tìm kiếm','Search','Rechercher','搜索'],['Mỗi ngày, một chút.','A little every day.','Un peu chaque jour.','每天进步一点。'],['Không chỉ sưu tầm từ.','Go beyond collecting words.','Ne collectionnez pas seulement les mots.','不只是收集词汇。'],['Hãy biến chúng thành vốn từ của bạn.','Make them part of your vocabulary.','Faites-en votre vocabulaire.','让它们真正成为你的词汇。'],['Kho riêng · PostgreSQL','Your private collection','Votre collection privée','私人学习库'],['Bản HTML · localStorage','Offline preview · local storage','Aperçu hors ligne · stockage local','离线预览 · 本地存储'],['Đang mở kho học tập…','Opening your learning space…','Ouverture de votre espace…','正在打开学习空间…'],['Đang kết nối…','Connecting…','Connexion…','正在连接…'],['○ Không dùng API','○ Manual learning mode','○ Mode sans API','○ 手动学习模式'],['● AI đã kết nối','● AI connected','● IA connectée','● AI 已连接'],['LexiRead · Từ của bạn. Ngữ cảnh của bạn. Nhịp học của bạn.','LexiRead · Your words. Your context. Your pace.','LexiRead · Vos mots. Votre contexte. Votre rythme.','LexiRead · 你的词汇，你的语境，你的节奏。'],
['Mọi trình độ','All levels','Tous les niveaux','所有级别'],['Mọi chủ đề','All topics','Tous les thèmes','所有主题'],['Mọi trạng thái','All statuses','Tous les états','所有状态'],['Tất cả bài','All readings','Toutes les lectures','所有文章'],['Chỉ yêu thích','Favourites only','Favoris uniquement','仅收藏'],['Chưa yêu thích','Not favourited','Non favoris','未收藏'],['Chưa đọc','Not started','Non commencé','未开始'],['Đang đọc','In progress','En cours','阅读中'],['Đã đọc','Completed','Terminé','已读'],['Bắt đầu','Start','Commencer','开始'],['Đọc tiếp','Continue reading','Continuer','继续阅读'],['Mở bài →','Open reading →','Ouvrir →','打开文章 →'],['Bản dịch & giải thích có sẵn','Translation & explanations included','Traduction et explications incluses','附翻译与解析'],['ước lượng','estimated','estimé','估计'],['Tìm tiêu đề hoặc chủ đề…','Search titles or topics…','Rechercher un titre ou un thème…','搜索标题或主题…'],['Tìm bài đọc','Search readings','Chercher une lecture','搜索文章'],['Trình độ','Level','Niveau','级别'],['Chủ đề','Topic','Thème','主题'],['Tiến độ đọc','Reading progress','Progression de lecture','阅读进度'],['Bài yêu thích','Favourite readings','Lectures favorites','收藏文章'],['Đọc để hiểu, không cần dịch từng chữ.','Read for meaning, not word by word.','Lisez pour comprendre, sans tout traduire.','理解含义，无需逐字翻译。'],['Thử đọc tiếng Anh trước, làm câu hỏi, rồi mở bản dịch và lưu từ bạn muốn học.','Read in English, answer the questions, then check the translation and save useful words.','Lisez en anglais, répondez aux questions, puis consultez la traduction et enregistrez des mots.','先读英语并答题，再查看翻译，保存想学的词。'],['Chưa có bài phù hợp','No matching readings','Aucune lecture trouvée','暂无匹配文章'],['Thử chủ đề hoặc mức độ khác.','Try another topic or level.','Essayez un autre thème ou niveau.','请尝试其他主题或级别。'],['A1–C1: mức độ do người biên soạn ước lượng','A1–C1: estimated by the author','A1–C1 : niveaux estimés par l’auteur','A1–C1：由编写者估计的级别'],
['Bài đọc','Reading','Texte','课文'],['Hiểu bài','Comprehension','Compréhension','阅读理解'],['Hỏi đáp & giải thích','Questions & explanations','Questions et explications','问答与解析'],['Hiện bản dịch','Show translation','Afficher la traduction','显示翻译'],['Cỡ chữ','Text size','Taille du texte','字号'],['Sửa bài','Edit reading','Modifier le texte','编辑文章'],['Ôn từ đã lưu từ bài này ↗','Review words from this reading ↗','Réviser les mots de ce texte ↗','复习本文词汇 ↗'],['Đánh dấu đã đọc','Mark as read','Marquer comme lu','标记为已读'],['✓ Đã đọc · bỏ đánh dấu','✓ Read · unmark','✓ Lu · annuler','✓ 已读 · 取消标记'],['☆ Yêu thích','☆ Favourite','☆ Favori','☆ 收藏'],['★ Đã yêu thích','★ Favourited','★ Dans les favoris','★ 已收藏'],['Đọc đến đây','Bookmark here','Marquer cet endroit','标记读到这里'],['Hỏi đoạn này','Ask about this paragraph','Question sur ce paragraphe','询问此段'],['+ Lưu từ / cụm từ','+ Save word / phrase','+ Enregistrer le mot','+ 保存词语'],['Giải thích câu','Explain sentence','Expliquer la phrase','解释句子'],['ENGLISH · VĂN BẢN GỐC','ENGLISH · ORIGINAL TEXT','ANGLAIS · TEXTE ORIGINAL','英语 · 原文'],['TIẾNG VIỆT · BẢN DỊCH THAM KHẢO','VIETNAMESE · REFERENCE TRANSLATION','VIETNAMIEN · TRADUCTION','越南语 · 参考译文'],['Chọn những từ bạn cần học','Choose words to learn','Choisissez les mots à apprendre','选择要学习的词汇'],['Lưu mục đã chọn','Save selected items','Enregistrer la sélection','保存所选项目'],['Chọn tất cả','Select all','Tout sélectionner','全选'],['Hiểu bài trước, đối chiếu sau.','Understand first, check afterwards.','Comprenez, puis vérifiez.','先理解，再核对。'],['Kiểm tra câu trả lời','Check answers','Vérifier les réponses','检查答案'],['Quay lại bài đọc','Back to reading','Retour au texte','返回课文'],['Làm lại bộ câu hỏi','Try the questions again','Refaire les questions','重新答题'],['Câu trả lời đúng','Correct answers','Réponses correctes','正确答案'],['✓ Đúng','✓ Correct','✓ Correct','✓ 正确'],['Chưa đúng','Not quite right','Pas tout à fait','不正确'],
['Kho từ cá nhân','Personal vocabulary','Vocabulaire personnel','个人词库'],['+ Thêm từ','+ Add word','+ Ajouter un mot','+ 添加词汇'],['+ Nhập bài','+ Import reading','+ Importer un texte','+ 导入文章'],['+ Nhập bài của tôi','+ Add my reading','+ Ajouter mon texte','+ 添加我的文章'],['Ôn từ hôm nay ↗','Review today’s words ↗','Réviser aujourd’hui ↗','复习今日词汇 ↗'],['Ôn ngay →','Review now →','Réviser →','立即复习 →'],['KẾ HOẠCH ÔN HÔM NAY','TODAY’S REVIEW PLAN','RÉVISIONS DU JOUR','今日复习计划'],['Không có từ đến hạn.','No words due.','Aucun mot à réviser.','暂无到期词汇。'],['Đã hoàn thành mục tiêu hôm nay.','Today’s goal completed.','Objectif du jour atteint.','今日目标已完成。'],['Bài soạn sẵn','Curated readings','Lectures préparées','精选文章'],['Bài đã đọc','Readings completed','Lectures terminées','已读文章'],['Thẻ trong kho riêng','Vocabulary cards','Cartes de vocabulaire','词汇卡片'],['Từ đang chờ ôn','Words to review','Mots à réviser','待复习词汇'],['Ngày học / 30 ngày','Study days / 30 days','Jours étudiés / 30 jours','近30天学习天数'],['Hoạt động hôm nay','Activity today','Activité du jour','今日活动'],['Lượt TOEIC','TOEIC attempts','Essais TOEIC','TOEIC 练习次数'],['Chọn một điểm bắt đầu','Choose where to start','Choisissez un point de départ','选择起点'],['Xem thư viện →','Browse library →','Voir la bibliothèque →','浏览阅读库 →'],['Khám phá bài đọc →','Explore readings →','Découvrir les lectures →','探索阅读 →'],['BÀI ĐỌC CỦA TÔI','MY READINGS','MES LECTURES','我的文章'],['KHO TỪ CÁ NHÂN','MY VOCABULARY','MON VOCABULAIRE','个人词库'],['Mang bài bạn đang học vào.','Bring your own reading.','Ajoutez votre propre texte.','导入你正在学习的文章。'],['Học một lần, gặp lại đúng lúc.','Learn once, review at the right time.','Apprenez, puis révisez au bon moment.','学一次，在合适的时候复习。'],
['Flashcard · Lật thẻ','Flashcards','Cartes mémoire','闪卡'],['ABCD · Anh → Việt','Multiple choice · English → Vietnamese','QCM · Anglais → Vietnamien','选择题 · 英语 → 越南语'],['ABCD · Việt → Anh','Multiple choice · Vietnamese → English','QCM · Vietnamien → Anglais','选择题 · 越南语 → 英语'],['Chọn synonym','Choose a synonym','Choisir un synonyme','选择近义词'],['Nhận diện paraphrase','Recognise paraphrases','Reconnaître les reformulations','识别同义改写'],['Điền từ trong câu','Fill in the gap','Compléter la phrase','填空'],['Gõ từ tiếng Anh','Type the English word','Saisir le mot anglais','输入英语单词'],['Quên','Again','À revoir','忘记了'],['Khó','Hard','Difficile','困难'],['Nhớ','Good','Bien','记得'],['Dễ','Easy','Facile','简单'],['Tất cả bộ từ','All word sets','Tous les groupes','所有词组'],['Mọi bài nguồn','All source readings','Tous les textes sources','所有来源文章'],['Bắt đầu ôn','Start review','Commencer la révision','开始复习'],['Tiếp tục →','Continue →','Continuer →','继续 →'],['Xuất backup JSON','Export JSON backup','Exporter la sauvegarde JSON','导出 JSON 备份'],['Nhập backup JSON','Import JSON backup','Importer la sauvegarde JSON','导入 JSON 备份'],['Xuất CSV','Export CSV','Exporter CSV','导出 CSV'],['Copy prompt / Dán JSON','Copy prompt / Paste JSON','Copier le prompt / Coller le JSON','复制提示词 / 粘贴 JSON'],['Dịch & gợi ý bằng AI','Translate & suggest with AI','Traduire avec l’IA','AI 翻译与建议'],['Đang xử lý…','Processing…','Traitement…','正在处理…'],['YOUR PERSONAL LEARNING LIBRARY','YOUR PERSONAL LEARNING LIBRARY','VOTRE BIBLIOTHÈQUE PERSONNELLE','个人学习库'],['MY LEARNING SPACE','MY LEARNING SPACE','MON ESPACE D’APPRENTISSAGE','我的学习空间']
];
rows.push(...[
  [
    "auth.identifier",
    "Tên đăng nhập hoặc email",
    "Username or email",
    "Identifiant ou e-mail",
    "用户名或邮箱"
  ],
  [
    "auth.error",
    "Tên đăng nhập/email hoặc mật khẩu chưa đúng.",
    "The username/email or password is incorrect.",
    "L’identifiant/e-mail ou le mot de passe est incorrect.",
    "用户名/邮箱或密码不正确。"
  ],
  [
    "auth.signup",
    "Chưa có tài khoản? Đăng ký miễn phí",
    "New here? Create a free account",
    "Nouveau ? Créez un compte gratuit",
    "还没有账号？免费注册"
  ],
  [
    "auth.forgot",
    "Quên mật khẩu?",
    "Forgot password?",
    "Mot de passe oublié ?",
    "忘记密码？"
  ],
  [
    "auth.backLogin",
    "← Về trang đăng nhập",
    "← Back to sign in",
    "← Retour à la connexion",
    "← 返回登录"
  ],
  [
    "auth.create",
    "Tạo góc học của bạn",
    "Create your learning space",
    "Créez votre espace d’apprentissage",
    "创建你的学习空间"
  ],
  [
    "auth.signupCopy",
    "Chọn tên đăng nhập và mật khẩu. Email chỉ dùng để khôi phục tài khoản khi cần; hãy nhập email bạn sở hữu.",
    "Choose a username and password. Enter an email you own for account recovery.",
    "Choisissez un identifiant et un mot de passe. Utilisez votre propre e-mail pour récupérer le compte.",
    "选择用户名和密码。请填写你自己的邮箱，以便找回账号。"
  ],
  [
    "auth.username",
    "Tên đăng nhập",
    "Username",
    "Identifiant",
    "用户名"
  ],
  [
    "auth.recoveryEmail",
    "Email khôi phục",
    "Recovery email",
    "E-mail de récupération",
    "找回账号邮箱"
  ],
  [
    "auth.confirmPassword",
    "Nhập lại mật khẩu",
    "Confirm password",
    "Confirmez le mot de passe",
    "确认密码"
  ],
  [
    "auth.passwordHint",
    "Ít nhất 10 ký tự, không dùng mật khẩu quá phổ biến hoặc giống tên đăng nhập.",
    "At least 10 characters. Avoid common passwords or your username.",
    "Au moins 10 caractères. Évitez les mots de passe courants ou votre identifiant.",
    "至少 10 个字符。不要使用常见密码或用户名。"
  ],
  [
    "auth.register",
    "Tạo tài khoản miễn phí",
    "Create a free account",
    "Créer un compte gratuit",
    "免费创建账号"
  ],
  [
    "auth.resetCopy",
    "Nhập email đã dùng khi đăng ký. Bạn sẽ nhận được liên kết đặt lại mật khẩu, có hiệu lực trong 1 giờ.",
    "Enter your registration email to request a password reset link, valid for 1 hour.",
    "Saisissez votre e-mail d’inscription pour demander un lien valable 1 heure.",
    "输入注册邮箱以申请密码重置链接，链接有效期为 1 小时。"
  ],
  [
    "auth.sendReset",
    "Gửi liên kết khôi phục",
    "Send reset link",
    "Envoyer le lien",
    "发送重置链接"
  ],
  [
    "auth.mailUnavailable",
    "Tính năng gửi email khôi phục chưa được mở. Vui lòng liên hệ quản trị viên để được hỗ trợ.",
    "Email recovery is not available yet. Please contact the administrator.",
    "La récupération par e-mail n’est pas encore disponible. Contactez l’administrateur.",
    "邮箱找回功能尚未启用，请联系管理员。"
  ],
  [
    "auth.checkEmail",
    "Kiểm tra hộp thư",
    "Check your inbox",
    "Consultez votre boîte mail",
    "查看邮箱"
  ],
  [
    "auth.resetSent",
    "Nếu email khớp một tài khoản đủ điều kiện, hệ thống sẽ gửi liên kết khôi phục. Kiểm tra cả thư rác. Nếu chưa nhận được, chờ vài phút rồi thử lại hoặc liên hệ quản trị viên.",
    "If the email matches an eligible account, a recovery link will be sent. Check spam too. If it does not arrive, wait a few minutes and retry or contact the administrator.",
    "Si l’e-mail correspond à un compte éligible, un lien sera envoyé. Vérifiez les indésirables. Sinon, attendez quelques minutes et réessayez ou contactez l’administrateur.",
    "如果邮箱对应符合条件的账号，系统将发送重置链接。请检查垃圾邮件。若未收到，请稍后重试或联系管理员。"
  ],
  [
    "auth.noShare",
    "Không chia sẻ liên kết này với người khác.",
    "Do not share this link.",
    "Ne partagez pas ce lien.",
    "请勿与他人分享此链接。"
  ],
  [
    "auth.newPassword",
    "Đặt mật khẩu mới",
    "Choose a new password",
    "Choisir un nouveau mot de passe",
    "设置新密码"
  ],
  [
    "auth.savePassword",
    "Lưu mật khẩu mới",
    "Save new password",
    "Enregistrer le mot de passe",
    "保存新密码"
  ],
  [
    "auth.expired",
    "Liên kết không còn hiệu lực",
    "This link is no longer valid",
    "Ce lien n’est plus valide",
    "链接已失效"
  ],
  [
    "auth.expiredCopy",
    "Liên kết có thể đã hết hạn hoặc đã được sử dụng.",
    "The link may have expired or already been used.",
    "Le lien a peut-être expiré ou déjà été utilisé.",
    "链接可能已过期或已使用。"
  ],
  [
    "auth.requestAgain",
    "Yêu cầu liên kết mới",
    "Request a new link",
    "Demander un nouveau lien",
    "申请新链接"
  ],
  [
    "auth.resetComplete",
    "Đã đổi mật khẩu",
    "Password changed",
    "Mot de passe modifié",
    "密码已修改"
  ],
  [
    "auth.resetCompleteCopy",
    "Bạn có thể đăng nhập bằng mật khẩu mới.",
    "You can now sign in with your new password.",
    "Vous pouvez vous connecter avec votre nouveau mot de passe.",
    "现在可以使用新密码登录。"
  ],
  [
    "account.title",
    "Tài khoản của tôi",
    "My account",
    "Mon compte",
    "我的账号"
  ],
  [
    "account.copy",
    "Cập nhật thông tin cá nhân. Bài học, từ vựng và lịch ôn của bạn vẫn được giữ nguyên.",
    "Update your profile. Your lessons, vocabulary and review schedule stay unchanged.",
    "Modifiez votre profil. Vos leçons, votre vocabulaire et vos révisions sont conservés.",
    "更新个人资料。学习内容、词库和复习进度将保留。"
  ],
  [
    "account.save",
    "Lưu thông tin",
    "Save profile",
    "Enregistrer le profil",
    "保存资料"
  ],
  [
    "account.emailHint",
    "Hãy dùng email bạn sở hữu để có thể nhận liên kết khôi phục. Email hiện chưa được xác minh quyền sở hữu.",
    "Use an email you own for recovery. Email ownership has not been verified.",
    "Utilisez votre propre e-mail pour la récupération. Sa propriété n’a pas été vérifiée.",
    "请使用你自己的邮箱找回账号。邮箱所有权尚未验证。"
  ],
  [
    "account.changePassword",
    "Đổi mật khẩu",
    "Change password",
    "Modifier le mot de passe",
    "修改密码"
  ],
  [
    "account.passwordCopy",
    "Nhập mật khẩu hiện tại và chọn mật khẩu mới. Các phiên đăng nhập khác sẽ phải đăng nhập lại.",
    "Enter your current password and choose a new one. Other sessions will need to sign in again.",
    "Saisissez votre mot de passe actuel et choisissez-en un nouveau. Les autres sessions devront se reconnecter.",
    "输入当前密码并设置新密码。其他会话需要重新登录。"
  ],
  [
    "account.passwordDone",
    "Phiên hiện tại được giữ lại. Hãy dùng mật khẩu mới ở những lần đăng nhập tiếp theo.",
    "This session stays signed in. Use the new password next time.",
    "Cette session reste connectée. Utilisez le nouveau mot de passe à l’avenir.",
    "当前会话将保持登录。下次请使用新密码。"
  ],
  [
    "account.back",
    "← Quay lại học",
    "← Back to learning",
    "← Reprendre l’apprentissage",
    "← 返回学习"
  ],
  [
    "hero.caption",
    "Luyện đọc với câu hỏi, lời giải và từ vựng theo ngữ cảnh.",
    "Practise with questions, explanations and vocabulary in context.",
    "Entraînez-vous avec des questions, des explications et du vocabulaire en contexte.",
    "通过问题、解析和语境词汇练习阅读。"
  ],
  [
    "card.englishOnly",
    "Tiếng Anh · chưa có bản dịch",
    "English · no translation yet",
    "Anglais · traduction à venir",
    "英语 · 暂无翻译"
  ]
]);
legacy.push(...rows.slice(-35).map(row=>row.slice(1)));
const motivationRows=[
['brand.imageAlt','Bạn thỏ tai lá đang đọc sách trong khu vườn nhỏ của LexiRead','A leaf-eared rabbit reading in LexiRead’s little garden','Un lapin aux oreilles en feuilles lit dans le petit jardin de LexiRead','叶子耳朵的小兔子在 LexiRead 的小花园里读书'],
['brand.gardenNote','Chậm một chút. Nhớ lâu hơn.','Take your time. Make it stick.','Prenez votre temps. Retenez davantage.','慢慢读，记得更牢。'],
['brand.welcome','Góc nhỏ của bạn. Mỗi ngày một điều mới.','Your little corner. A new discovery every day.','Votre petit coin. Une découverte chaque jour.','属于你的小天地，每天发现新事物。'],
['brand.official','Đề mẫu chính thức','Official samples','Exemples officiels','官方样题'],
['brand.officialLink','Khám phá đề mẫu chính thức ↗','Explore official samples ↗','Découvrir les exemples officiels ↗','探索官方样题 ↗'],
['nav.menu','Menu học','Study menu','Menu d’étude','学习菜单'],
['level.choose','Chọn trình độ đọc','Choose your reading level','Choisissez votre niveau','选择阅读级别'],
['level.note','Chọn mức bạn thấy vừa sức. Bạn có thể đổi bất cứ lúc nào.','Choose a comfortable level. You can change it any time.','Choisissez un niveau adapté. Vous pouvez le changer à tout moment.','选择适合自己的级别，随时可以更改。'],
['level.label.all','Tất cả trình độ','All levels','Tous les niveaux','全部级别'],
['level.label.pre-A1','Mới bắt đầu','First steps','Premiers pas','入门'],
['level.label.A1','Khởi đầu','Beginner','Débutant','初级'],
['level.label.A2','Nền tảng','Elementary','Élémentaire','基础'],
['level.label.B1','Trung cấp','Intermediate','Intermédiaire','中级'],
['level.label.B2','Khá','Upper intermediate','Intermédiaire +','中高级'],
['level.label.C1','Nâng cao','Advanced','Avancé','高级'],
['level.label.C2','Thành thạo','Proficient','Maîtrise','精通'],
['streak.eyebrow','MỖI NGÀY MỘT CHÚT','A LITTLE EVERY DAY','UN PEU CHAQUE JOUR','每天进步一点'],
['streak.count','{count} ngày liên tiếp','{count} consecutive days','{count} jours de suite','连续学习 {count} 天'],
['streak.done','Hôm nay đã học rồi. Một bước nhỏ đáng ghi nhận!','You studied today. A small step worth celebrating!','Vous avez étudié aujourd’hui. Un petit pas qui compte !','今天已经学习了，每一小步都值得肯定！'],
['streak.keep','Thêm một chút hôm nay để nối dài nhịp học nhé.','A little practice today keeps your rhythm going.','Un peu de pratique aujourd’hui pour garder le rythme.','今天再学一点，延续学习节奏。'],
['streak.start','Bắt đầu từ một bài đọc nhỏ hôm nay nhé.','Start with a short reading today.','Commencez par une petite lecture aujourd’hui.','今天从一篇短文开始吧。'],
['streak.today','Hôm nay','Today','Aujourd’hui','今天'],
['streak.studied','Đã học','Studied','Étudié','已学习'],
['streak.noActivity','Chưa ghi nhận học','No study recorded','Aucune étude enregistrée','暂无学习记录'],
['streak.week','Hoạt động học 7 ngày gần nhất','Learning over the last 7 days','Apprentissage des 7 derniers jours','最近七天学习记录'],
['streak.rule','Ôn một thẻ, hoàn thành bài đọc hoặc nộp bài tập để ghi nhận ngày học. Tính ngày theo giờ Việt Nam.','Review a card, finish a reading or submit an exercise to record a study day. Dates use Vietnam time.','Révisez une carte, terminez une lecture ou rendez un exercice pour valider la journée. Heure du Vietnam.','复习一张卡片、完成阅读或提交练习即可记录学习日。按越南时间计算。'],
['streak.best','Dài nhất: {count} ngày','Longest: {count} days','Record : {count} jours','最长连续：{count} 天'],
['streak.target','Cột mốc tiếp: {count} ngày','Next milestone: {count} days','Prochaine étape : {count} jours','下个目标：{count} 天'],
['streak.milestone','Tiến độ đến cột mốc chuỗi học','Progress to next streak milestone','Progression vers la prochaine étape','连续学习目标进度'],
['streak.daily','Mục tiêu ôn từ hôm nay','Today’s vocabulary review goal','Objectif de révision du jour','今日词汇复习目标'],
['streak.goalNote','Không cần đủ mục tiêu ôn để giữ chuỗi học.','You don’t need the full review goal to keep your streak.','Pas besoin d’atteindre cet objectif pour garder la série.','保持连续学习无需完成全部复习目标。'],
['streak.goalDone','Đã đạt mục tiêu hôm nay. Bạn có thể nghỉ ngơi rồi!','Today’s goal is complete. Take a well-earned break!','Objectif atteint. Vous pouvez faire une pause !','今天的目标完成了，可以休息一下啦！'],
['streak.review','Ôn một chút →','Review a little →','Réviser un peu →','复习一下 →'],
['streak.read','Đọc một bài →','Read a story →','Lire un texte →','读一篇文章 →'],
];
rows.push(...motivationRows);legacy.push(...motivationRows.map(row=>row.slice(1)));
legacy.push(...[["Nhập bộ từ cá nhân", "Import a vocabulary deck", "Importer une liste de mots", "导入个人词汇集"], ["Thêm cả bộ từ, xem trước rồi lưu để ôn mỗi ngày.", "Add a deck, preview it, and save it for daily practice.", "Ajoutez une liste, vérifiez-la puis enregistrez-la pour réviser chaque jour.", "添加词汇集，预览后保存，便于每日复习。"], ["Thêm bộ từ của bạn", "Add your vocabulary deck", "Ajouter votre liste de mots", "添加你的词汇集"], ["Chọn file bộ từ", "Choose a vocabulary file", "Choisir un fichier de vocabulaire", "选择词汇文件"], ["JSON · Tối đa 2 MB · 500 từ", "JSON · Up to 2 MB · 500 words", "JSON · 2 Mo maximum · 500 mots", "JSON · 最多 2 MB · 500 个词"], ["Tạo bộ từ với AI", "Create a deck with AI", "Créer une liste avec l’IA", "用 AI 创建词汇集"], ["Chọn chủ đề, sao chép prompt rồi dán vào AI bạn đang dùng. Mang file kết quả về đây để học.", "Choose a topic, copy the prompt into your AI tool, then import the result here.", "Choisissez un sujet, copiez le prompt dans votre outil IA, puis importez le résultat ici.", "选择主题，将提示词复制到你使用的 AI 工具中，再将结果导入这里。"], ["Bắt đầu từ bộ có sẵn", "Start with an existing deck", "Commencer avec une liste existante", "从现有词汇集开始"], ["Khám phá bộ từ theo chủ đề, lưu từ bạn cần rồi luyện bằng flashcard.", "Explore topic decks, save useful words, and practise with flashcards.", "Explorez les listes par thème, enregistrez les mots utiles puis révisez avec des cartes.", "探索主题词汇集，保存需要的词，并用闪卡练习。"], ["Khám phá bộ từ →", "Explore vocabulary decks →", "Explorer les listes de mots →", "探索词汇集 →"], ["Khám phá bộ luyện Reading →", "Explore reading practice sets →", "Explorer les séries de lecture →", "探索阅读练习集 →"], ["Bộ luyện Reading", "Reading practice sets", "Séries de lecture", "阅读练习集"], ["Chọn một bộ và luyện từng phần. Các bài luyện do LexiRead biên soạn.", "Choose a set and practise each section. These exercises are authored by LexiRead.", "Choisissez une série et travaillez chaque partie. Ces exercices sont rédigés par LexiRead.", "选择一套练习，按部分学习。练习内容由 LexiRead 编写。"], ["Loại nội dung", "Content type", "Type de contenu", "内容类型"], ["Đề Reading theo từng phần", "Reading tests by section", "Tests de lecture par partie", "分部分阅读测试"], ["Bộ luyện ngắn", "Short practice sets", "Séries courtes", "短篇练习集"], ["Tài liệu đọc thêm", "Further reading resources", "Ressources de lecture supplémentaires", "补充阅读资料"], ["Tìm bộ luyện", "Find practice sets", "Rechercher une série", "查找练习集"], ["Tìm theo tên…", "Search by title…", "Rechercher par titre…", "按标题搜索…"], ["Chưa có kết quả phù hợp.", "No matching results.", "Aucun résultat correspondant.", "暂无匹配结果。"]]);
legacy.push(['Chọn file JSON','Choose a JSON file','Choisir un fichier JSON','选择 JSON 文件']);
legacy.push(['Bản HTML chỉ tra các từ đã có trong bài. Mở bản web để tra thêm nghĩa.','The HTML preview only looks up words in the current reading. Open the web app for more definitions.','L’aperçu HTML ne recherche que les mots du texte actuel. Ouvrez le site pour consulter davantage de définitions.','HTML 预览仅查询当前文章中的词语。请打开网站查看其他释义。']);
legacy.push(
['Luyện đề TOEIC','TOEIC practice tests','Entraînement au TOEIC','TOEIC 模拟练习'],
['Chọn đề, làm bài và xem lời giải.','Choose a test, practise and review the answers.','Choisissez un test, entraînez-vous et consultez les corrigés.','选择练习，答题并查看解析。'],
['Cách làm bài →','Test tips →','Conseils pour le test →','答题方法 →'],
['Tìm đề theo tên…','Search tests by title…','Rechercher un test par titre…','按名称查找练习…'],
['Khác','Other','Autres','其他']);
const dictionaries=Object.fromEntries(languages.map((l,i)=>[l,Object.fromEntries(rows.map(r=>[r[0],r[i+1]]))]));
const normalize=value=>value.replace(/\s+/g,' ').trim();
// Authored, local catalogs. No translation service is called in the browser.
const sourceMap=new Map((window.LEXI_INTERFACE_LOCALES||[]).map(r=>[normalize(r[0]),r]));
legacy.forEach(r=>sourceMap.set(normalize(r[0]),r));
const patterns=[...sourceMap.values()].filter(r=>/\{\d+\}/.test(r[0])).map(row=>{
  const keys=[];
  const pattern=normalize(row[0]).split(/(\{\d+\})/).map(part=>{
    if(/^\{\d+\}$/.test(part)){keys.push(part);return '([\\s\\S]{1,200})';}
    return part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  }).join('');
  return {row,keys,re:new RegExp('^'+pattern+'$')};
}).sort((a,b)=>b.row[0].length-a.row[0].length);
let current='vi';try{const saved=localStorage.getItem('lexiread.language');if(languages.includes(saved))current=saved;}catch{}
const originals=new WeakMap(),attributeSources=new WeakMap();
const protectedSelector='script,style,code,pre,textarea,[data-language],[contenteditable]:not([contenteditable="false"]),[data-no-i18n],[lang="en"]:not(html),.reader-en,.reader-vi,.quote,.candidate-body,.question-prompt,.toeic-passage,.toeic-document,.toeic-set-list strong,.qa-answer,.flashcard .word,.flashcard .meaning,.reading-option>span:last-child';
const attributeProtectedSelector=protectedSelector.replace(',textarea','');
function t(key,vars={}){return (dictionaries[current][key]||dictionaries.vi[key]||key).replace(/\{(\w+)\}/g,(m,k)=>Object.hasOwn(vars,k)?String(vars[k]):m);}
function translate(source){
  if(current==='vi')return source;const trimmed=normalize(source),entry=sourceMap.get(trimmed);if(entry)return source.replace(source.trim(),entry[languages.indexOf(current)]);
  const decorated=trimmed.match(/^([←→↗✓★☆◐◉◇✦↺◎◫▤↥⚙·•]\s*)?(.+?)(\s*[←→↗])?$/);
  if(decorated&&(decorated[1]||decorated[3])){const core=sourceMap.get(decorated[2]);if(core)return source.replace(source.trim(),(decorated[1]||'')+core[languages.indexOf(current)]+(decorated[3]||''));}
  for(const {row,keys,re} of patterns){const match=trimmed.match(re);if(match){const vars=Object.fromEntries(keys.map((key,i)=>[key,match[i+1]]));return source.replace(source.trim(),row[languages.indexOf(current)].replace(/\{\d+\}/g,key=>vars[key]??key));}}
  const count=trimmed.match(/^(\d+) bài phù hợp$/);if(count)return t('library.count',{count:count[1]});
  return source;
}
let observer,scheduled=false;
function apply(){
  observer?.disconnect();document.documentElement.lang=current==='zh'?'zh-Hans':current;
  document.querySelectorAll('[data-language]').forEach(s=>{s.value=current;s.setAttribute('aria-label',({vi:'Ngôn ngữ giao diện',en:'Interface language',fr:'Langue de l’interface',zh:'界面语言'})[current]);});
  document.querySelectorAll('[data-i18n]').forEach(el=>{if(el.closest(protectedSelector)||el.children.length)return;const value=t(el.getAttribute('data-i18n'));if(el.textContent!==value)el.textContent=value;});
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{if(!el.closest(attributeProtectedSelector))el.setAttribute('placeholder',t(el.getAttribute('data-i18n-placeholder')));});
  document.querySelectorAll('[data-i18n-alt]').forEach(el=>{if(!el.closest(attributeProtectedSelector))el.setAttribute('alt',t(el.getAttribute('data-i18n-alt')));});
  // Only known interface strings are replaced; originals allow a lossless switch back.
  const walker=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){
    const node=walker.currentNode,parent=node.parentElement;if(!parent||parent.closest(protectedSelector)||(parent.matches('[data-i18n]')&&!parent.children.length))continue;
    let record=originals.get(node);if(!record||node.nodeValue!==record.last)record={source:node.nodeValue,last:node.nodeValue};
    const next=translate(record.source);if(next!==node.nodeValue){if(parent.tagName==='OPTION'&&!parent.hasAttribute('value'))parent.value=record.source;node.nodeValue=next;}record.last=next;originals.set(node,record);
  }
  document.querySelectorAll('[placeholder],[aria-label],[title],[alt]').forEach(el=>{if(el.closest(attributeProtectedSelector)||el.matches('[data-language]'))return;let sources=attributeSources.get(el)||{};for(const attr of ['placeholder','aria-label','title','alt']){if(!el.hasAttribute(attr)||el.hasAttribute('data-i18n-'+attr))continue;const value=el.getAttribute(attr);let old=sources[attr];if(!old||old.last!==value)old={source:value};const next=translate(old.source);if(next!==value)el.setAttribute(attr,next);sources[attr]={source:old.source,last:next};}attributeSources.set(el,sources);});
  observer?.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['data-i18n','placeholder','aria-label','title','alt']});
}
function setLanguage(lang){if(!languages.includes(lang))return;current=lang;try{localStorage.setItem('lexiread.language',lang);}catch{}apply();document.dispatchEvent(new CustomEvent('lexiread:language',{detail:lang}));}
window.LexiI18n={t,translate,apply,setLanguage,get language(){return current;},languages};
document.addEventListener('DOMContentLoaded',()=>{observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;apply();});});apply();document.addEventListener('change',e=>{if(e.target.matches('[data-language]'))setLanguage(e.target.value);});});
window.addEventListener('storage',e=>{if(e.key==='lexiread.language'&&languages.includes(e.newValue)){current=e.newValue;apply();document.dispatchEvent(new CustomEvent('lexiread:language',{detail:current}));}});
})();
