# P1.5 - áp quyết định duyệt (pilot sách mẫu)

⚠️ Người duyệt ở đây là **auto-truth (sách mẫu)** - quyết định điền từ đáp án để kiểm chứng đường đi. Sách thật cần người có chuyên môn.

Hàng đợi: 2 mục · đã áp: 2 · stale: không · còn chờ: 0

| ưu tiên | trang in | ngữ cảnh | hiện tại | gợi ý LLM | quyết định | kết quả |
|---|---|---|---|---|---|---|
| 1-SỐ LIỆU | 4 | Paracetamol «5OO» mg mỗi lần, không quá 3 g mỗi … | `5OO` | `500` | accept (auto-truth (sách mẫu)) | `500` |
| 1-SỐ LIỆU | 6 | «l» g | `l` | `1` | accept (auto-truth (sách mẫu)) | `1` |

## Văn bản sau duyệt

- **list_item** (trang in 4): trước `Paracetamol 5OO mg mỗi lần, không quá 3 g mỗi ngày.` → sau `Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày.`
- **table** (trang in 6): trước `Amoxicilin | l g | 2 | 14 ngày` → sau `Amoxicilin | 1 g | 2 | 14 ngày`

## Chỉ tiêu sau duyệt

```
✓ G5_wer: words=1004, before=0.0408, after=0.003, target=0.01
✓ G8_numbers: 
    dose_errors: {'error': 'Paracetamol 500 mg → Paracetamol 5OO mg', 'kept': False, 'flagged': False, 'fixed_by_review': True}
    dose_errors: {'error': '1 g → l g', 'kept': False, 'flagged': False, 'fixed_by_review': True}
```
