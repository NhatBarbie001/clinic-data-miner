# Plan I5: công cụ để bạn tự soát cây IASP (spotcheck + bảng hội chứng)

> Thuộc [plan P2R](plan.md) (đã duyệt) · Trạng thái: `Đã duyệt` 2026-10-26 (mặc định mục 9) · Ngày: 2026-10-26
> Đầu vào: cây sau I4 (`data/books/iasp/p2_tree/nodes.jsonl`), dòng P1 (`lines.jsonl`), PDF gốc

## 1. Vì sao cần

I1-I4 kiểm bằng máy: đếm độc lập trên PDF rồi so (số hội chứng, mã, trang, mục lục…). Máy **không
tự thấy** được các lỗi kiểu:

| Lỗi | Ví dụ | Máy đếm có thấy? |
|---|---|---|
| Ranh giới sai | 3 dòng cuối của `Relief` (hội chứng A) bị gán vào hội chứng B kế tiếp | không - tổng số chữ vẫn đủ |
| Lẫn cột | 1 đoạn cột phải chen vào giữa mục cột trái | không - không mất chữ nào |
| Mục bị cắt / nuốt | `Usual Course` nuốt luôn `Complications` vì tên mục không in đậm | khó |
| Tên sai | tên hội chứng dính thêm 1 dòng của đoạn văn | khó |

Chỉ người **nhìn trang gốc** mới bắt được. Plan P2R đặt chỉ tiêu **A9: bạn soát 10 hội chứng ngẫu
nhiên, đạt ≥ 9/10**. I5 làm công cụ để việc soát đó mất ~15-20 phút thay vì lật PDF thủ công.
(I5 chỉ làm công cụ; bạn chấm thật ở I6.)

## 2. Kết quả bạn nhận được

```
uv run dm --book iasp p2 spotcheck --n 10          # chọn mẫu + sinh trang soát + bảng hội chứng
→ data/books/iasp/p2_tree/spotcheck/index.html      mở bằng trình duyệt (không cần mạng)
→ data/books/iasp/p2_tree/spotcheck/review.csv      phiếu chấm (10 dòng)
→ data/books/iasp/p2_tree/syndromes.csv             mọi hội chứng, mở bằng Excel
uv run dm --book iasp p2 spotcheck score            # đọc phiếu chấm → A9 đạt / chưa đạt
```

### 2.1 Trang soát `index.html`: mỗi hội chứng một khung

```
┌─ 3/10 · Tumors of the Brachial Plexus · XI-1 · GROUP XI · PDF 137 ───────────────────────────────┐
│ ┌──────────── ảnh trang PDF 137 ────────────┐  Mã IASP: 102.X4b, 202.X4b   Cờ: (không)           │
│ │ ▓▓ Tumors of the Brachial Plexus (XI-1) ▓▓│  ─────────────────────────────────────────────    │
│ │ ░Definition░  ┊ ░Main Features░           │  ▸ Definition [definition]                        │
│ │ ░Progressive aching…░ ┊ ░Incidence: …░    │    Progressive aching, burning pain with …        │
│ │ ▒Site▒        ┊ ▒Associated…▒             │  ▸ Site [site]                                    │
│ │ ▒Shoulder and upper limb.▒                │    Shoulder and upper limb.                       │
│ │   … (vùng tô màu = phần máy gán cho       │  ▸ System [body_system] …                         │
│ │      hội chứng này; mỗi mục một màu)      │  … (đủ mọi mục, toàn văn)                         │
│ └───────────────────────────────────────────┘                                                    │
│  Chấm: ☐ Đúng tên   ☐ Đúng ranh giới   ☐ Đủ mục, đúng nội dung   ☐ Không lẫn cột   Ghi chú: [   ] │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Bên trái:** ảnh thật của (các) trang PDF chứa hội chứng. Vùng chữ máy gán cho hội chứng được
  **tô màu, mỗi mục một màu**, tên hội chứng viền đậm. Cách đọc nhanh: *chữ của hội chứng này mà
  không được tô = bị sót / bị gán cho nút khác; vùng tô lan sang hội chứng khác = ranh giới sai.*
- **Bên phải:** nội dung máy tách ra: tên, mã, mã IASP, cờ, từng mục kèm loại mục và **toàn văn**.
  Rê chuột lên một mục → vùng tương ứng bên trái nháy viền (biết ngay mục đó lấy chữ từ đâu).
- **4 ô chấm + ghi chú** cho mỗi hội chứng, đúng 4 tiêu chí của A9. Lưu tạm ngay trong trình duyệt
  (đóng mở lại không mất); nút **"Tải phiếu chấm (CSV)"** xuất ra file cùng dạng `review.csv`.
- Một file HTML + thư mục ảnh `pages/*.jpg`; không dùng thư viện ngoài, không cần internet.

### 2.2 Phiếu chấm `review.csv` (cách chấm thứ 2: Excel)

| unit_id | code | title | pdf_pages | ok_title | ok_boundary | ok_sections | ok_columns | note |
|---|---|---|---|---|---|---|---|---|
| nd_… | XI-1 | Tumors of the Brachial Plexus | 137 | 1 | 1 | 1 | 1 | |

`1` = đúng, `0` = sai, để trống = chưa chấm. Chấm bằng trang HTML hay bằng Excel đều được; lệnh
`spotcheck score` đọc file này. Một hội chứng **đạt** khi cả 4 cột = 1.

### 2.3 `syndromes.csv`: mọi hội chứng một dòng (lọc trong Excel)

`code, title, group, part, pdf_start, pdf_end, printed_start, printed_end, n_sections, words,`
một cột **mỗi loại mục** (`definition`, `site`, `symptom`, … ✓ hoặc trống), `iasp_codes`, `flags`.
Dùng để lọc nhanh: hội chứng thiếu `definition`, có cờ, quá ngắn / quá dài…

## 3. Chọn mẫu: thế nào là "ngẫu nhiên" cho công bằng

- **Ngẫu nhiên có hạt giống cố định** (`--seed`, mặc định 2026): chạy lại → đúng 10 hội chứng đó
  (để bạn và tôi xem cùng một mẫu; đổi seed để lấy mẫu mới).
- **Rải đều theo nhóm chữ cái** theo tỉ lệ số hội chứng, tránh 10 cái rơi hết vào một chương.
  Số hội chứng thật: A 41 · B 67 · D 40 · E 34 · F 87 · G 48 · H 18 (nhóm C chỉ có đoạn giới thiệu,
  0 hội chứng) → 10 mẫu chia ≈ A 1 · B 2 · D 1 · E 1 · F 3 · G 1 · H 1.
- **Không chọn lọc theo cờ**: A9 đo chất lượng trung bình nên mẫu phải ngẫu nhiên thật. Các hội chứng
  **có cờ** (`missing_syndrome_title`, `empty`, `no_code` - 8 cái) hiện ở **phần riêng cuối trang**
  ("Để bạn xem thêm"), **không tính** vào A9.
- Chọn thêm theo ý bạn: `--codes XI-1,XXIV-6` (cũng không tính vào A9).

## 4. Chấm điểm `spotcheck score`

- Đọc `review.csv` (chấp nhận dấu phân cách `,` hoặc `;` - Excel tiếng Việt hay lưu bằng `;`).
- Còn ô trống → báo hội chứng nào chưa chấm, không tính điểm.
- In: `A9: 9/10 đạt (ngưỡng ≥ 9) → ĐẠT`, kèm danh sách hội chứng sai và ghi chú của bạn →
  `spotcheck/score.md`.
- **Chống chấm nhầm bản cũ:** trang soát ghi lại sha256 của `nodes.jsonl` lúc sinh; nếu cây đã được
  chạy lại sau đó, `score` cảnh báo "phiếu chấm thuộc bản cây cũ".

## 5. Thiết kế code

| Thành phần | Nội dung |
|---|---|
| `evaluation/spotcheck.py` (mới, dùng chung mọi sách) | chọn mẫu (seed + rải nhóm), gom dữ liệu 1 hội chứng (nút con, dòng, vùng tô theo trang), bảng hội chứng, đọc / chấm phiếu |
| `evaluation/spotcheck_page.py` (mới) | sinh `index.html` (escape mọi chữ của sách), ảnh trang JPEG 120 dpi |
| `cli/p2.py` | lệnh `p2 spotcheck` (`--n`, `--seed`, `--codes`, `--dpi`) và `p2 spotcheck score` |
| `BookRules.review_units` (luật mới, mặc định = nút `disease`) | IASP thêm GROUP-hội chứng (`GROUP XVI … (XVI-1)`) |
| `p2.spotcheck` trong cấu hình | `n`, `seed`, `dpi`, tên đơn vị (`syndromes` cho IASP, `diseases` mặc định) |

**Vùng tô:** mỗi block có danh sách dòng (`line_ids`); mỗi dòng có tọa độ trên trang PDF (P1) →
quy đổi theo dpi thành ô vuông trên ảnh. Không sửa ảnh; vùng tô là lớp CSS phủ lên.

**Không đụng tới cây:** I5 chỉ ĐỌC `nodes.jsonl`, `blocks.jsonl`, `lines.jsonl`, PDF → không đổi
dữ liệu P1/P2, không đổi kết quả I1-I4, sách mẫu không đổi. Chạy được cho cả sách mẫu (thử luôn
trên `book01` để chắc công cụ dùng chung được).

## 6. Kiểm tra (xong khi)

| # | Kiểm | Cách |
|---|---|---|
| S1 | Chọn mẫu ổn định, rải đều | cùng seed → cùng 10 hội chứng; mỗi nhóm có hội chứng được ≥ 1 mẫu (7 nhóm, 10 mẫu); không trùng; không chọn hội chứng có cờ |
| S2 | **Vùng tô đúng chỗ** | tôi tự sinh ảnh có vẽ khung (PyMuPDF) cho 3 hội chứng, **tự xem ảnh** để chắc khung trùng chữ (lưu vào `samples/P2R/I5/overlay_check_*.png`); test: mọi ô nằm trong khổ trang |
| S3 | Không mất nội dung | mọi block của hội chứng xuất hiện bên phải đúng 1 lần, theo thứ tự đọc |
| S4 | An toàn HTML | chữ có `<`, `&`, `"` hiển thị đúng, không vỡ trang (test) |
| S5 | Chấm điểm | phiếu đủ / thiếu ô / sai giá trị / `;` của Excel / bản cây cũ → đúng kết quả + thông báo (test) |
| S6 | Dùng chung | chạy được trên sách mẫu `book01` (test) |
| S7 | Không đổi dữ liệu | kiểm byte sách mẫu như I3-I4; IASP `nodes.jsonl` sha không đổi |
| - | Đột biến | phá các luật mới → test phải bắt được (như I3, I4) |

## 7. Mẫu + báo cáo

`samples/P2R/I5/`: bộ spotcheck thật trên cả Part II (`index.html` + `pages/*.jpg`, ~3 MB),
`review.csv` (trống, để bạn chấm ở I6), `syndromes.csv`, `overlay_check_*.png`, `mutations.txt`.
Báo cáo `docs/phases/P2R/I5_report.md`, kèm hướng dẫn soát 1 trang (nhìn gì, chấm thế nào).

## 8. Ngoài phạm vi I5

Chấm thật 10 hội chứng (bạn làm ở I6). Sửa luật nếu bạn phát hiện lỗi (I6). Không dùng AI. $0.

## 9. Cần bạn quyết (mặc định của tôi in đậm)

1. **Commit bộ spotcheck mẫu (~3 MB ảnh trang sách) vào `samples/P2R/I5/`?** **Có** (repo private,
   bạn đã cho phép commit nội dung trích từ sách) · hay chỉ commit HTML + CSV, ảnh để ở `data/`.
2. **Cỡ mẫu A9:** **10 hội chứng** (như plan P2R) · hay 20 để chắc hơn (~35-40 phút soát).
3. **Ghi kết quả chấm:** **cả hai** - ô chấm trong HTML (tải ra CSV) và sửa trực tiếp `review.csv`
   bằng Excel · hay chỉ Excel (đơn giản hơn, bỏ phần ô chấm trong HTML).

## 10. Thay đổi khi triển khai (2026-10-26)

- Cột loại mục trong bảng hội chứng đặt tên `has_<loại>` (cột loại `code` trùng tên cột mã).
- CSS/JS của trang soát để ở file riêng `evaluation/assets/` (dễ đọc, kiểm cú pháp được).
- Bên phải hiện lại ký hiệu danh sách `1.` / `-` (lưu riêng khỏi chữ ở P1).
- Kết quả: [I5_report.md](I5_report.md).
