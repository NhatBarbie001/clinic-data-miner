# P1.4 - từng thay đổi của LLM sau guard (pilot sách mẫu)

Chấp nhận = áp dụng vào văn bản. Từ chối = giữ nguyên bản gốc (kèm luật). ⚠️ = số liệu nghi sai: KHÔNG tự sửa, chuyển người duyệt kèm gợi ý.


## Trang PDF 4 (trang in 1)

| block | trước | sau | kết quả | luật | ghi chú |
|---|---|---|---|---|---|
| paragraph | `la` | `là` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| paragraph | `viêrn` | `viêm` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (char_confusion) |
| heading | `NGUYEN` | `NGUYÊN` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| paragraph | `1à` | `là` | ✅ chấp nhận | digit_letter | ✓ sửa lỗi đã cài (char_confusion) |
| list_item | `truyen:` | `truyền:` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `tbuốc` | `thuốc` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (char_confusion) |
| list_item | `kbớp` | `khớp` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (char_confusion) |

## Trang PDF 5 (trang in 2)

| block | trước | sau | kết quả | luật | ghi chú |
|---|---|---|---|---|---|
| list_item | `duoi` | `dưới` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `vá` | `và` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (wrong_tone) |
| list_item | `rnỗi` | `mỗi` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (char_confusion) |
| list_item | `dien.` | `diễn.` | ✅ chấp nhận | ok | sửa thêm ngoài lỗi đã cài - xem mục cuối |
| list_item | `van` | `vận` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `bạn` | `hạn` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (char_confusion) |

## Trang PDF 6 (trang in 3)

| block | trước | sau | kết quả | luật | ghi chú |
|---|---|---|---|---|---|
| heading | `DAI` | `ĐẠI` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| paragraph | `phảnứng` | `phản ứng` | ✅ chấp nhận | split_merge | ✓ sửa lỗi đã cài (merge_words) |
| list_item | `trong` | `trọng` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `lau,` | `lâu,` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `Cung` | `Cứng` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `co` | `có` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `đắc` | `đặc` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (wrong_tone) |
| paragraph | `kem` | `kèm` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| paragraph | `sang` | `sáng` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| paragraph | `dong.` | `động.` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |

## Trang PDF 7 (trang in 4)

| block | trước | sau | kết quả | luật | ghi chú |
|---|---|---|---|---|---|
| list_item | `can,` | `cân,` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `5OO` | `500` | ⚠️ từ chối → duyệt | G-num | gợi ý `500` |
| list_item | `dot` | `đợt` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |

## Trang PDF 8 (trang in 5)

| block | trước | sau | kết quả | luật | ghi chú |
|---|---|---|---|---|---|
| paragraph | `boặc` | `hoặc` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (char_confusion) |
| paragraph | `tai` | `tái` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| heading | `BIEN` | `BIẾN` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `tieu` | `tiêu` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| paragraph | `hoac` | `hoặc` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |

## Trang PDF 9 (trang in 6)

| block | trước | sau | kết quả | luật | ghi chú |
|---|---|---|---|---|---|
| heading | `TRI` | `TRỊ` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `ngay.` | `ngày.` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| table ô r0c0 | `Thuộc` | `Thuốc` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (wrong_tone) |
| table ô r1c3 | `ngảy` | `ngày` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (wrong_tone) |
| table ô r2c1 | `l` | `1` | ⚠️ từ chối → duyệt | G-num | gợi ý `1` |
| list_item | `khong` | `không` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (drop_diacritics) |
| list_item | `kẻo` | `kéo` | ✅ chấp nhận | ok | ✓ sửa lỗi đã cài (wrong_tone) |

## Lỗi đã cài CHƯA được sửa

- tr.5 drop_diacritics: điển → dien
- tr.6 drop_diacritics: CHỨNG → CHUNG
- tr.9 wrong_tone: đồ → độ

Cả 3 đều là lỗi tạo ra **từ có nghĩa** (`dien`, `CHUNG`, `độ`) - LLM giữ nguyên theo đúng chỉ dẫn "không chắc thì giữ nguyên".

## Sửa NGOÀI các lỗi đã cài (= sửa sai: `kinh dien` → `kinh diễn`, đúng phải là `kinh điển`)

- `dien.` → `diễn.`
