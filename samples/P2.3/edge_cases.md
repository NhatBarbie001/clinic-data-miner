# Tình huống ngoài sách mẫu (block tự dựng, dựng thật bằng `build_tree`)

## Có lời nói đầu trước chương đầu tiên → nút `front` (Phần đầu)

Đầu vào (theo thứ tự đọc): `Sách này dành cho sinh viên y khoa.` → `CHƯƠNG 1. HÔ HẤP` → `Giới thiệu chương.` → `HEN PHẾ QUẢN` → `1. ĐẠI CƯƠNG` → `…`

```
Sách thử · tr.in 1
├─ Phần đầu · 1 đoạn văn · tr.in 1
└─ Chương 1. Hô hấp · 1 đoạn văn · tr.in 1
   └─ Hen phế quản · tr.in 1
      └─ 1. Đại cương · 1 đoạn văn · tr.in 1
```

## Sách không chia chương → bệnh là con trực tiếp của sách

Đầu vào (theo thứ tự đọc): `HEN PHẾ QUẢN` → `1. ĐẠI CƯƠNG` → `…` → `VIÊM PHỔI` → `1. ĐẠI CƯƠNG` → `…`

```
Sách thử · tr.in 1
├─ Hen phế quản · tr.in 1
│  └─ 1. Đại cương · 1 đoạn văn · tr.in 1
└─ Viêm phổi · tr.in 1
   └─ 1. Đại cương · 1 đoạn văn · tr.in 1
```

## Mục con thiếu mục cha (`2.1.` ngay dưới bệnh) → cờ `orphan_subsection`

Đầu vào (theo thứ tự đọc): `SỎI THẬN` → `2.1. Thể lâm sàng` → `…`

```
Sách thử · tr.in 1
└─ Sỏi thận · tr.in 1
   └─ 2.1. Thể lâm sàng · 1 đoạn văn · tr.in 1 ⚑ orphan_subsection
```

- ⚠ '2.1. Thể lâm sàng' (trang PDF 4) không có nút cha đúng cấp - gắn tạm vào 'Sỏi thận'.

## Tiêu đề `other` (LƯU Ý) → nội dung của mục đang mở; mục rỗng → `empty`; tên mục lặp → `duplicate_path`

Đầu vào (theo thứ tự đọc): `GOUT` → `1. ĐIỀU TRỊ` → `Allopurinol…` → `LƯU Ý` → `Không tự ý dùng thuốc.` → `2. PHÒNG BỆNH` → `3. ĐIỀU TRỊ` → `…`

```
Sách thử · tr.in 1
└─ Gout · tr.in 1
   ├─ 1. Điều trị · 2 đoạn văn, 1 tiêu đề khác · tr.in 1 ⚑ other_heading
   ├─ 2. Phòng bệnh · tr.in 1 ⚑ empty
   └─ 3. Điều trị · 1 gạch đầu dòng · tr.in 1 ⚑ duplicate_path
```
