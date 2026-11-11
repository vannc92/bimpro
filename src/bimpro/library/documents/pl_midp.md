---
title: Kế hoạch chuyển giao thông tin (TIDP/MIDP)
short: Kế hoạch chuyển giao thông tin
summary: Kế hoạch chuyển giao của từng nhóm thực hiện và kế hoạch tổng thể của dự án
kind: appendix
orientation: landscape
---
# muc-dich | MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG
Phụ lục này là bộ phận không tách rời của Kế hoạch thực hiện BIM (mã hiệu {{ code('bep') }}), xác định các sản phẩm thông tin, bên chủ trì, định dạng và thời điểm chuyển giao trong giai đoạn {{ stage.phrase }} của dự án {{ p.general.name }}. Kế hoạch được Quản lý BIM cập nhật khi có thay đổi về tiến độ hoặc danh mục sản phẩm.

# dot | CÁC ĐỢT CHUYỂN GIAO
[Bảng#dot|10,60,30] Các đợt chuyển giao thông tin
{{ tbl(['TT', 'Đợt chuyển giao', 'Ngày chuyển giao'], rows(p.delivery.rounds, '#', 'name', 'date')) }}

# midp | KẾ HOẠCH CHUYỂN GIAO THÔNG TIN TỔNG THỂ (MIDP)
{% set rn = p.delivery.rounds|map(attribute='name')|list %}
{% set r = [] %}{% set ns = namespace(g=none, i=0) %}
{% for m in p.delivery.midp %}
{% if m.group != ns.g %}{% set _ = r.append(('group', m.group)) %}{% set ns.g = m.group %}{% endif %}
{% set ns.i = ns.i + 1 %}
{% set d = split(m.dates) %}
{% set _ = r.append([ns.i|string, m.file, m.description, m.native, m.exchange, m.lead] + (d + [''] * rn|length)[:rn|length]) %}
{% endfor %}
[Bảng#midp] Kế hoạch chuyển giao thông tin tổng thể (MIDP)
{{ tbl(['TT', 'Tên tập tin', 'Mô tả', 'Định dạng gốc', 'Định dạng trao đổi', 'Bên chủ trì'] + rn, r) }}

# tidp | KẾ HOẠCH CHUYỂN GIAO THÔNG TIN NHIỆM VỤ (TIDP)
[Bảng#tidp] Kế hoạch chuyển giao thông tin nhiệm vụ (TIDP)
{{ tbl(['TT', 'Nhiệm vụ', 'Sản phẩm (mã hiệu)', 'Người thực hiện', 'Đầu vào cần có', 'Bắt đầu', 'Hoàn thành', 'Ghi chú'], grows(p.delivery.tidp, 'team', '#', 'task', 'product', 'person', 'inputs?', 'start', 'finish', 'note?')) }}

# cap-nhat | CẬP NHẬT KẾ HOẠCH
- Nhóm thực hiện cập nhật TIDP của mình khi có thay đổi và thông báo cho Điều phối BIM qua CDE;
- Quản lý BIM tổng hợp các TIDP thành MIDP, rà soát sự phù hợp với các mốc của dự án và phát hành lại phụ lục này;
- Các sản phẩm trong MIDP phải có mã hiệu theo {{ pl('pl_naming') }} và thuộc danh mục mô hình tại Kế hoạch thực hiện BIM.
