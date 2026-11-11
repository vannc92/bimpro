---
title: Quy định đặt tên tập tin
short: Quy định đặt tên tập tin
summary: Diễn giải chi tiết các trường thông tin của quy ước đặt tên và bảng mã các trường
kind: appendix
---
# muc-dich | MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG
Phụ lục này là bộ phận không tách rời của Kế hoạch thực hiện BIM (mã hiệu {{ code('bep') }}), quy định cách đặt tên tập tin mô hình, bản vẽ, tài liệu và báo cáo được tạo lập, trao đổi trên môi trường dữ liệu chung của dự án {{ p.general.name }}.

# nguyen-tac | NGUYÊN TẮC CHUNG
- Chỉ sử dụng các ký tự a-z, A-Z, chữ số 0-9, dấu gạch ngang (-) và dấu gạch dưới (_); không sử dụng dấu cách, chữ có dấu tiếng Việt và ký tự đặc biệt;
- Độ dài toàn bộ đường dẫn không vượt quá 256 ký tự;
- Các trường thông tin chính phân cách bằng dấu gạch ngang "-"; nội dung chính và phụ trong một trường phân cách bằng dấu gạch dưới "_";
- Trường không áp dụng điền "ZZ"; các mã viết in hoa;
- Trạng thái phù hợp (suitability) của tài liệu được quản lý bằng thuộc tính trên CDE, không đưa vào tên tập tin.

# cau-truc | CẤU TRÚC TÊN TẬP TIN
Tên tập tin của dự án có cấu trúc như sau:

> {{ p.naming.syntax }}

[Bảng#truong|6,24,10,10,20,30] Các trường thông tin của tên tập tin
{{ tbl(['TT', 'Trường thông tin', 'Số ký tự', 'Bắt buộc', 'Ví dụ', 'Diễn giải'], rows(p.naming.fields, '#', 'name', 'length', 'required', 'example?', 'note?')) }}

{% set ns = namespace(names=[]) %}
{% for c in p.naming.codes %}{% if c.table not in ns.names %}{% set ns.names = ns.names + [c.table] %}{% endif %}{% endfor %}
{% for name in ns.names %}
[Bảng] Bảng mã trường {{ name }}
{% set r = [] %}{% for c in p.naming.codes if c.table == name %}{% set _ = r.append([c.code, c.meaning, c.note]) %}{% endfor %}
{{ tbl(['Mã', 'Diễn giải', 'Ghi chú'], r) }}

{% endfor %}

# phien-ban | PHIÊN BẢN VÀ MÃ TRẠNG THÁI
Phiên bản tài liệu được quy ước như sau:

- Phiên bản trình duyệt, chưa được Chủ đầu tư chấp thuận: ký hiệu bằng chữ cái A, B, C…;
- Ấn bản chính thức sau khi được Chủ đầu tư chấp thuận: ký hiệu Ab1, Ab2…;
- Ký hiệu phiên bản được ghi thống nhất trên bìa, cuối trang và bảng kiểm soát phiên bản của tài liệu.

Mã trạng thái của thông tin trên CDE như sau:

[Bảng#trang-thai|10,22,18,50] Mã trạng thái thông tin trên CDE
{{ tbl(['Mã', 'Tên', 'Vùng CDE', 'Ý nghĩa'], rows(p.cde.status_codes, 'code', 'name', 'zone', 'meaning')) }}

# vi-du | VÍ DỤ ĐẶT TÊN
[Bảng#vi-du|6,44,50] Ví dụ đặt tên tập tin
{{ tbl(['TT', 'Tên tập tin', 'Diễn giải'], rows(p.naming.examples, '#', 'name', 'meaning')) }}

# tuan-thu | KIỂM SOÁT VIỆC TUÂN THỦ
- Chuyên gia quản lý dữ liệu kiểm tra tên tập tin khi tải lên CDE; tập tin đặt sai quy ước bị từ chối hoặc yêu cầu đổi tên trước khi chia sẻ;
- Điều phối BIM cấp số thứ tự cho mô hình và tài liệu mới; số thứ tự đã cấp không được dùng lại;
- Việc bổ sung mã mới vào các bảng mã do Quản lý BIM quyết định và cập nhật vào phụ lục này.
