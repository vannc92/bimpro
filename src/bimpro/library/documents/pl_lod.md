---
title: Ma trận LOD và bộ tham số thông tin (LOI)
short: Ma trận LOD và LOI
summary: Định nghĩa mức độ phát triển thông tin, ma trận LOD theo cấu kiện và bộ tham số thông tin bắt buộc
kind: appendix
orientation: landscape
---
# muc-dich | MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG
Phụ lục này là bộ phận không tách rời của Kế hoạch thực hiện BIM (mã hiệu {{ code('bep') }}), quy định mức độ phát triển thông tin (LOD) và thông tin phi hình học (LOI) của các đối tượng mô hình trong giai đoạn {{ stage.phrase }} của dự án {{ p.general.name }}. Mức LOD chung của giai đoạn là LOD {{ LOD }}.

# dinh-nghia | ĐỊNH NGHĨA CÁC MỨC LOD
[Bảng#dinh-nghia|10,45,45] Định nghĩa các mức độ phát triển thông tin
| Mức | Hình học | Thông tin phi hình học |
|---|---|---|
| LOD 100 | Khối bao, ký hiệu thể hiện sự tồn tại của đối tượng | Thông tin khái quát |
| LOD 200 | Hình dạng, kích thước, số lượng và vị trí gần đúng | Thông tin chủ yếu về chủng loại, vật liệu |
| LOD 300 | Hình dạng, kích thước, số lượng, vị trí và hướng chính xác theo thiết kế | Thông tin đủ để lập bản vẽ thiết kế |
| LOD 350 | Như LOD 300, thể hiện thêm giao diện và liên kết với các cấu kiện, hệ thống liên quan | Thông tin đủ để phối hợp và triển khai thi công |
| LOD 400 | Chi tiết chế tạo, lắp đặt | Thông tin đủ để gia công, chế tạo |
| LOD 500 | Đúng hiện trạng thi công | Thông tin hoàn công phục vụ vận hành |

Các mức LOD được hiểu theo Quyết định số 348/QĐ-BXD ngày 02/4/2021 của Bộ Xây dựng.

# ma-tran | MA TRẬN LOD THEO CẤU KIỆN
[Bảng#ma-tran|6,34,10,50] Ma trận LOD và thông tin phi hình học theo cấu kiện
{{ tbl(['TT', 'Tên cấu kiện', 'LOD', 'Thông tin phi hình học cần đính kèm'], grows(p.models.lod, 'group', '#', 'element', 'lod', 'info')) }}

# tham-so | BỘ THAM SỐ THÔNG TIN CHUNG (LOI)
Mọi đối tượng mô hình phải có các tham số sau, nhập bằng tham số dùng chung (shared parameter) của dự án:

[Bảng#tham-so|22,14,12,22,30] Bộ tham số thông tin bắt buộc
{{ tbl(['Tên tham số', 'Kiểu dữ liệu', 'Instance/Type', 'Áp dụng cho', 'Mô tả'], rows(p.models.params, 'name', 'kind', 'scope', 'applies', 'description')) }}

- Tệp tham số dùng chung được Điều phối BIM phát hành tại thư mục tài nguyên trên CDE; các bộ môn không tự thêm, sửa tham số;
- Khi xuất IFC, các tham số được ánh xạ sang bộ thuộc tính (property set) theo cấu hình xuất của dự án;
- Việc bổ sung tham số mới do Quản lý BIM quyết định và cập nhật vào phụ lục này.
