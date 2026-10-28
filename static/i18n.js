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
["hero.practice", "IELTS & TOEIC", "IELTS & TOEIC", "IELTS & TOEIC", "IELTS & TOEIC"],
['hero.caption','Có bản dịch, câu hỏi và lời giải trong từng bài.','Translations, questions and explanations in every lesson.','Traductions, questions et explications dans chaque leçon.','每篇文章均配有翻译、问题和解析。'],
['demo.label','MỘT TRANG SÁCH, MỘT ĐIỀU MỚI','A NEW PAGE, A NEW DISCOVERY','UNE PAGE, UNE DÉCOUVERTE','读一页，发现新知'],
['demo.meaning','tò mò, muốn tìm hiểu','wanting to know or learn more','curieux, qui souhaite en savoir plus','好奇的，想了解更多的'],
['demo.save','+ Thử lưu từ','+ Try saving','+ Essayer','+ 试着保存'],
['demo.saved','✓ Đã thử lưu','✓ Tried it','✓ Essayé','✓ 已体验'],
['demo.caption','Thử một thao tác nhỏ trong hành trình học.','Try one small step in your learning journey.','Essayez un premier geste pour apprendre.','体验学习过程中的一小步。'],
['demo.done','Đây là bản minh họa. Đăng nhập để lưu vào kho từ của bạn.','This is a demo. Sign in to save words to your vocabulary.','Ceci est une démo. Connectez-vous pour enregistrer vos mots.','这是演示。登录后即可保存到你的词库。'],
['stats.readings','bài đọc theo trình độ','graded reading lessons','lectures par niveau','分级阅读文章'],
['stats.levels','từ cơ bản đến nâng cao','from beginner to advanced','du débutant à avancé','从入门到高级'],
["stats.ielts", "bài IELTS Reading", "IELTS Reading lessons", "lectures IELTS Reading", "篇 IELTS Reading 文章"],
["stats.toeic", "bài TOEIC Reading", "TOEIC Reading sets", "séries TOEIC Reading", "套 TOEIC Reading 练习"],
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
['practice.eyebrow','MỘT MỤC TIÊU. MỘT BƯỚC TIẾN.','ONE GOAL. ONE STEP FORWARD.','UN OBJECTIF. UN PAS EN AVANT.','一个目标，一步进展'],["practice.title", "IELTS & TOEIC Reading", "IELTS & TOEIC Reading", "IELTS & TOEIC Reading", "IELTS & TOEIC Reading"],
['ielts.chip','Đọc học thuật · B1–C1','Academic reading · B1–C1','Lecture académique · B1–C1','学术阅读 · B1–C1'],
["ielts.copy", "Các dạng câu hỏi Reading, kèm lời giải.", "Reading question types with explanations.", "Les types de questions de lecture, avec explications.", "阅读题型及答案解析。"],
["ielts.start", "Xem bài →", "View lessons →", "Voir les leçons →", "查看文章 →"],
['ielts.note','Bài luyện kỹ năng tự biên soạn, không phải đề thi chính thức hay bài thi thử đầy đủ; không quy đổi band.','Original skill exercises, not official papers or full mock tests. Scores are not converted to IELTS bands.','Exercices originaux, ni sujets officiels ni examens blancs complets. Les scores ne sont pas convertis en bandes IELTS.','原创技能练习，非官方试题或完整模拟考试，分数不换算为雅思等级。'],
['toeic.chip','Tiếng Anh trong công việc','English for the workplace','L’anglais au travail','职场英语'],
["toeic.copy", "Part 5, 6 và 7, kèm lời giải.", "Parts 5, 6 and 7 with explanations.", "Parties 5, 6 et 7, avec explications.", "Part 5、6、7，附答案解析。"],
["toeic.start", "Xem bài →", "View tests →", "Voir les exercices →", "查看练习 →"],['toeic.note','Nội dung tự biên soạn, không phải đề ETS chính thức.','Original practice content, not official ETS test material.','Contenu original, non issu des tests officiels ETS.','原创练习内容，非 ETS 官方试题。'],['preview','Xem các bài','Browse exercises','Voir les exercices','浏览练习'],
['method.eyebrow','ÍT MỖI NGÀY. NHỚ LÂU HƠN.','A LITTLE EACH DAY. REMEMBER MORE.','UN PEU CHAQUE JOUR. RETENEZ PLUS.','每天一点，记得更久'],['method.title','Biến điều vừa đọc thành điều bạn nhớ.','Turn what you read into what you remember.','Retenez ce que vous venez de lire.','让读过的内容成为记住的知识。'],
['method.read','Đọc theo nhịp của bạn','Read at your own pace','Lisez à votre rythme','按自己的节奏阅读'],['method.readCopy','Đọc tiếng Anh trước, mở bản dịch khi cần. Từng đoạn ngắn giúp bạn không bị ngợp.','Read in English first and reveal the translation when needed. Short paragraphs keep it manageable.','Lisez d’abord en anglais et affichez la traduction si besoin. Avancez paragraphe par paragraphe.','先读英语，需要时再查看翻译。短段落让阅读更轻松。'],
['method.save','Giữ lại từ có ý nghĩa','Keep the words that matter','Gardez les mots utiles','留下有意义的词汇'],['method.saveCopy','Bôi đen từ ngay trong bài để lưu cả nghĩa lẫn ngữ cảnh. Không cần chép sang một ứng dụng khác.','Select a word in the text to save its meaning and context. No need to copy it into another app.','Sélectionnez un mot pour garder son sens et son contexte. Inutile de le recopier ailleurs.','在文章中选中词汇，保存含义和语境，无需复制到其他应用。'],
['method.review','Gặp lại trước khi quên','Meet them again before you forget','Révisez avant d’oublier','在遗忘前再次相遇'],['method.reviewCopy','Ôn bằng flashcard và bài tập. Lịch ôn thay đổi theo mức ghi nhớ của chính bạn.','Review with flashcards and exercises. Your schedule adapts to how well you remember.','Révisez avec des cartes et des exercices. Le calendrier s’adapte à votre mémorisation.','通过闪卡和练习复习，复习计划会根据你的记忆情况调整。'],
['cta.eyebrow','BÀI ĐỌC TIẾP THEO ĐANG CHỜ','YOUR NEXT READ IS WAITING','VOTRE PROCHAINE LECTURE VOUS ATTEND','下一篇阅读正等着你'],['cta.title','Bắt đầu từ một trang, hôm nay.','Start with one page, today.','Commencez par une page, aujourd’hui.','今天，从一页开始。'],['cta.copy','Đăng nhập để giữ bài đã đọc, từ đã lưu và những bước tiến nhỏ của bạn.','Sign in to keep your readings, saved words and small steps forward.','Connectez-vous pour conserver vos lectures, vos mots et vos progrès.','登录以保存已读文章、词汇和点滴进步。'],['cta.start','Vào không gian học ↗','Enter your learning space ↗','Accéder à mon espace ↗','进入学习空间 ↗'],
['footer','Đọc. Khám phá. Ghi nhớ.','Read. Discover. Remember.','Lire. Découvrir. Retenir.','阅读。探索。记忆。'],['footer.link','Tìm câu chuyện tiếp theo ↑','Find your next story ↑','Trouver la prochaine histoire ↑','寻找下一个故事 ↑'],
['auth.eyebrow','MỖI LẦN TRỞ LẠI, MỘT BƯỚC XA HƠN','EVERY RETURN IS A STEP FORWARD','CHAQUE RETOUR EST UN PAS EN AVANT','每次回来，都更进一步'],['auth.storyTitle','Thế giới rộng hơn qua từng trang đọc.','A bigger world, one page at a time.','Un monde plus grand, page après page.','每读一页，世界就更宽广。'],['auth.storyCopy','Một câu chuyện mới, vài từ đáng nhớ. Không gian học của bạn luôn sẵn sàng khi bạn trở lại.','A new story, a few words worth keeping. Your learning space is ready whenever you return.','Une nouvelle histoire, quelques mots à retenir. Votre espace vous attend à chaque retour.','一个新故事，几个值得记住的词。你的学习空间随时等你回来。'],
['auth.welcome','CHÀO MỪNG BẠN TRỞ LẠI','WELCOME BACK','BON RETOUR','欢迎回来'],['auth.title','Tiếp tục hành trình của bạn.','Pick up where you left off.','Reprenez votre parcours.','继续你的学习之旅。'],['auth.copy','Đăng nhập để mở bài đọc, kho từ và lịch ôn dành riêng cho bạn.','Sign in to your readings, vocabulary and personal review schedule.','Connectez-vous à vos lectures, votre vocabulaire et vos révisions.','登录查看你的文章、词库和个人复习计划。'],['auth.email','Địa chỉ email','Email address','Adresse e-mail','电子邮箱'],['auth.password','Mật khẩu','Password','Mot de passe','密码'],['auth.show','Hiện','Show','Voir','显示'],['auth.hide','Ẩn','Hide','Masquer','隐藏'],['auth.submit','Đăng nhập và bắt đầu học →','Sign in and start learning →','Se connecter et apprendre →','登录并开始学习 →'],
['auth.noAccount','Bạn chưa có tài khoản hoặc quên mật khẩu?','Need an account or a password reset?','Besoin d’un compte ou d’un nouveau mot de passe ?','需要账号或重置密码？'],['auth.contact','Liên hệ người đã giới thiệu Lexivela cho bạn để được cấp tài khoản hoặc hỗ trợ đặt lại mật khẩu.','Contact the person who introduced you to Lexivela for an account or help resetting your password.','Contactez la personne qui vous a présenté Lexivela pour obtenir un compte ou réinitialiser votre mot de passe.','请联系向你介绍 Lexivela 的人，获取账号或密码重置帮助。'],['auth.back','← Quay lại khám phá thư viện','← Back to the library','← Retour à la bibliothèque','← 返回阅读库'],['auth.error','Email hoặc mật khẩu chưa đúng. Hãy kiểm tra và thử lại nhé.','The email or password is incorrect. Please check and try again.','L’e-mail ou le mot de passe est incorrect. Vérifiez et réessayez.','邮箱或密码不正确，请检查后重试。'],['auth.throttled','Bạn đã thử đăng nhập quá nhiều lần. Vui lòng thử lại sau 15 phút.','Too many sign-in attempts. Please try again in 15 minutes.','Trop de tentatives. Réessayez dans 15 minutes.','登录尝试过多，请在 15 分钟后重试。'],
['app.contentLanguage','Ngôn ngữ giao diện thay đổi; bài học tiếng Anh và giải thích tiếng Việt được giữ nguyên.','The interface language changes; English lessons and Vietnamese explanations stay unchanged.','La langue de l’interface change ; les leçons en anglais et les explications en vietnamien sont conservées.','仅切换界面语言；英语课文和越南语解析保持不变。'],
["app.ieltsTitle", "IELTS Reading", "IELTS Reading", "IELTS Reading", "IELTS Reading"],['app.ieltsLead','Đọc có chiến lược. Trả lời có bằng chứng.','Read strategically. Answer with evidence.','Lisez avec méthode. Répondez avec des preuves.','有策略地阅读，有依据地作答。'],['app.ieltsSkills','Bắt đầu với một bài, đọc kỹ và đối chiếu lời giải. Tiến độ và từ vựng được lưu cùng tài khoản học của bạn.','Start with one passage, read closely and review the explanations. Progress and vocabulary stay in your learning account.','Commencez par un texte et étudiez les explications. Vos progrès et votre vocabulaire sont conservés dans votre compte.','从一篇文章开始，仔细阅读并核对解析。进度和词汇会保存在你的学习账号中。'],
];
// Existing screens use Vietnamese source labels. Exact matches avoid changing learning content.
const legacy=[
['mục','items','éléments','项'],
['← Về bài học','← Back to lesson','← Retour à la leçon','← 返回课程'],
['Tra bằng từ gốc, như','Search with a base form, such as','Cherchez une forme de base, comme','使用原形查询，例如'],
['Mở bài học rồi chọn “Lưu bộ & ôn thẻ” để bắt đầu.','Open a lesson and choose “Save set & study cards” to start.','Ouvrez une leçon puis choisissez « Enregistrer et réviser ».','打开课程，选择“保存词集并复习”即可开始。'],
['ColloCaid Sample Data · Frankenberg-Garcia, Rees, Lew, Roberts & Butcher. Chỉ gồm phần mẫu được công bố.','ColloCaid Sample Data · Frankenberg-Garcia, Rees, Lew, Roberts & Butcher. Includes the published sample only.','ColloCaid Sample Data · Frankenberg-Garcia, Rees, Lew, Roberts & Butcher. Échantillon publié uniquement.','ColloCaid 样本数据 · Frankenberg-Garcia、Rees、Lew、Roberts 与 Butcher。仅包含已公开的样本。'],
['Open English WordNet 2025 · Open English WordNet Team, phát triển từ Princeton WordNet. Các dạng từ liên quan được nối theo từng nghĩa, không phải từ đồng nghĩa hay một họ từ đầy đủ.','Open English WordNet 2025 · Open English WordNet Team, based on Princeton WordNet. Forms are linked by individual senses; they are not synonyms or complete word families.','Open English WordNet 2025 · Open English WordNet Team, issu de Princeton WordNet. Les formes sont liées par sens ; ce ne sont ni des synonymes ni des familles complètes.','Open English WordNet 2025 · Open English WordNet 团队，基于 Princeton WordNet。词形按具体词义关联，并非同义词或完整词族。'],
['Học từ đi cùng nhau. Chọn đúng dạng từ trong câu.','Learn words together. Choose the right form in context.','Apprenez les mots ensemble. Choisissez la bonne forme en contexte.','学习词语搭配，在句中选择正确词形。'],
['Tìm từ hoặc cụm','Find a word or phrase','Chercher un mot ou une expression','查找单词或短语'],
['Cách kết hợp','Word combination','Association de mots','搭配类型'],
['Kiểu bài học','Lesson type','Type de leçon','课程类型'],
['Chế độ học','Study mode','Mode d’apprentissage','学习模式'],
['Học qua ví dụ','Learn with examples','Apprendre par les exemples','通过例句学习'],
['Bài tập','Exercises','Exercices','练习'],
['Lưu bộ & ôn thẻ →','Save set & study cards →','Enregistrer et réviser →','保存词集并复习 →'],
['Nghĩa câu & cách dùng','Sentence meaning & usage','Sens de la phrase et emploi','句意与用法'],
['Tra thêm collocations & dạng từ','Explore more collocations & word forms','Explorer les collocations et les formes','探索更多搭配与词形'],
['Nguồn bài học','Lesson sources','Sources de la leçon','课程来源'],
['Nguồn dữ liệu','Data sources','Sources des données','数据来源'],
['Chưa tìm thấy bài phù hợp. Thử từ khóa hoặc trình độ khác.','No matching lessons. Try a different word or level.','Aucune leçon trouvée. Essayez un autre mot ou niveau.','没有匹配课程，请尝试其他词语或等级。'],
['Chưa có kết quả cho từ này trong nguồn đã nhập. Thử từ gốc hoặc mở Từ điển.','No result in the installed sources. Try the base form or open the dictionary.','Aucun résultat dans les sources disponibles. Essayez la forme de base ou le dictionnaire.','已导入的数据中暂无结果，请尝试原形或打开词典。'],
['Đang lưu bộ từ…','Saving word set…','Enregistrement des mots…','正在保存词集…'],
['Dạng từ liên quan · Xem nghĩa để chọn cách dùng phù hợp.','Related forms · Check the meaning before choosing a form.','Formes liées · Vérifiez le sens avant de choisir.','相关词形 · 请结合词义选择。'],
['Collocations học thuật · ColloCaid','Academic collocations · ColloCaid','Collocations académiques · ColloCaid','学术搭配 · ColloCaid'],
['Ví dụ, bản dịch và bài tập do Lexivela biên soạn.','Examples, translations and exercises written for Lexivela.','Exemples, traductions et exercices rédigés pour Lexivela.','例句、翻译和练习为 Lexivela 编写。'],
['Ưu tiên collocations và cụm diễn đạt trong bài, kèm câu gốc để ôn.','Prioritize collocations and useful phrases from the reading, with the original sentence for review.','Privilégiez les collocations et expressions du texte, avec la phrase originale pour réviser.','优先选择文章中的搭配和实用短语，并保留原句供复习。'],
['Số mục (từ / cụm)','Items (words / phrases)','Nombre de mots / expressions','数量（单词／短语）'],
['B1 trở lên gồm B1–C2, xét theo nghĩa của cả từ hoặc cụm. Bài ít mục phù hợp thì lấy ít hơn.','B1 and above includes B1–C2, based on the meaning of the whole word or phrase. Return fewer items if the reading has fewer suitable ones.','B1 et plus comprend B1–C2, selon le sens du mot ou de l’expression entière. Retenez moins d’éléments si le texte en contient moins.','B1 及以上包括 B1–C2，按整个词语或短语的含义判断。合适的词项较少时，可少选。'],
['Đã lưu','Saved','Enregistré','已保存'],
['Ôn tiếp','Next review:','Prochaine révision :','下次复习：'],
['khoảng {0} phút nữa','in about {0} minutes','dans environ {0} minutes','约 {0} 分钟后'],
['khoảng {0} giờ nữa','in about {0} hours','dans environ {0} heures','约 {0} 小时后'],
['Flashcard bài này','Flashcards for this reading','Cartes de cette lecture','本文词卡'],
['Flashcard bài đọc','Reading flashcards','Cartes de lecture','阅读词卡'],
['Về bài đọc','Back to reading','Retour à la lecture','返回文章'],
['Xem bộ từ','View this deck','Voir ces cartes','查看词卡组'],
['Bài này chưa có thẻ. Mở bài đọc rồi chọn “Flashcard bài này”.','No cards yet. Open the reading and choose “Flashcards for this reading”.','Pas encore de cartes. Ouvrez la lecture et choisissez « Cartes de cette lecture ».','暂无词卡。打开文章，选择“本文词卡”。'],
['Chưa tìm thấy từ có nghĩa sẵn trong bài này. Bạn có thể bôi đen từ để tra và lưu.','No matching words with saved meanings yet. Select a word in the reading to look it up and save it.','Aucun mot avec un sens enregistré pour cette lecture. Sélectionnez un mot pour le consulter et le sauvegarder.','暂未找到已有释义的匹配词。可选中文章中的词语查询并保存。'],
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
['Tổng quan','Overview','Vue d’ensemble','概览'],['Thư viện luyện đọc','Reading library','Bibliothèque de lecture','阅读库'],['Luyện IELTS Reading','IELTS Reading practice','Entraînement IELTS Reading','雅思阅读练习'],['Luyện TOEIC Reading','TOEIC Reading practice','Entraînement TOEIC Reading','TOEIC 阅读练习'],['Bài đọc của tôi','My readings','Mes lectures','我的文章'],['Kho từ của tôi','My vocabulary','Mon vocabulaire','我的词库'],['Luyện nhớ từ','Vocabulary practice','Réviser le vocabulaire','词汇练习'],['Thống kê truy cập','Visit statistics','Statistiques de visites','访问统计'],['Cài đặt & dữ liệu','Settings & data','Réglages et données','设置与数据'],['KHÔNG GIAN HỌC','LEARNING SPACE','ESPACE D’APPRENTISSAGE','学习空间'],['Đăng xuất','Sign out','Déconnexion','退出登录'],['Đóng','Close','Fermer','关闭'],['Hủy','Cancel','Annuler','取消'],['Lưu','Save','Enregistrer','保存'],['Xóa','Delete','Supprimer','删除'],['Sửa','Edit','Modifier','编辑'],['Lọc','Filter','Filtrer','筛选'],['Tìm kiếm','Search','Rechercher','搜索'],['Mỗi ngày, một chút.','A little every day.','Un peu chaque jour.','每天进步一点。'],['Không chỉ sưu tầm từ.','Go beyond collecting words.','Ne collectionnez pas seulement les mots.','不只是收集词汇。'],['Hãy biến chúng thành vốn từ của bạn.','Make them part of your vocabulary.','Faites-en votre vocabulaire.','让它们真正成为你的词汇。'],['Kho riêng · PostgreSQL','Your private collection','Votre collection privée','私人学习库'],['Bản HTML · localStorage','Offline preview · local storage','Aperçu hors ligne · stockage local','离线预览 · 本地存储'],['Đang mở kho học tập…','Opening your learning space…','Ouverture de votre espace…','正在打开学习空间…'],['Đang kết nối…','Connecting…','Connexion…','正在连接…'],['○ Không dùng API','○ Manual learning mode','○ Mode sans API','○ 手动学习模式'],['● AI đã kết nối','● AI connected','● IA connectée','● AI 已连接'],['Lexivela · Từ của bạn. Ngữ cảnh của bạn. Nhịp học của bạn.','Lexivela · Your words. Your context. Your pace.','Lexivela · Vos mots. Votre contexte. Votre rythme.','Lexivela · 你的词汇，你的语境，你的节奏。'],
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
['brand.imageAlt','Bạn thỏ tai lá đang đọc sách trong khu vườn nhỏ của Lexivela','A leaf-eared rabbit reading in Lexivela’s little garden','Un lapin aux oreilles en feuilles lit dans le petit jardin de Lexivela','叶子耳朵的小兔子在 Lexivela 的小花园里读书'],
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
legacy.push(...[["Nhập bộ từ cá nhân", "Import a vocabulary deck", "Importer une liste de mots", "导入个人词汇集"], ["Thêm cả bộ từ, xem trước rồi lưu để ôn mỗi ngày.", "Add a deck, preview it, and save it for daily practice.", "Ajoutez une liste, vérifiez-la puis enregistrez-la pour réviser chaque jour.", "添加词汇集，预览后保存，便于每日复习。"], ["Thêm bộ từ của bạn", "Add your vocabulary deck", "Ajouter votre liste de mots", "添加你的词汇集"], ["Chọn file bộ từ", "Choose a vocabulary file", "Choisir un fichier de vocabulaire", "选择词汇文件"], ["JSON · Tối đa 2 MB · 500 từ", "JSON · Up to 2 MB · 500 words", "JSON · 2 Mo maximum · 500 mots", "JSON · 最多 2 MB · 500 个词"], ["Tạo bộ từ với AI", "Create a deck with AI", "Créer une liste avec l’IA", "用 AI 创建词汇集"], ["Chọn chủ đề, sao chép prompt rồi dán vào AI bạn đang dùng. Mang file kết quả về đây để học.", "Choose a topic, copy the prompt into your AI tool, then import the result here.", "Choisissez un sujet, copiez le prompt dans votre outil IA, puis importez le résultat ici.", "选择主题，将提示词复制到你使用的 AI 工具中，再将结果导入这里。"], ["Bắt đầu từ bộ có sẵn", "Start with an existing deck", "Commencer avec une liste existante", "从现有词汇集开始"], ["Khám phá bộ từ theo chủ đề, lưu từ bạn cần rồi luyện bằng flashcard.", "Explore topic decks, save useful words, and practise with flashcards.", "Explorez les listes par thème, enregistrez les mots utiles puis révisez avec des cartes.", "探索主题词汇集，保存需要的词，并用闪卡练习。"], ["Khám phá bộ từ →", "Explore vocabulary decks →", "Explorer les listes de mots →", "探索词汇集 →"], ["Khám phá bộ luyện Reading →", "Explore reading practice sets →", "Explorer les séries de lecture →", "探索阅读练习集 →"], ["Bộ luyện Reading", "Reading practice sets", "Séries de lecture", "阅读练习集"], ["Chọn một bộ và luyện từng phần. Các bài luyện do Lexivela biên soạn.", "Choose a set and practise each section. These exercises are authored by Lexivela.", "Choisissez une série et travaillez chaque partie. Ces exercices sont rédigés par Lexivela.", "选择一套练习，按部分学习。练习内容由 Lexivela 编写。"], ["Loại nội dung", "Content type", "Type de contenu", "内容类型"], ["Đề Reading theo từng phần", "Reading tests by section", "Tests de lecture par partie", "分部分阅读测试"], ["Bộ luyện ngắn", "Short practice sets", "Séries courtes", "短篇练习集"], ["Tài liệu đọc thêm", "Further reading resources", "Ressources de lecture supplémentaires", "补充阅读资料"], ["Tìm bộ luyện", "Find practice sets", "Rechercher une série", "查找练习集"], ["Tìm theo tên…", "Search by title…", "Rechercher par titre…", "按标题搜索…"], ["Chưa có kết quả phù hợp.", "No matching results.", "Aucun résultat correspondant.", "暂无匹配结果。"]]);
legacy.push(['Chọn file JSON','Choose a JSON file','Choisir un fichier JSON','选择 JSON 文件']);
legacy.push(['Bản HTML chỉ tra các từ đã có trong bài. Mở bản web để tra thêm nghĩa.','The HTML preview only looks up words in the current reading. Open the web app for more definitions.','L’aperçu HTML ne recherche que les mots du texte actuel. Ouvrez le site pour consulter davantage de définitions.','HTML 预览仅查询当前文章中的词语。请打开网站查看其他释义。']);
legacy.push(
['Luyện đề TOEIC','TOEIC practice tests','Entraînement au TOEIC','TOEIC 模拟练习'],
['Chọn đề, làm bài và xem lời giải.','Choose a test, practise and review the answers.','Choisissez un test, entraînez-vous et consultez les corrigés.','选择练习，答题并查看解析。'],
['Cách làm bài →','Test tips →','Conseils pour le test →','答题方法 →'],
['Tìm đề theo tên…','Search tests by title…','Rechercher un test par titre…','按名称查找练习…'],
['Khác','Other','Autres','其他']);
legacy.push(...[
  [
    "Lọc từ trong bài đọc, tạo bộ riêng và ôn lại mỗi ngày.",
    "Extract words from a reading, build a personal deck and review daily.",
    "Relevez les mots d’un texte, créez votre liste et révisez chaque jour.",
    "从阅读中筛选词汇，创建个人词汇集并每天复习。"
  ],
  [
    "Tạo prompt cho AI",
    "Create an AI prompt",
    "Créer un prompt pour l’IA",
    "生成 AI 提示词"
  ],
  [
    "Ví dụ: Từ mới trong bài The Future of Work",
    "Example: Words from The Future of Work",
    "Exemple : Mots de The Future of Work",
    "例如：The Future of Work 中的生词"
  ],
  [
    "Nguồn từ vựng",
    "Vocabulary source",
    "Source du vocabulaire",
    "词汇来源"
  ],
  [
    "Từ bài đọc",
    "From a reading",
    "À partir d’un texte",
    "从阅读中筛选"
  ],
  [
    "Theo chủ đề",
    "By topic",
    "Par thème",
    "按主题生成"
  ],
  [
    "Bài đọc tiếng Anh",
    "English reading passage",
    "Texte en anglais",
    "英语阅读文章"
  ],
  [
    "Dán bài đọc bạn muốn lọc từ vào đây…",
    "Paste the reading you want to extract words from…",
    "Collez le texte dont vous souhaitez relever les mots…",
    "在此粘贴要筛选词汇的文章…"
  ],
  [
    "AI sẽ chọn từ trong bài và giữ lại câu gốc để bạn ôn theo ngữ cảnh.",
    "The AI will select words from the reading and keep the original sentences for context.",
    "L’IA sélectionnera les mots du texte et conservera les phrases originales pour le contexte.",
    "AI 会筛选文章中的词汇，并保留原句供你结合语境复习。"
  ],
  [
    "Mức từ vựng tối thiểu",
    "Minimum vocabulary level",
    "Niveau minimum du vocabulaire",
    "词汇最低级别"
  ],
  [
    "Số từ tối đa",
    "Maximum number of words",
    "Nombre maximum de mots",
    "词汇数量上限"
  ],
  [
    "Ví dụ: chọn B1 trở lên để học cả từ B1, B2, C1 và C2. Nếu bài có ít từ phù hợp, bộ từ sẽ ngắn hơn.",
    "For example, B1 and above includes B1, B2, C1 and C2. A reading with fewer suitable words will produce a shorter deck.",
    "Par exemple, B1 et plus inclut B1, B2, C1 et C2. Si le texte contient moins de mots adaptés, la liste sera plus courte.",
    "例如，B1 及以上包含 B1、B2、C1 和 C2。文章中符合条件的词较少时，词汇集也会更短。"
  ],
  [
    "Lexivela chỉ tạo prompt. Bạn tự dán vào AI mình đang dùng để lấy kết quả.",
    "Lexivela creates the prompt. Paste it into your AI tool to get the result.",
    "Lexivela crée le prompt. Collez-le dans votre outil IA pour obtenir le résultat.",
    "Lexivela 只生成提示词。请将其粘贴到你使用的 AI 工具中获取结果。"
  ],
  [
    "Nhập kết quả từ AI",
    "Import the AI result",
    "Importer le résultat de l’IA",
    "导入 AI 结果"
  ],
  [
    "Dán prompt vừa sao chép vào AI bạn đang dùng và gửi.",
    "Paste the copied prompt into your AI tool and send it.",
    "Collez le prompt dans votre outil IA et envoyez-le.",
    "将复制的提示词粘贴到你使用的 AI 工具中并发送。"
  ],
  [
    "Tải file JSON AI trả về, hoặc sao chép toàn bộ khối JSON.",
    "Download the JSON file from the AI, or copy the entire JSON block.",
    "Téléchargez le fichier JSON fourni par l’IA ou copiez tout le bloc JSON.",
    "下载 AI 返回的 JSON 文件，或复制完整的 JSON 内容。"
  ],
  [
    "Chọn file hoặc dán JSON bên dưới, rồi bấm Xem trước bộ từ.",
    "Choose the file or paste the JSON below, then preview the deck.",
    "Choisissez le fichier ou collez le JSON ci-dessous, puis affichez l’aperçu.",
    "在下方选择文件或粘贴 JSON，然后预览词汇集。"
  ],
  [
    "Đã có file bộ từ? Bạn có thể bắt đầu ngay ở bước này.",
    "Already have a vocabulary file? You can start at this step.",
    "Vous avez déjà un fichier de vocabulaire ? Commencez à cette étape.",
    "已有词汇文件？可以直接从这一步开始。"
  ],
  [
    "3. Xem lại và lưu bộ từ",
    "3. Review and save your deck",
    "3. Vérifier et enregistrer la liste",
    "3. 检查并保存词汇集"
  ],
  [
    "Sau khi xem trước, bỏ chọn từ bạn không muốn học rồi bấm Lưu bộ từ vào kho của tôi. Chọn Ôn bộ từ này để bắt đầu.",
    "In the preview, deselect unwanted words and save the deck to your library. Choose Review this deck to begin.",
    "Dans l’aperçu, décochez les mots inutiles et enregistrez la liste dans votre bibliothèque. Lancez ensuite la révision de cette liste.",
    "预览时取消勾选不想学习的词，再将词汇集保存到词库。选择复习此词汇集即可开始。"
  ],
  [
    "Khám phá bộ từ có sẵn →",
    "Explore existing decks →",
    "Explorer les listes disponibles →",
    "浏览现有词汇集 →"
  ],
  [
    "Bạn đặt tên bộ từ trước nhé, tối đa 100 ký tự.",
    "Enter a deck name of up to 100 characters.",
    "Saisissez un nom de liste de 100 caractères maximum.",
    "请先输入词汇集名称，最多 100 个字符。"
  ],
  [
    "Bạn chọn lại mức từ vựng và số từ nhé.",
    "Please select the vocabulary level and word count again.",
    "Sélectionnez à nouveau le niveau et le nombre de mots.",
    "请重新选择词汇级别和数量。"
  ],
  [
    "Bạn chọn lấy từ từ bài đọc hoặc theo chủ đề nhé.",
    "Choose a reading or a topic as the source.",
    "Choisissez un texte ou un thème comme source.",
    "请选择从文章中筛选或按主题生成。"
  ],
  [
    "Bạn dán bài đọc tiếng Anh vào bước 1 trước nhé.",
    "Paste the English reading into step 1 first.",
    "Collez d’abord le texte anglais à l’étape 1.",
    "请先在第 1 步粘贴英语文章。"
  ],
  [
    "Bài đọc quá dài. Bạn chia thành các phần dưới 20.000 ký tự nhé.",
    "The reading is too long. Split it into sections under 20,000 characters.",
    "Le texte est trop long. Divisez-le en parties de moins de 20 000 caractères.",
    "文章过长，请分成每段少于 20,000 个字符的部分。"
  ],
  [
    "Bạn điền chủ đề trước nhé, tối đa 200 ký tự.",
    "Enter a topic of up to 200 characters.",
    "Saisissez un thème de 200 caractères maximum.",
    "请先填写主题，最多 200 个字符。"
  ],
  [
    "Đã sao chép prompt kèm nội dung bạn chọn. Dán vào AI, rồi mang kết quả về bước 2 nhé.",
    "Prompt and source copied. Paste them into your AI tool, then bring the result to step 2.",
    "Prompt et contenu copiés. Collez-les dans votre outil IA, puis importez le résultat à l’étape 2.",
    "已复制提示词及所选内容。粘贴到 AI 工具中，再回到第 2 步导入结果。"
  ],
  [
    "File chưa đúng mẫu bộ từ Lexivela. Bạn tải mẫu ở bước 2 để đối chiếu nhé.",
    "The file does not match the Lexivela format. Download the sample in step 2 to compare.",
    "Le fichier ne suit pas le format Lexivela. Téléchargez le modèle à l’étape 2 pour comparer.",
    "文件不符合 Lexivela 格式，请下载第 2 步的示例进行对照。"
  ],
  [
    "Chưa đọc được file. Hãy dùng đúng khối JSON hoặc file mẫu ở bước 2.",
    "Could not read the file. Use the complete JSON block or the sample from step 2.",
    "Impossible de lire le fichier. Utilisez le bloc JSON complet ou le modèle de l’étape 2.",
    "无法读取文件，请使用完整的 JSON 或第 2 步的示例文件。"
  ],
  [
    "A1 trở lên",
    "A1 and above",
    "A1 et plus",
    "A1 及以上"
  ],
  [
    "A2 trở lên",
    "A2 and above",
    "A2 et plus",
    "A2 及以上"
  ],
  [
    "B1 trở lên",
    "B1 and above",
    "B1 et plus",
    "B1 及以上"
  ],
  [
    "B2 trở lên",
    "B2 and above",
    "B2 et plus",
    "B2 及以上"
  ],
  [
    "C1 trở lên",
    "C1 and above",
    "C1 et plus",
    "C1 及以上"
  ],
  [
    "C2 trở lên",
    "C2 and above",
    "C2 et plus",
    "C2 及以上"
  ]
]);
const dictionaries=Object.fromEntries(languages.map((l,i)=>[l,Object.fromEntries(rows.map(r=>[r[0],r[i+1]]))]));
const normalize=value=>value.replace(/\s+/g,' ').trim();
// Authored, local catalogs. No translation service is called in the browser.
const sourceMap=new Map((window.LEXI_INTERFACE_LOCALES||[]).map(r=>[normalize(r[0]),r]));
legacy.push(...[["Cách làm từng bước, có ví dụ để thử ngay.", "Step-by-step tips, with an example to try.", "Des conseils étape par étape, avec un exemple à essayer.", "分步讲解，配有即学即练的例题。"], ["Cách học với kênh này", "How to learn with this channel", "Comment apprendre avec cette chaîne", "如何利用这个频道学习"], ["Trình độ gợi ý; độ khó tùy video.", "Suggested levels; difficulty varies by video.", "Niveaux indicatifs ; la difficulté varie selon la vidéo.", "等级仅供参考，难度因视频而异。"], ["Chọn kênh phù hợp, học vài từ mới qua mỗi video.", "Find a channel and learn a few words with each video.", "Choisissez une chaîne et apprenez quelques mots avec chaque vidéo.", "选择合适的频道，每个视频学几个新词。"]]);
legacy.push(...[["Mở kênh YouTube · {0}", "Open YouTube channel · {0}", "Ouvrir la chaîne YouTube · {0}", "打开 YouTube 频道 · {0}"], ["Xem bài gợi ý · {0}", "Watch the suggested lesson · {0}", "Voir la leçon suggérée · {0}", "观看推荐课程 · {0}"], ["Nguồn giới thiệu · {0}", "About this channel · {0}", "À propos de cette chaîne · {0}", "频道介绍 · {0}"], ["Trình độ gợi ý", "Suggested level", "Niveau conseillé", "推荐级别"], ["Có nền tảng", "Elementary", "Élémentaire", "基础"], ["Xem xong, giữ lại một chút.", "Keep a few useful words.", "Retenez quelques mots utiles.", "记住几个实用词语。"], ["Nghe để nắm ý → nghe lại chỗ chưa rõ → thử nói hoặc viết bằng từ vừa học. Mỗi lần chỉ cần giữ 3–5 cụm hữu ích.", "Listen for the main idea, replay tricky parts, then use 3–5 new phrases in your own sentences.", "Écoutez pour saisir l’essentiel, réécoutez les passages difficiles puis utilisez 3 à 5 expressions nouvelles dans vos propres phrases.", "先听懂大意，再重听难点，然后用三至五个新短语造句。"]]);
legacy.push(...[["Ôn từ đến hạn hoặc chọn bộ bạn muốn học.", "Review due words or pick a deck to practise.", "Révisez les mots à revoir ou choisissez une liste.", "复习到期词汇，或选择想学的词汇集。"]]);
legacy.push(...[["IELTS Reading", "IELTS Reading", "IELTS Reading", "IELTS Reading"], ["TOEIC Reading", "TOEIC Reading", "TOEIC Reading", "TOEIC Reading"], ["IELTS & TOEIC Reading", "IELTS & TOEIC Reading", "IELTS & TOEIC Reading", "IELTS & TOEIC Reading"], ["Xem bài", "View lessons", "Voir les leçons", "查看文章"], ["Chọn trình độ và chủ đề.", "Choose a level and topic.", "Choisissez un niveau et un thème.", "选择级别和主题。"], ["Bộ đề Reading", "Reading sets", "Séries de lecture", "阅读套题"], ["Cách làm từng dạng bài", "Question-type guides", "Guides par type de question", "各类题型指南"], ["Thông tin bài", "About these exercises", "À propos des exercices", "练习说明"], ["Bài tập do Lexivela biên soạn.", "Original exercises by Lexivela.", "Exercices créés par Lexivela.", "Lexivela 原创练习。"]]);
legacy.push(...[["Cụm trong câu", "Phrases in context", "Expressions en contexte", "语境中的词组"], ["Cụm trong câu · EWT", "Phrases in context · EWT", "Expressions en contexte · EWT", "语境中的词组 · EWT"], ["Cặp từ được lọc từ câu thực tế. Xem cả câu để hiểu cách dùng; không phải cụm nào cũng là collocation cố định.", "Word pairs found in real sentences. Read the whole sentence for context; not every pair is a fixed collocation.", "Paires de mots tirées de phrases réelles. Lisez la phrase entière pour comprendre leur emploi ; toutes ne sont pas des collocations fixes.", "词对来自真实例句。请阅读整句理解用法；并非每个词对都是固定搭配。"], ["Nguồn EWT", "EWT source", "Source EWT", "EWT 来源"], ["UD English EWT 2.18 · Natalia Silveira, Sebastian Schuster, Nathan Schneider và các cộng tác viên. Các cặp từ được lọc tự động từ câu có sẵn.", "UD English EWT 2.18 · Natalia Silveira, Sebastian Schuster, Nathan Schneider and contributors. Word pairs are automatically extracted from source sentences.", "UD English EWT 2.18 · Natalia Silveira, Sebastian Schuster, Nathan Schneider et leurs collaborateurs. Les paires sont extraites automatiquement des phrases sources.", "UD English EWT 2.18 · Natalia Silveira、Sebastian Schuster、Nathan Schneider 及其他贡献者。词对由原始例句自动提取。"]]);
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
