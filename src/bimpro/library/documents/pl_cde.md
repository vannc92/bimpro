---
title: Cấu trúc thư mục và ma trận phân quyền CDE
short: Cấu trúc thư mục và phân quyền CDE
summary: Cây thư mục dự án, trạng thái CDE theo thư mục và quyền truy cập theo vai trò
kind: appendix
---
# muc-dich | MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG
Phụ lục này là bộ phận không tách rời của Kế hoạch thực hiện BIM (mã hiệu {{ code('bep') }}), quy định cấu trúc thư mục, trạng thái thông tin và quyền truy cập trên môi trường dữ liệu chung {{ CDE }} của dự án {{ p.general.name }}.

# nguyen-tac | NGUYÊN TẮC TỔ CHỨC THƯ MỤC
- Thư mục gốc của dự án gồm bốn vùng trạng thái theo ISO 19650: WIP, SHARED, PUBLISHED và ARCHIVED; tệp kế thừa trạng thái của thư mục chứa nó;
- Tên thư mục có dạng <STT 2 chữ số>_<Tên viết tắt>, không dấu, không khoảng trắng;
- Cấu trúc thư mục không quá ba cấp dưới thư mục gốc;
- Vùng WIP được tổ chức theo nhóm thực hiện; vùng SHARED và PUBLISHED theo loại thông tin; vùng ARCHIVED theo mốc chuyển giao;
- Mã trạng thái phù hợp của tệp được ghi trong thuộc tính của tệp trên CDE, không đưa vào tên tệp.

# cay-thu-muc | CÂY THƯ MỤC DỰ ÁN
[Bảng#cay|18,24,40,18] Cây thư mục dự án trên CDE
{{ tbl(['Thư mục cấp 1', 'Thư mục cấp 2', 'Nội dung lưu trữ', 'Mã phù hợp'], rows(p.cde.folders, 'level1', 'level2', 'content', 'suit')) }}

# phan-quyen | VAI TRÒ VÀ CẤP QUYỀN
[Bảng#cap-quyen|20,12,68] Các cấp quyền truy cập
| Cấp quyền | Ký hiệu | Phạm vi thao tác |
|---|---|---|
| Không có quyền | – | Không nhìn thấy thư mục |
| Xem | V | Xem tệp, mô hình trực tuyến |
| Tải xuống | DL | Xem và tải tệp xuống |
| Bình luận | CM | Tải xuống, bình luận, đánh dấu trên tệp và mô hình |
| Tải lên | UP | Bình luận và tải tệp, phiên bản mới lên |
| Chỉnh sửa | ED | Tải lên, sửa thuộc tính, di chuyển tệp |
| Xóa | DE | Chỉnh sửa và xóa tệp |
| Quản trị | AD | Toàn quyền, kể cả phân quyền thư mục |

Quyền được cấp theo vai trò; quyền cấp cho cá nhân được ưu tiên hơn quyền theo vai trò và theo đơn vị; thư mục con kế thừa quyền của thư mục cha trừ khi được thiết lập riêng.

{% set roles = split(p.cde.perm_roles) %}
{% set r = [] %}
{% for x in p.cde.perms %}{% set v = split(x.values) %}{% set _ = r.append([x.folder] + (v + [''] * roles|length)[:roles|length]) %}{% endfor %}
[Bảng#ma-tran-quyen] Ma trận phân quyền theo vai trò
{{ tbl(['Thư mục'] + roles, r) }}

# van-hanh | QUY ĐỊNH VẬN HÀNH
[Bảng#chuyen-trang-thai|20,34,22,24] Quy định chuyển trạng thái thông tin
{{ tbl(['Chuyển trạng thái', 'Điều kiện', 'Người thực hiện', 'Chức năng CDE'], rows(p.cde.transitions, 'change', 'condition', 'by', 'function')) }}

- Tài khoản được cấp theo đề nghị của Quản lý BIM, sau khi người dùng đã được hướng dẫn sử dụng CDE; quyền truy cập được thu hồi ngay khi nhân sự rời dự án;
- Chuyên gia quản lý dữ liệu rà soát định kỳ danh sách tài khoản, quyền truy cập và nhật ký hoạt động; sai lệch được báo cáo Quản lý BIM để xử lý.
