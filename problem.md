# Problem Statement: Hệ thống khai thác dữ liệu y khoa từ sách

## 1. Bối cảnh

Có một cuốn sách y khoa tiếng Việt dạng PDF scan, **đã được OCR sẵn** (PDF có lớp text). Nội dung sách hiện chỉ đọc được thủ công, không tra cứu, truy vấn hay tái sử dụng được.

Mục tiêu là xây dựng hệ thống **biến nội dung cuốn sách thành nguồn tri thức truy vấn được**, phục vụ:
- Hỏi đáp bằng ngôn ngữ tự nhiên.
- Truy vấn hàng loạt (liệt kê, lọc, tổng hợp) theo bệnh, nguyên nhân, triệu chứng, phương pháp điều trị...
- Làm nguồn dữ liệu cho các hệ thống RAG.

## 2. Đầu vào

| Mục | Mô tả |
|---|---|
| Nguồn dữ liệu | **1 cuốn sách** y khoa (giai đoạn hiện tại) |
| Định dạng | PDF scan đã có lớp text từ OCR |
| Ngôn ngữ | Tiếng Việt (có thể lẫn thuật ngữ Latin/tiếng Anh, tên thuốc) |
| Chất lượng text | Có thể còn lỗi OCR: sai/mất dấu, xuống dòng giữa câu, header/footer, số trang, bảng bị vỡ |

**Không cần làm OCR.** Hệ thống chỉ đọc lớp text có sẵn trong PDF.

## 3. Ràng buộc kỹ thuật

- **LLM:** dùng API **OpenRouter**.
- **Ngôn ngữ lập trình:** Python.
- Kiến trúc phải mở rộng được sang **nhiều sách/nhiều nguồn** về sau, dù hiện tại chỉ có 1 cuốn.

## 4. Yêu cầu chức năng

### 4.1. Xử lý và cấu trúc hóa nội dung sách
- Trích xuất text từ PDF, làm sạch lỗi OCR và chuẩn hóa tiếng Việt.
- Nhận diện cấu trúc sách: chương → bệnh → mục (định nghĩa, nguyên nhân, triệu chứng, chẩn đoán, điều trị, biến chứng, phòng bệnh...).
- Mỗi đơn vị nội dung phải **giữ được vị trí nguồn** (trang, chương, mục).

### 4.2. Hỏi đáp (Q&A)
Trả lời câu hỏi cụ thể bằng tiếng Việt, ví dụ:
- "Triệu chứng của viêm khớp dạng thấp là gì?"
- "Nguyên nhân gây viêm loét dạ dày?"
- "Điều trị tăng huyết áp như thế nào?"

### 4.3. Truy vấn hàng loạt / tổng hợp
Trả lời được các câu hỏi cần quét toàn bộ sách, ví dụ:
- "Liệt kê các loại bệnh đau."
- "Những bệnh nào có triệu chứng sốt và đau khớp?"
- "Những bệnh nào được điều trị bằng corticoid?"
- "Liệt kê nguyên nhân, triệu chứng, phương pháp điều trị của tất cả bệnh trong chương X."

Chạy được **danh sách câu hỏi theo lô** (file đầu vào) hoặc theo **template** áp dụng cho nhiều bệnh, sau đó xuất kết quả ra Excel/CSV/JSON.

### 4.4. Dữ liệu có cấu trúc
Trích xuất thông tin mỗi bệnh theo schema thống nhất, tối thiểu gồm: tên bệnh, tên gọi khác, nhóm bệnh, định nghĩa, nguyên nhân, yếu tố nguy cơ, triệu chứng, chẩn đoán, điều trị (phương pháp, thuốc), biến chứng, phòng bệnh, trang nguồn.

Chuẩn hóa các tên gọi đồng nghĩa (ví dụ "đau đầu" = "nhức đầu") để truy vấn tổng hợp cho kết quả đúng.

### 4.5. Phục vụ RAG
Có chỉ mục tìm kiếm (vector + từ khóa) trên nội dung sách, kèm metadata (bệnh, loại mục, trang). Chỉ mục và dữ liệu có cấu trúc phải xuất được để hệ thống khác tái sử dụng.

### 4.6. Sinh dữ liệu huấn luyện LLM
- Từ nội dung sách đã cấu trúc hóa, sinh bộ dữ liệu để fine-tune một LLM mã nguồn mở cỡ **< 26B tham số**.
- Dữ liệu ở định dạng chuẩn (JSONL hội thoại) và **truy ngược được về nguồn** (bệnh, mục, trang).
- Dữ liệu phục vụ **cả hai chế độ trả lời**: trả lời trực tiếp không cần tài liệu (closed-book) và trả lời dựa trên ngữ cảnh RAG (chi tiết ở mục 6).
- Giai đoạn hiện tại: **sinh và kiểm tra dữ liệu mẫu**. Huấn luyện thật làm ở giai đoạn sau.

## 5. Yêu cầu phi chức năng

- **Trung thực với nguồn:** câu trả lời và dữ liệu trích xuất chỉ dựa trên nội dung sách, không bịa và không bổ sung kiến thức ngoài. Nếu sách không đề cập thì phải nói rõ.
- **Trích dẫn:** mọi câu trả lời phải kèm nguồn (tên bệnh/mục, số trang).
- **Bảo toàn nội dung chuyên môn:** khi sửa lỗi OCR không được thay đổi liều lượng, tên thuốc, tên hoạt chất hay số liệu.
- **Kiểm chứng được:** có bộ câu hỏi chuẩn để đo độ chính xác của tìm kiếm, câu trả lời và dữ liệu trích xuất.
- **Chi phí và độ ổn định:** gọi API có cache, retry, giới hạn tốc độ, và tiếp tục được khi bị lỗi giữa chừng lúc chạy lô.

## 6. Dữ liệu huấn luyện và huấn luyện LLM (< 26B)

### 6.1. Định hướng: fine-tune để làm gì?

Một model duy nhất sau fine-tune phải làm được **cả hai chế độ trả lời**:

| Chế độ | Mô tả | Đầu vào lúc dùng | Điểm mạnh | Rủi ro |
|---|---|---|---|---|
| **A. Trả lời trực tiếp (closed-book)** | Model đã "học" nội dung sách, trả lời không cần tài liệu đi kèm | Chỉ có câu hỏi | Nhanh, không cần hạ tầng tìm kiếm, chạy offline | Có thể nhớ sai chi tiết (liều thuốc, con số), lẫn lộn giữa các bệnh |
| **B. Trả lời dựa trên RAG** | Model đọc các đoạn trích do hệ thống tìm được rồi trả lời từ đó | Câu hỏi + các đoạn trích | Chính xác, trích dẫn được trang, dễ cập nhật | Phụ thuộc chất lượng tìm kiếm |

Ngoài ra model cũng cần học thêm các năng lực chung cho cả hai chế độ:
- **Văn phong y khoa tiếng Việt:** dùng đúng thuật ngữ, trình bày có cấu trúc (nguyên nhân / triệu chứng / điều trị), có câu nhắc "không thay thế chẩn đoán của bác sĩ".
- **Thao tác có cấu trúc:** trích xuất JSON theo schema ở mục 4.4 và gọi tool, để thay model API bằng model tự host.

**Phân biệt chế độ bằng system prompt:** mỗi chế độ dùng một system prompt riêng, cố định. Model nhận ra chế độ qua system prompt và qua việc có hay không có khối "Tài liệu:" trong câu hỏi.

**Lưu ý về chế độ A:**
- Một cuốn sách chỉ có khoảng vài trăm nghìn đến 1 triệu token. Muốn model nhớ được kiến thức, **mỗi sự kiện phải xuất hiện nhiều lần dưới nhiều cách diễn đạt khác nhau** (xem D1b, D2, D8 ở mục 6.2). Chỉ huấn luyện mỗi câu hỏi một lần thì model sẽ không nhớ.
- Ở chế độ A, model chỉ trích dẫn tới mức **chương / tên bệnh**, không trích số trang, vì nhớ số trang rất dễ sai.
- Với thông tin rủi ro cao (liều thuốc, chống chỉ định), chế độ A nên khuyến nghị người dùng kiểm tra lại bằng chế độ B hoặc tra trực tiếp trong sách.

### 6.2. Các loại dữ liệu cần sinh

Tất cả đều sinh tự động từ đầu ra của bài toán chính: cây cấu trúc sách, các chunk RAG và dữ liệu có cấu trúc theo bệnh. LLM qua OpenRouter đóng vai trò "teacher".

| # | Loại dữ liệu | Cách sinh | Chế độ | Dùng cho giai đoạn |
|---|---|---|---|---|
| D1 | **Văn bản sạch** của sách | Đầu ra làm sạch, chia theo mục, mỗi mục kèm tiêu đề "Chương – Bệnh – Mục" | A | Continued pretraining |
| D1b | **Văn bản diễn đạt lại** | LLM viết lại mỗi mục theo 5–10 cách: tóm tắt, giảng giải cho sinh viên, dạng gạch đầu dòng, dạng hỏi–đáp, liên hệ với bệnh khác. **Giữ nguyên mọi con số, tên thuốc, liều lượng.** | A | Continued pretraining |
| D2 | **QA đơn lẻ** | Mỗi mục của bệnh → 3–10 cặp hỏi–đáp ("Triệu chứng của X?", "Thuốc nào dùng cho X?") | A (không kèm tài liệu) | SFT |
| D3 | **QA tổng hợp / liệt kê** | Sinh từ database có cấu trúc ("Bệnh nào có triệu chứng sốt?", "So sánh điều trị X và Y") | A và B | SFT |
| D4 | **QA có ngữ cảnh RAG** | Đầu vào = câu hỏi + top-k đoạn tìm được (gồm cả đoạn đúng và **đoạn nhiễu**); đầu ra = câu trả lời chỉ dựa trên đoạn đúng, có trích dẫn trang | B | SFT |
| D5 | **Mẫu từ chối** | Chế độ B: ngữ cảnh không chứa câu trả lời → "Tài liệu không đề cập...". Chế độ A: hỏi về bệnh hoặc nội dung không có trong sách → "Sách không đề cập...". Chiếm khoảng 10–15% bộ dữ liệu. | A và B | SFT |
| D6 | **Trích xuất có cấu trúc** | Đầu vào = văn bản một bệnh; đầu ra = JSON theo schema ở 4.4 | Chung | SFT |
| D7 | **Dữ liệu ưu tiên (preference)** | Cùng một câu hỏi: *chosen* = trả lời đúng nguồn; *rejected* = trả lời bịa, sai liều, lẫn bệnh, thiếu trích dẫn | A và B | DPO/ORPO (tùy chọn) |
| D8 | **QA closed-book nhiều cách hỏi** | Mỗi sự kiện quan trọng (triệu chứng chính, thuốc điều trị, liều) hỏi theo **≥ 5 cách khác nhau**, hỏi theo cả hai chiều ("X có triệu chứng gì?" và "Triệu chứng Y gặp trong bệnh nào?") | A | SFT |

**Một câu hỏi, hai mẫu:** cùng một câu hỏi nên sinh **một mẫu chế độ A và một mẫu chế độ B**. Nhờ đó model học được cả kiến thức lẫn cách đọc tài liệu, và dữ liệu cũng dùng được để so sánh hai chế độ.

**Đa dạng hóa câu hỏi:** diễn đạt lại theo nhiều kiểu người hỏi (bệnh nhân hỏi bình dân, sinh viên y, bác sĩ), câu hỏi ngắn hoặc dài, sai chính tả nhẹ, không dấu, hội thoại nhiều lượt.

**Tỉ lệ trộn gợi ý cho SFT:** khoảng 40% chế độ A, 40% chế độ B, 20% còn lại (trích xuất JSON, từ chối, liệt kê). Tinh chỉnh dần theo kết quả đánh giá.

**Quy mô ước tính:**
- Continued pretraining (D1 + D1b): khoảng 5–10 triệu token, tức gấp 5–10 lần độ dài sách.
- SFT: khoảng 20.000–60.000 mẫu.
- DPO: khoảng 2.000–5.000 cặp.
- Con số cụ thể phụ thuộc vào số bệnh trong sách.

### 6.3. Định dạng dữ liệu

JSONL dạng hội thoại (tương thích chat template của hầu hết model mở), kèm metadata để truy vết.

**Mẫu chế độ A (trả lời trực tiếp):**

```json
{
  "messages": [
    {"role": "system", "content": "Bạn là trợ lý y khoa, trả lời dựa trên kiến thức từ sách <tên sách>. Nếu sách không đề cập, hãy nói rõ."},
    {"role": "user", "content": "Viêm khớp dạng thấp có triệu chứng gì?"},
    {"role": "assistant", "content": "Theo sách (Chương 3 – Viêm khớp dạng thấp), các triệu chứng gồm: ..."}
  ],
  "meta": {"task": "closed_book_qa", "mode": "A", "disease": "Viêm khớp dạng thấp", "section": "symptom", "pages": [121], "fact_ids": ["..."]}
}
```

**Mẫu chế độ B (có tài liệu RAG):**

```json
{
  "messages": [
    {"role": "system", "content": "Bạn là trợ lý tra cứu y khoa. Chỉ trả lời dựa trên tài liệu được cung cấp và ghi rõ trang nguồn."},
    {"role": "user", "content": "Tài liệu:\n[1] (Viêm khớp dạng thấp – Triệu chứng, tr.121) ...\n[2] (Thoái hóa khớp – Điều trị, tr.140) ...\n\nCâu hỏi: Viêm khớp dạng thấp có triệu chứng gì?"},
    {"role": "assistant", "content": "Theo tài liệu, viêm khớp dạng thấp có các triệu chứng: ... (tr.121)."}
  ],
  "meta": {"task": "rag_qa", "mode": "B", "disease": "Viêm khớp dạng thấp", "section": "symptom", "pages": [121], "source_chunk_ids": ["..."]}
}
```

### 6.4. Kiểm soát chất lượng dữ liệu

- **Kiểm tra trung thực tự động:** dùng một LLM khác làm giám khảo, chấm xem câu trả lời có được văn bản nguồn hỗ trợ hay không, rồi loại mẫu không đạt.
- **Kiểm tra số liệu:** liều thuốc, con số, tên thuốc trong câu trả lời phải xuất hiện nguyên văn trong nguồn (kiểm bằng quy tắc).
- **Khử trùng lặp** các câu hỏi gần giống nhau (dùng embedding).
- **Người có chuyên môn duyệt mẫu ngẫu nhiên** khoảng 2–5% bộ dữ liệu.
- **D1b phải giữ nguyên dữ kiện:** so khớp các con số, tên thuốc và liều lượng giữa bản diễn đạt lại và bản gốc. Lệch thì loại bỏ.
- **Chia train/val/test khác nhau cho từng chế độ:**
  - *Chế độ B:* chia **theo bệnh**. Bệnh trong tập test không xuất hiện trong train, để đo khả năng đọc tài liệu mới.
  - *Chế độ A:* **không thể** chia theo bệnh, vì model phải đã học bệnh đó mới trả lời được. Thay vào đó, tập test gồm **câu hỏi diễn đạt mới** về các sự kiện đã có trong train (chia theo `fact_id` và kiểu diễn đạt), để đo xem model hiểu hay chỉ thuộc lòng câu hỏi.
- Bộ câu hỏi chuẩn ở mục 8 **không bao giờ** được đưa vào train, kể cả dưới dạng diễn đạt lại.

### 6.5. Quy trình huấn luyện

**Bước 1: Chọn model nền (< 26B)**
- Tiêu chí: hỗ trợ tiếng Việt tốt, giấy phép cho phép fine-tune và sử dụng, context dài (≥ 8K token để chứa ngữ cảnh RAG), có sẵn bản instruct.
- Ứng viên tham khảo: dòng **Qwen** (7B–14B), **Gemma** (≤ 12B), **Llama 3.x 8B**, các model tối ưu cho tiếng Việt / Đông Nam Á (**SeaLLM**, **Vistral**...). Cần kiểm tra lại các phiên bản mới nhất tại thời điểm triển khai.
- Cách chọn: chạy 2–3 ứng viên ở dạng **base + RAG, chưa fine-tune** trên bộ câu hỏi chuẩn, rồi chọn model tốt nhất làm nền. Điểm này cũng là **baseline** để so sánh sau fine-tune.

**Bước 2: Continued pretraining (CPT) trên D1 + D1b**, bắt buộc để phục vụ chế độ A
- Mục tiêu: nạp kiến thức của sách vào model.
- Trộn khoảng 70–80% dữ liệu sách với 20–30% dữ liệu tiếng Việt tổng quát, để model không quên kiến thức cũ (catastrophic forgetting).
- Dùng LoRA rank cao (64–256) và **bật train cả `embed_tokens` / `lm_head`** (Unsloth hỗ trợ sẵn), hoặc full fine-tune nếu đủ GPU. Chạy 2–4 epoch, learning rate thấp hơn bước SFT.
- Sau bước này, kiểm tra nhanh bằng cách hỏi closed-book khoảng 50 câu để xem model đã nhớ được bao nhiêu.

**Bước 3: Supervised Fine-Tuning (SFT) trên D2–D6, D8** (trộn cả chế độ A và B)
- Phương pháp: **LoRA / QLoRA** (chỉ huấn luyện adapter), đủ tốt và rẻ cho bài toán này.
- Công cụ: **Unsloth** (nhanh, tiết kiệm VRAM), **LLaMA-Factory** (có giao diện, cấu hình bằng YAML), **TRL** hoặc **Axolotl**.
- Cấu hình khởi điểm (tinh chỉnh dần qua tập val):

  | Tham số | Giá trị gợi ý |
  |---|---|
  | LoRA rank / alpha | 16–64 / gấp 1–2 lần rank |
  | Target modules | Tất cả lớp attention + MLP |
  | Learning rate | 1e-4 – 2e-4 (cosine, warmup ~3%) |
  | Epochs | 2–3 (theo dõi val loss để tránh overfit) |
  | Max sequence length | 4096–8192 (đủ cho ngữ cảnh RAG) |
  | Loss | Chỉ tính trên phần trả lời của assistant |

**Bước 4 (tùy chọn): Preference tuning (DPO/ORPO) trên D7**
- Mục tiêu: giảm bịa, tăng thói quen trích dẫn và từ chối đúng lúc.

**Bước 5: Đóng gói và triển khai**
- Merge LoRA vào model, lượng tử hóa (GGUF cho Ollama/llama.cpp, AWQ/GPTQ cho vLLM).
- Phục vụ qua **API tương thích OpenAI** (vLLM / Ollama), để hệ thống chỉ cần đổi `base_url` là chuyển từ OpenRouter sang model tự host.

### 6.6. Phần cứng ước tính (QLoRA 4-bit)

| Cỡ model | VRAM tối thiểu | Ví dụ GPU |
|---|---|---|
| 7–9B | ~16–24 GB | RTX 4090, L4, A10 |
| 12–14B | ~24–32 GB | RTX 4090 (seq ngắn), A100 40GB |
| 20–26B | ~40–48 GB | A100 80GB, H100, L40S |

Nếu không có GPU riêng, có thể thuê GPU cloud theo giờ (RunPod, Vast.ai, Lambda, Colab Pro). Với vài chục nghìn mẫu, một lần SFT trên model 8–14B thường mất vài giờ.

### 6.7. Đánh giá model sau huấn luyện

So sánh **4 cấu hình** trên các tập test tương ứng (mục 6.4) và bộ câu hỏi chuẩn:

1. Model nền, không RAG (baseline của chế độ A)
2. Model nền + RAG (baseline của chế độ B)
3. **Model fine-tune, không RAG** (mục tiêu chế độ A)
4. **Model fine-tune + RAG** (mục tiêu chế độ B)

Chỉ số đo:
- Độ đúng của câu trả lời.
- **Riêng chế độ A:** tỉ lệ nhớ đúng sự kiện, nhất là liều thuốc và con số; tỉ lệ lẫn lộn giữa các bệnh; khả năng trả lời câu hỏi diễn đạt mới và câu hỏi theo chiều ngược.
- Độ trung thực (tỉ lệ thông tin bịa).
- Trích dẫn đúng trang.
- Tỉ lệ từ chối đúng / từ chối sai.
- Độ chính xác JSON khi trích xuất.
- **Kiểm tra suy giảm năng lực chung**: model không được kém đi rõ rệt ở các tác vụ tiếng Việt thông thường.

### 6.8. Lưu ý pháp lý

- **Bản quyền sách:** cần có quyền sử dụng nội dung sách để huấn luyện và phân phối model.
- **Điều khoản của model teacher:** một số nhà cung cấp trên OpenRouter cấm dùng output của họ để huấn luyện model khác.
  - **Giai đoạn hiện tại:** chỉ **thử nghiệm sinh dữ liệu mẫu**, chưa huấn luyện, nên được dùng bất kỳ model nào trên OpenRouter.
  - **Trước khi huấn luyện thật:** rà soát lại điều khoản, nếu cần thì sinh lại dữ liệu bằng model cho phép. Vì vậy mỗi mẫu cần lưu `meta.teacher_model` để lọc hoặc sinh lại dễ dàng.
- **Giấy phép model nền:** kiểm tra điều kiện sử dụng thương mại.

## 7. Ngoài phạm vi (giai đoạn hiện tại)

- OCR từ ảnh scan.
- Xử lý nhiều sách cùng lúc (chỉ cần thiết kế sẵn để mở rộng).
- Tư vấn hoặc chẩn đoán y khoa cho người bệnh: hệ thống chỉ là công cụ tra cứu tài liệu.
- Huấn luyện model từ đầu (pretraining từ con số 0).
- **Huấn luyện thật:** giai đoạn hiện tại chỉ sinh và kiểm tra dữ liệu mẫu. Mục 6.5–6.7 là định hướng cho giai đoạn sau.

## 8. Tiêu chí thành công

| Tiêu chí | Mục tiêu |
|---|---|
| Số bệnh nhận diện được so với mục lục sách | Khớp đầy đủ |
| Tìm kiếm: đoạn đúng nằm trong top 5 (Recall@5) | ≥ 90% |
| Độ chính xác dữ liệu trích xuất (so với nhãn tay ~20 bệnh) | ≥ 90%, không có thông tin bịa |
| Câu trả lời có trích dẫn nguồn đúng | 100% |
| Trả lời đúng cả câu hỏi cụ thể và câu hỏi liệt kê/tổng hợp | Đạt trên bộ câu hỏi chuẩn (~100 câu) |
| Dữ liệu huấn luyện qua kiểm tra trung thực (mục 6.4) | ≥ 95% mẫu được giữ lại đạt yêu cầu khi duyệt tay |
| Model fine-tune, chế độ A, so với model nền không RAG | Tốt hơn rõ rệt về độ đúng; tỉ lệ sai liều/con số thấp, đo trên tập test câu hỏi diễn đạt mới |
| Model fine-tune + RAG (chế độ B) so với model nền + RAG | Tốt hơn về độ đúng, trích dẫn và tỉ lệ bịa trên bộ test |
| Model fine-tune + RAG so với LLM API (OpenRouter) + RAG | Đạt mức tương đương, đủ để thay thế khi tự host |

## 9. Vấn đề còn mở

- Model cụ thể trên OpenRouter cho từng tác vụ (làm sạch, trích xuất, hỏi đáp), cân đối giữa chất lượng và chi phí.
- Danh sách nhóm bệnh cần phân loại (ví dụ: bệnh đau, nhiễm trùng, mạn tính...).
- Người duyệt chuyên môn cho bộ câu hỏi chuẩn và cho bảng chuẩn hóa thuật ngữ.
- Giao diện sử dụng: web UI, API, hay cả hai.
- Model nền cụ thể để fine-tune, và hạ tầng GPU (máy riêng hay thuê cloud).
- Mức sai sót chấp nhận được ở chế độ A, và chế độ A có được trả lời về liều thuốc hay không.
- Quyền sử dụng sách để huấn luyện, và model teacher trên OpenRouter có cho phép dùng output để huấn luyện hay không.
- Model sau fine-tune dùng nội bộ hay phát hành ra ngoài (ảnh hưởng đến yêu cầu giấy phép).
