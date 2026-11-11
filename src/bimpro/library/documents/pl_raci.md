---
title: Ma trận vai trò và trách nhiệm (RACI)
short: Ma trận vai trò và trách nhiệm (RACI)
summary: Phân định trách nhiệm thực hiện – phê duyệt – tham vấn – thông báo cho từng nhiệm vụ BIM
kind: appendix
orientation: landscape
---
# muc-dich | MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG
Phụ lục này là bộ phận không tách rời của Kế hoạch thực hiện BIM (mã hiệu {{ code('bep') }}), quy định chi tiết vai trò và trách nhiệm của các bên đối với từng nhiệm vụ BIM trong giai đoạn {{ stage.phrase }} của dự án {{ p.general.name }}.

# ky-hieu | QUY ƯỚC KÝ HIỆU
[Bảng#ky-hieu|10,22,68] Quy ước ký hiệu trong ma trận
| Ký hiệu | Tên gọi | Ý nghĩa |
|---|---|---|
| R | Thực hiện (Responsible) | Trực tiếp thực hiện nhiệm vụ |
| A | Phê duyệt (Accountable) | Chịu trách nhiệm cuối cùng và phê duyệt kết quả; mỗi nhiệm vụ chỉ có một A |
| C | Tham vấn (Consulted) | Được hỏi ý kiến trước hoặc trong khi thực hiện |
| I | Thông báo (Informed) | Được thông báo về kết quả |
| – | Không tham gia | Không có trách nhiệm đối với nhiệm vụ |

- Mỗi nhiệm vụ có duy nhất một vai trò A; ký hiệu "R, A" thể hiện vai trò vừa thực hiện vừa chịu trách nhiệm phê duyệt;
- Vai trò A ký xác nhận trên danh mục kiểm tra hoặc biên bản tương ứng;
- Việc tham vấn (C) và thông báo (I) được thực hiện qua CDE;
- Người được ủy quyền thay thế kế thừa toàn bộ vai trò của người ủy quyền trong thời gian ủy quyền.

# vai-tro | CÁC VAI TRÒ THAM GIA
Các vai trò trong ma trận và đơn vị đảm nhiệm tương ứng như sau:

[Bảng#vai-tro|12,58,30] Danh mục vai trò tham gia ma trận RACI
{{ tbl(['Mã', 'Vai trò', 'Đơn vị'], rows(p.org.raci_roles, 'code', 'role', 'org')) }}

Trong ma trận, vai trò Trưởng nhóm BIM bộ môn và Kỹ thuật viên BIM được hiểu là áp dụng cho bộ môn có liên quan đến nhiệm vụ đang xét, không phải toàn bộ các bộ môn.

# ma-tran | MA TRẬN VAI TRÒ VÀ TRÁCH NHIỆM
Ma trận phân định trách nhiệm cho {{ p.org.raci|length }} nhiệm vụ BIM của giai đoạn, nhóm theo trình tự triển khai:

{% set codes = p.org.raci_roles|map(attribute='code')|list %}
{% set r = [] %}{% set ns = namespace(g=none) %}
{% for t in p.org.raci %}
{% if t.group != ns.g %}{% set _ = r.append(('group', t.group)) %}{% set ns.g = t.group %}{% endif %}
{% set v = split(t.values) %}
{% set _ = r.append([t.ref, t.task] + (v + [''] * codes|length)[:codes|length]) %}
{% endfor %}
[Bảng#ma-tran] Ma trận vai trò và trách nhiệm (RACI)
{{ tbl(['TT', 'Nhiệm vụ'] + codes, r) }}

# ghi-chu | GHI CHÚ ÁP DỤNG VÀ KIỂM SOÁT THAY ĐỔI
- Ma trận này áp dụng cho giai đoạn {{ stage.phrase }}. Sang giai đoạn {{ stage.next }}, ma trận được rà soát lại cùng với BEP của giai đoạn đó;
- Trường hợp một bộ môn không có Trưởng nhóm BIM riêng, Điều phối BIM kiêm nhiệm vai trò này cho bộ môn đó và phải được ghi nhận bằng văn bản;
- Mọi đề nghị điều chỉnh ma trận được gửi qua chức năng quản lý vấn đề (Issues) trên CDE tới Quản lý BIM; Quản lý BIM tổng hợp, trình Chủ nhiệm dự án chấp thuận và phát hành phiên bản cập nhật của phụ lục;
- Phiên bản phụ lục luôn được phát hành đồng bộ với phiên bản BEP tương ứng; khi hai tài liệu có nội dung khác nhau thì áp dụng theo bản có ngày phát hành sau.
