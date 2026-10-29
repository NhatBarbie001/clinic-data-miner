# Báo cáo P2R · I5: công cụ soát tay (spotcheck) + bảng hội chứng

Ngày: 2026-10-26 · Plan: [I5_plan.md](I5_plan.md) (đã duyệt, mặc định mục 9: commit mẫu có ảnh,
10 hội chứng, chấm bằng cả HTML lẫn Excel)

## 1. Tóm tắt

```
uv run dm --book iasp p2 spotcheck          # ~7 giây: 10 hội chứng ngẫu nhiên + 8 có cờ, 22 trang ảnh
uv run dm --book iasp p2 spotcheck score    # đọc phiếu chấm → A9 đạt / chưa đạt
```

| Đầu ra | Nội dung |
|---|---|
| `p2_tree/spotcheck/index.html` | trang soát: ảnh trang PDF (vùng chữ tô màu theo loại mục) ↔ nội dung đã tách, 4 ô chấm |
| `p2_tree/spotcheck/review.csv` | phiếu chấm 10 dòng (sửa được bằng Excel) |
| `p2_tree/syndromes.csv` | 335 hội chứng, mỗi dòng: mã, tên, nhóm, trang, số mục, số từ, `has_<loại mục>`, mã IASP, cờ |
| `p2_tree/spotcheck/score.md` | kết quả A9 sau khi chấm |

Ảnh chụp trang soát thật (Edge, không cần mạng): bên trái ảnh trang PDF 60 với vùng của
"Polymyalgia Rheumatica (1-8)" tô màu theo mục (tên viền đỏ), bên phải 15 mục kèm nhãn loại mục.

Chi phí $0. Công cụ **chỉ đọc**: `nodes.jsonl` của IASP giữ nguyên sha256 (`7329347590c4…`), sách
mẫu không đổi.

## 2. Hướng dẫn soát (cho bạn, ở I6)

1. Mở `samples/P2R/I5/spotcheck/index.html` (hoặc `data/books/iasp/p2_tree/spotcheck/index.html`)
   bằng trình duyệt.
2. Với mỗi hội chứng, nhìn **bên trái** trước:
   - chữ của hội chứng này mà **không được tô** → bị sót / bị gán cho nút khác;
   - vùng tô **lan sang** hội chứng khác → sai ranh giới;
   - hai màu xen kẽ lộn xộn trong một đoạn → nghi lẫn cột.
3. Nhìn **bên phải**: tên đúng chưa, đủ các mục như trên trang chưa, nội dung mỗi mục có đúng là
   của mục đó (rê chuột lên mục → vùng chữ của nó nháy viền bên trái).
4. Tích đủ 4 ô (Đúng tên · Đúng ranh giới · Đủ mục, đúng nội dung · Không lẫn cột) nếu đúng; sai
   thì để trống ô sai, bấm **Có lỗi**, ghi chú ngắn ("3 dòng cuối Relief sang hội chứng sau").
   Kết quả lưu ngay trong trình duyệt.
5. Bấm **Tải phiếu chấm (CSV)** →
   `uv run dm --book iasp p2 spotcheck score --file <file vừa tải>`.
   (Hoặc mở `review.csv` bằng Excel, điền 1 = đúng / 0 = sai, lưu, chạy `... spotcheck score`.)

A9 **đạt** khi ≥ 9/10 hội chứng đúng cả 4 tiêu chí. Phần cuối trang ("Để bạn xem thêm") là 8
hội chứng có cờ - xem cho biết, **không tính** điểm.

## 3. Mẫu ngẫu nhiên (seed 2026)

Chia theo tỉ lệ số hội chứng mỗi nhóm chữ cái (nhóm C không có hội chứng):

| Nhóm | Số hội chứng | Lượt | Được chọn |
|---|---|---|---|
| A | 41 | 1 | I-8 Polymyalgia Rheumatica |
| B | 67 | 2 | V-5 Mixed Headache · VIII-3 Tuberculosis of Larynx |
| D | 40 | 1 | X-9 Thoracic Discogenic Pain |
| E | 34 | 1 | XI-7 Bicipital Tendinitis |
| F | 87 | 3 | XIX-7 Duodenal Ulcer with Chest Pain · XXV-2 Rectal, Perineal, and Genital Pain of Psychological Origin · XXV-5 Ulcer of Anus or Rectum |
| G | 48 | 1 | XXVII-10 Sacroiliac Joint Pain |
| H | 18 | 1 | XXXII-3 Osteoarthritis of the Hip |

## 4. Kiểm chứng

| # | Kiểm | Kết quả |
|---|---|---|
| S1 | Chọn mẫu ổn định, rải đều, bỏ hội chứng có cờ | test: cùng seed → cùng mẫu; khác seed → khác; tỉ lệ đúng phân bố IASP thật |
| S2 | **Vùng tô trùng chữ** | tôi vẽ khung bằng đúng tọa độ của trang soát lên PDF rồi **tự xem ảnh** 5 trang (I-8, V-5, VIII-3): khung trùng khít từng dòng, dừng đúng ở tên hội chứng kế tiếp → `samples/P2R/I5/overlay_check_*.png` |
| S3 | Không mất nội dung | test: mọi block của hội chứng hiện đúng 1 lần, theo thứ tự đọc |
| S4 | An toàn HTML | test: chữ `<b>&`, `</script>` hiển thị đúng; dữ liệu nhúng không đóng được thẻ `<script>` |
| S5 | Chấm điểm | test: 9/10 đạt, 8/10 chưa, ô trống, giá trị lạ, phiếu của mẫu khác, file Excel dùng `;`, phiếu thuộc bản cây cũ |
| S6 | Dùng chung | test: chạy đủ `spotcheck` + `score` trên sách mẫu `book01` |
| S7 | Không đổi dữ liệu | `nodes.jsonl` IASP cùng sha trước/sau; sách mẫu 12/12 (như I3-I4) |

- Chạy lại `spotcheck` khi `review.csv` **đã có điểm** → giữ nguyên phiếu, chỉ báo (không mất
  công chấm).
- Test: **661 pass** (11 test mới: `tests/unit/test_spotcheck.py`, `tests/books/test_iasp_i5.py`).
  Đột biến **12/12** bị bắt (lần đầu 1 sống: chặn `</script>` trong dữ liệu → đã thêm test).
  ruff + mypy sạch; cú pháp JS kiểm bằng Node; trang mở thử bằng Edge (ảnh chụp ở trên).

## 5. Công cụ đã bắt được lỗi thật (để sửa ở I6)

Ngay khi tự xem trang soát, tôi thấy 2 lỗi P1 mà các phép đếm của I1-I4 không thấy:

| Lỗi | Ví dụ | Số chỗ | Nguyên nhân |
|---|---|---|---|
| Mục danh sách đánh số bị tách dòng sau | `1. Symmetrical proximal limb myalgia and severe stiff-` ‖ `ness.` (Polymyalgia Rheumatica, PDF 61) | 11 / 110 mục danh sách | sách không thụt dòng sau của mục danh sách → P1 coi là đoạn mới |
| Tên mục vắt qua trang bị tách đôi | `Summary of Essential Features and Diagnostic` ‖ `Criteria` (Tuberculosis of Larynx, PDF 115) | 1 | luật nối tiêu đề chỉ nối trong cùng trang |

Cả hai không mất chữ, không sai ranh giới hội chứng, nhưng làm nội dung một mục bị vụn. Sẽ sửa ở
I6 cùng các lỗi bạn tìm thấy khi soát.

## 6. Thay đổi code

| Thành phần | Nội dung |
|---|---|
| `evaluation/spotcheck.py` (mới) | chọn mẫu, gom dữ liệu 1 hội chứng (nút, văn bản, ô chữ theo % khổ trang), bảng hội chứng, đọc / chấm phiếu |
| `evaluation/spotcheck_page.py` + `evaluation/assets/spotcheck.{css,js}` (mới) | trang HTML, ảnh trang JPEG 120 dpi |
| `cli/p2.py` | `p2 spotcheck` (`--n --seed --codes --dpi`), `p2 spotcheck score` (`--file`) |
| `BookRules.review_units` (mặc định: nút `disease`) | IASP: thêm GROUP-hội chứng (XVI-1) |
| `p2.spotcheck` (cấu hình) | `n=10, seed=2026, dpi=120, min_pass=0.9, unit_name` (IASP: `syndromes`) |

## 7. Mẫu (`samples/P2R/I5/`)

`spotcheck/` (index.html + 22 ảnh trang, ~4 MB) · `syndromes.csv` · `overlay_check_*.png` ·
`spotcheck_run.txt` · `mutations.txt`.

## 8. Việc tiếp: I6

1. **Bạn soát** 10 hội chứng bằng trang trên (~15-20 phút), gửi phiếu / chạy `spotcheck score`.
2. Tôi sửa 2 lỗi ở mục 5 + lỗi bạn tìm thấy, chạy lại cả Part II, kiểm lại A1-A9.
3. Báo cáo cuối P2R (`docs/phases/P2R/report.md`) bằng ngôn ngữ thường, có ví dụ trước/sau.
