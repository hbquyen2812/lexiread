# Tài liệu đối chiếu

Đối chiếu ngày 18/10/2026. Các nguồn dưới đây dành cho API, framework và phân biệt từ; không phải cam kết rằng toàn bộ dependency đã được integration-test cùng nhau.

## Công nghệ — tài liệu chính thức

- Django supported releases (5.2 LTS): https://www.djangoproject.com/download/
- Django deployment checklist: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- Docker Desktop / Windows / WSL 2: https://docs.docker.com/desktop/setup/install/windows-install/
- OpenAI Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- GPT-4.1 mini model reference: https://developers.openai.com/api/docs/models/gpt-4.1-mini
- ChatGPT và API có billing riêng: https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform
- pypdf text extraction, hạn chế của PDF scan: https://pypdf.readthedocs.io/en/stable/user/extract-text.html

Django5.2 được chọn vì là LTS và phù hợp app này, không vì được coi là release mới nhất. Requirements dùng khoảng phiên bản; sau khi chạy integration tests trên máy thực, nên khóa lại phiên bản đã kiểm thử và cập nhật patch bảo mật có kiểm soát.

## Từ vựng — từ điển

- reinstate: https://www.merriam-webster.com/dictionary/reinstate
- monumental: https://www.merriam-webster.com/dictionary/monumental
- depict: https://www.merriam-webster.com/dictionary/depict
- undertaking: https://www.merriam-webster.com/dictionary/undertaking
- on the spur of the moment: https://www.merriam-webster.com/dictionary/on%20the%20spur%20of%20the%20moment
- pull out: https://www.merriam-webster.com/dictionary/pull%20out
- step down: https://www.merriam-webster.com/dictionary/step%20down
- flawed: https://www.merriam-webster.com/dictionary/flawed
- defective: https://www.merriam-webster.com/dictionary/defective

Nghĩa tiếng Việt, ví dụ ngắn và ghi chú trong dataset là nội dung biên soạn để học. Không sao chép ví dụ từ điển dài, không gắn nhãn official IELTS, không đưa IPA/CEFR suy đoán. Bài Set in Metal do người học cung cấp; không có nguồn xuất bản độc lập trong gói. Giữ passage trong thư viện cá nhân, không coi việc có file là quyền tái xuất bản công khai.


## Bổ sung khi xây Reading Studio v2

- Django migrations: https://docs.djangoproject.com/en/5.2/topics/migrations/
- OWASP LLM Prompt Injection Prevention: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- CEFR descriptors (Council of Europe): https://www.coe.int/en/web/common-european-framework-reference-languages/the-cefr-descriptors
- pypdf published releases: https://pypi.org/project/pypdf/

Các nguồn công nghệ trên hỗ trợ lựa chọn thiết kế; không phải cơ quan đã kiểm định app. 12 bài mới là nội dung học hư cấu nguyên gốc, không lấy từ những website này; nhãn trình độ chỉ là ước lượng biên soạn.
