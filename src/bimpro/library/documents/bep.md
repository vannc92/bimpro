---
title: KẾ HOẠCH THỰC HIỆN BIM (BEP)
short: Kế hoạch thực hiện BIM
kind: bep
---
# gioi-thieu | GIỚI THIỆU CHUNG
## co-so | Cơ sở thực hiện
Các cơ sở pháp lý dưới đây được sử dụng làm căn cứ trong quá trình triển khai BIM cho dự án.

{% for x in p.basis.legal %}
- {{ x }};
{% endfor %}
{% for x in p.basis.contracts %}
- {{ x }};
{% endfor %}

{{ p.basis.note }}

## thuat-ngu | Ký tự viết tắt và thuật ngữ
[Bảng#thuat-ngu|6,22,42,20,10] Ký hiệu viết tắt và thuật ngữ
{% set g = [
 ['Chủ đầu tư', 'Tổ chức sở hữu vốn hoặc tổ chức được giao thay mặt chủ sở hữu vốn trực tiếp quản lý quá trình thực hiện dự án.', 'Employer', ''],
 ['Mô hình hóa thông tin công trình', 'Việc sử dụng dạng hiển thị số của công trình xây dựng để hỗ trợ công tác thiết kế, thi công và quản lý vận hành thông qua tạo dựng căn cứ đáng tin cậy cho việc ra quyết định (ISO 19650-1:2018).', 'Building Information Modelling', 'BIM'],
 ['Mô hình BIM', 'Mô hình số hóa ba chiều chứa dữ liệu thông tin công trình.', 'BIM Model', ''],
 ['Mô hình thành phần', 'Mô hình của một khu vực/hệ thống do một bộ môn tạo lập, là đơn vị quản lý và trao đổi nhỏ nhất của dự án.', 'Discipline Model', ''],
 ['Mô hình tổng hợp', 'Mô hình liên kết các mô hình thành phần phục vụ phối hợp và rà soát tổng thể.', 'Federated Model', ''],
 ['Môi trường dữ liệu chung', 'Nơi thu thập, lưu trữ, quản lý và phổ biến toàn bộ thông tin, dữ liệu, tài liệu được tạo ra bởi các bên tham gia thực hiện BIM.', 'Common Data Environment', 'CDE'],
 ['Mức độ phát triển thông tin', 'Chỉ chất lượng, số lượng và mức độ chi tiết của thông tin trong mô hình BIM ở từng giai đoạn đầu tư xây dựng.', 'Level of Development', 'LOD'],
 ['Kế hoạch thực hiện BIM', 'Tài liệu xác định tiêu chuẩn, phương pháp và quy định sử dụng trong dự án để đáp ứng mục tiêu và yêu cầu về BIM, được thống nhất giữa các bên.', 'BIM Execution Plan', 'BEP'],
 ['Yêu cầu về thông tin trao đổi', 'Yêu cầu của Chủ đầu tư để tạo lập thông tin liên quan đến việc áp dụng BIM.', 'Exchange Information Requirements', 'EIR'],
 ['Kế hoạch chuyển giao thông tin nhiệm vụ', 'Kế hoạch chuyển giao thông tin của từng nhóm thực hiện BIM.', 'Task Information Delivery Plan', 'TIDP'],
 ['Kế hoạch chuyển giao thông tin tổng thể', 'Kế hoạch tổng thể được xây dựng từ các TIDP của dự án.', 'Master Information Delivery Plan', 'MIDP'],
 ['Định dạng tập tin IFC', 'Chuẩn định dạng mở phục vụ trao đổi dữ liệu giữa các phần mềm và nộp dữ liệu BIM cho cơ quan chuyên môn về xây dựng.', 'Industry Foundation Classes', 'IFC'],
] %}
{% if f.clash %}{% set _ = g.append(['Phát hiện xung đột', 'Việc dùng công cụ chuyên dụng để tìm các vị trí giao cắt, chồng lấn hoặc vi phạm khoảng hở giữa các đối tượng của mô hình tổng hợp.', 'Clash Detection', '']) %}{% endif %}
{% if f.sim4d %}{% set _ = g.append(['Mô phỏng tiến độ thi công', 'Mô hình BIM gắn với tiến độ để mô phỏng trình tự và biện pháp thi công theo thời gian.', 'BIM 4D', '4D']) %}{% endif %}
{% if f.qto %}{% set _ = g.append(['Bóc tách khối lượng', 'Việc trích xuất khối lượng cấu kiện, vật liệu từ mô hình BIM.', 'Quantity Take-Off', 'QTO']) %}{% endif %}
{% if f.asbuilt %}{% set _ = g.append(['Mô hình thông tin tài sản', 'Mô hình thông tin phục vụ giai đoạn quản lý, vận hành công trình, hình thành từ mô hình hoàn công.', 'Asset Information Model', 'AIM']) %}{% endif %}
{% set _ = g.extend([
 ['Quản lý BIM', 'Người chịu trách nhiệm xác định chiến lược áp dụng BIM, chủ trì điều phối và quản lý thông tin trong quá trình áp dụng BIM.', 'BIM Manager', ''],
 ['Điều phối BIM', 'Người chịu trách nhiệm điều phối công việc thiết kế và phối hợp giữa các bộ môn trên mô hình.', 'BIM Coordinator', ''],
 ['Kỹ thuật viên BIM', 'Người trực tiếp tạo lập mô hình BIM.', 'BIM Modeler', ''],
 ['Nhóm thực hiện BIM', 'Các bộ phận trực tiếp tạo lập và quản lý thông tin BIM của dự án.', 'Task Team', ''],
]) %}
{% set r = [] %}{% for x in g %}{% set _ = r.append([loop.index|string] + x) %}{% endfor %}
{{ tbl(['TT', 'Thuật ngữ', 'Định nghĩa', 'Từ tiếng Anh', 'Viết tắt'], r) }}

## thong-tin | Thông tin chung của dự án
[Bảng#thong-tin|28,72] Thông tin chung của dự án
{{ tbl(['Thông tin', 'Nội dung'], rows(p.general.info, 'label', 'value')) }}

## tien-do | Tiến độ dự án
[Bảng#tien-do|8,62,30] Các mốc tiến độ chính của dự án
{{ tbl(['TT', 'Nội dung công việc', 'Thời gian dự kiến'], rows(p.schedule.milestones, '#', 'task', 'time')) }}

[Hình#tien-do?] Mốc tiến độ và sản phẩm BIM

## tieu-chuan | Tiêu chuẩn áp dụng
{{ A }} tham khảo và áp dụng các tiêu chuẩn, hướng dẫn cho công tác triển khai BIM của dự án như bảng bên dưới:

[Bảng#tieu-chuan|26,14,45,15] Tiêu chuẩn và quy định áp dụng
{{ tbl(['Tên', 'Ngày ban hành', 'Mô tả', 'Yêu cầu'], rows(p.basis.standards, 'name', 'date', 'description', 'requirement')) }}

## tai-lieu | Tài liệu kèm theo Kế hoạch thực hiện BIM
Các phụ lục dưới đây là bộ phận không tách rời của Kế hoạch thực hiện BIM, được phát hành thành tài liệu độc lập có mã hiệu riêng và được cập nhật trong quá trình thực hiện gói thầu:

[Bảng#tai-lieu|10,34,56] Danh mục tài liệu kèm theo BEP
{% set r = [] %}{% for d in appendices %}{% set _ = r.append([d.label, d.title, d.summary]) %}{% endfor %}
{{ tbl(['Mã', 'Tên tài liệu', 'Nội dung chính'], r) }}

# muc-tieu | MỤC TIÊU VÀ NỘI DUNG ÁP DỤNG BIM CHO DỰ ÁN
## muc-tieu-bim | Mục tiêu áp dụng BIM
Trong giai đoạn {{ stage.phrase }}, các mục tiêu ứng dụng BIM được xác định như sau:

{% for x in p.bim.objectives %}
- {{ x }}{{ ';' if not loop.last else '.' }}
{% endfor %}

## noi-dung | Nội dung áp dụng BIM
### noi-dung-bang | Nội dung áp dụng BIM cho dự án
Các nội dung áp dụng BIM trong giai đoạn {{ stage.short }} của dự án như sau:

[Bảng#noi-dung|8,62,15,15] Các nội dung áp dụng BIM
{% set r = [] %}{% for u in p.bim.uses %}{% set _ = r.append([loop.index|string, u.name, 'X' if u.required else '', '' if u.required else 'X']) %}{% endfor %}
{{ tbl(['TT', 'Nội dung áp dụng BIM', 'Bắt buộc', 'Tùy chọn'], r) }}

### noi-dung-mo-ta | Mô tả nội dung áp dụng BIM cho dự án
{% for u in p.bim.uses %}
### {{ u.name }}

{{ u.description }}

{% endfor %}

## gioi-han | Giới hạn phạm vi áp dụng BIM ở giai đoạn {{ stage.short }}
Để thống nhất cách hiểu giữa các bên và làm cơ sở nghiệm thu sản phẩm, phạm vi áp dụng BIM ở giai đoạn này được giới hạn như sau:

{% for x in p.bim.limits %}
- {{ x }}{{ ';' if not loop.last else '.' }}
{% endfor %}

# to-chuc | SƠ ĐỒ TỔ CHỨC, VAI TRÒ, TRÁCH NHIỆM VÀ NHÂN SỰ THAM GIA
## so-do | Sơ đồ tổ chức
[Hình#so-do-to-chuc] Sơ đồ tổ chức thực hiện BIM cho dự án

## vai-tro | Vai trò và trách nhiệm
[Bảng#vai-tro|28,72] Trách nhiệm và nội dung công việc thực hiện BIM
| Trách nhiệm | Nội dung công việc |
|---|---|
| Chủ đầu tư (Ban Quản lý dự án) | • Phê duyệt Kế hoạch thực hiện BIM (BEP) và bảo đảm đáp ứng các yêu cầu về phạm vi công việc của dự án;<br>• Tổ chức họp định kỳ với nhóm BIM của {{ A }} để thống nhất quy trình, cách tiếp cận và giải quyết các vướng mắc;<br>• Tổ chức nghiệm thu các sản phẩm BIM của dự án theo BEP đã được phê duyệt. |
{% if f.supervisor %}
| Tư vấn giám sát, quản lý BIM | • Chủ trì tổ chức phối hợp BIM giữa các bên theo phân công của Chủ đầu tư;<br>• Kiểm tra độc lập chất lượng mô hình BIM và kết quả phát hiện xung đột của {{ A }};<br>• Xem xét, cho ý kiến về sản phẩm BIM trước khi Chủ đầu tư chấp thuận. |
{% endif %}
| Quản lý BIM (BIM Manager) | • Quản lý, phát triển và triển khai kế hoạch thực hiện của nhóm triển khai BIM;<br>• Kiểm soát và duy trì chất lượng sản phẩm BIM, bảo đảm tuân thủ BEP và các tiêu chuẩn áp dụng;<br>• Quản lý mô hình tổng hợp cho tất cả các hệ thống, khu vực và bộ môn;<br>• Duy trì và quản lý Kế hoạch chuyển giao thông tin và danh mục sản phẩm chuyển giao;<br>• Phê duyệt các sản phẩm thông tin trước khi phát hành lên vùng dữ liệu của Chủ đầu tư trên CDE theo các mốc đã thỏa thuận;<br>• Lập Báo cáo mô hình thông tin công trình BIM. |
| Điều phối BIM (BIM Coordinator) | • Phối hợp xây dựng, triển khai và cập nhật BEP của dự án;<br>• Phối hợp lập kế hoạch, thiết lập và duy trì các tập tin dữ liệu, hệ tọa độ và điểm gốc dự án;<br>• Liên kết mô hình các bộ môn thành mô hình tổng hợp tại các mốc quan trọng xác định trong BEP;<br>• {% if f.clash %}Chủ trì chạy kiểm tra xung đột trên mô hình tổng hợp, lập báo cáo xung đột{% else %}Chủ trì kiểm tra phối hợp trực quan, rà soát tổng mặt bằng và giao diện giữa các hạng mục{% endif %}; ghi nhận và theo dõi vấn đề trên CDE;<br>• Điều phối các cuộc họp phối hợp và xử lý vấn đề của mô hình. |
| Chuyên gia quản lý dữ liệu (CDE Manager) | • Thiết lập, cấu hình và quản lý môi trường dữ liệu chung của nhóm thực hiện, bảo đảm tính khả dụng cho từng nhóm trong giai đoạn {{ stage.short }};<br>• Thiết lập cấu trúc thư mục, trạng thái CDE, ma trận phân quyền và các quy trình xem xét – trình duyệt – phân phối tài liệu;<br>• Giám sát việc cập nhật tài liệu lên CDE và bảo đảm mọi thông tin tuân thủ tiêu chuẩn đặt tên của dự án;<br>• Hướng dẫn các thành viên truy cập CDE, yêu cầu quyền truy cập mới và các quy định bảo mật phải tuân thủ. |
| Trưởng nhóm BIM các bộ môn | • Kiểm tra chất lượng mô hình BIM của bộ môn; phối hợp với Điều phối BIM để xử lý các vấn đề nội bộ bộ môn;<br>• Phối hợp với các bộ môn khác trong công tác thực hiện BIM cho dự án;<br>• Lập kế hoạch và kiểm soát nhiệm vụ triển khai BIM trong từng bộ môn. |
| Kỹ thuật viên BIM (BIM Modeler) | • Tạo lập, cập nhật và chỉnh sửa mô hình bộ môn theo đúng quy ước của BEP;<br>• Trích xuất thông tin, hình ảnh và mặt cắt từ mô hình phục vụ thuyết minh và họp phối hợp{% if f.drawings %};<br>• Triển khai bản vẽ từ mô hình theo quy định của dự án{% endif %}. |

Ma trận trách nhiệm chi tiết (RACI) của dự án được trình bày tại {{ pl('pl_raci') }} – MA TRẬN VAI TRÒ VÀ TRÁCH NHIỆM đính kèm.

## nhan-su | Nhân sự tham gia dự án
Danh sách nhân sự tham gia triển khai BIM của {{ A }} như sau:

[Bảng#nhan-su|7,24,13,30,26] Nhân sự chính tham gia dự án
{{ tbl(['TT', 'Họ và tên', 'Đơn vị', 'Vai trò', 'Email'], rows(p.org.people, '#', 'name', 'org', 'role', 'email')) }}

## nang-luc | Yêu cầu năng lực và đào tạo
- Quản lý BIM và Điều phối BIM: có kinh nghiệm triển khai BIM cho ít nhất một dự án công trình năng lượng hoặc công nghiệp; nắm vững ISO 19650/TCVN 14177 và quy trình quản lý thông tin trên CDE;
- Trưởng nhóm BIM bộ môn: là chủ trì hoặc thành viên chủ chốt của bộ môn thiết kế tương ứng, sử dụng thành thạo phần mềm dựng mô hình của bộ môn;
- Kỹ thuật viên BIM: sử dụng thành thạo phần mềm dựng mô hình ở mức tạo lập mô hình và thư viện đối tượng (family), hiểu quy ước đặt tên và hệ tọa độ của dự án;
- Toàn bộ thành viên tham gia phải được hướng dẫn sử dụng CDE trước khi được cấp quyền truy cập; nội dung và thời điểm hướng dẫn do Chuyên gia quản lý dữ liệu tổ chức.

# du-lieu | QUẢN LÝ DỮ LIỆU VÀ TRAO ĐỔI THÔNG TIN
## pham-vi | Phạm vi công việc
Phạm vi công việc áp dụng BIM cho dự án bao gồm:

### pv-cde | Thiết lập môi trường dữ liệu chung (CDE)
{% if p.cde.provider and p.cde.provider != p.general.author_short %}
- Tiếp nhận và sử dụng môi trường dữ liệu chung {{ CDE }} do {{ p.cde.provider }} cung cấp, vận hành cho dự án:
  + Đề nghị cấp tài khoản, phân quyền cho nhóm thực hiện BIM của {{ A }} theo vai trò;
  + Tổ chức dữ liệu của {{ A }} theo cấu trúc thư mục, trạng thái và quy trình trao đổi đã thống nhất với Chủ đầu tư;
  + Tham gia thử nghiệm, hoàn thiện các quy trình phối hợp trên CDE giữa các bên;
  + Hướng dẫn nội bộ việc sử dụng CDE cho các thành viên tham gia.
{% else %}
- Xây dựng môi trường dữ liệu chung trong giai đoạn {{ stage.short }}:
  + Cung cấp và vận hành nền tảng môi trường dữ liệu chung {{ CDE }} của {{ p.cde.provider }} cho dự án, bảo đảm đáp ứng yêu cầu của giai đoạn {{ stage.phrase }};
  + Thiết lập, cấu hình, phân quyền và quản lý việc trao đổi dữ liệu trên CDE giữa Chủ đầu tư/Ban Quản lý dự án, {{ A }} và các bên liên quan;
  + Cài đặt và thiết lập cấu trúc dữ liệu, bao gồm thống nhất các biểu mẫu (bản vẽ, công văn, tài liệu) và các tiêu chuẩn, hướng dẫn áp dụng trong dự án;
  + Thử nghiệm, cập nhật và hoàn thiện các quy trình phối hợp trên CDE giữa Chủ đầu tư và {{ A }};
  + Hướng dẫn sử dụng môi trường dữ liệu chung cho các bên tham gia.
{% endif %}
- Hướng dẫn, phổ biến và hỗ trợ Chủ đầu tư trong việc khai thác mô hình BIM/3D phục vụ điều phối, kiểm soát và phê duyệt thiết kế trên môi trường dữ liệu chung.

### pv-bep | Lập Kế hoạch thực hiện BIM (BEP)
- Xác định mục tiêu và các ứng dụng BIM trong giai đoạn {{ stage.phrase }} của dự án;
- Xây dựng kế hoạch chuyển giao thông tin tổng thể (MIDP) trên cơ sở các TIDP của từng nhóm thực hiện;
- Thiết kế quy trình triển khai, xác định rõ nhiệm vụ, chức năng và công việc của từng bên liên quan đến hoạt động phối hợp và trao đổi thông tin;
- Xác định các loại thông tin, mức độ chi tiết và quy trình tạo lập, kiểm soát, phê duyệt, trao đổi thông tin dự án;
- Xác định hệ thống tập tin dùng để trao đổi, liên kết và tổng hợp mô hình;
- Lập tiến độ và tần suất cập nhật mô hình, tần suất kiểm tra phối hợp.

### pv-mo-hinh | Xây dựng mô hình BIM
{% if f.existing %}
- Tiếp nhận mô hình BIM của giai đoạn trước và hồ sơ hiện trạng; dựng mô hình các hạng mục hiện hữu làm nền cho công tác phối hợp;
{% endif %}
- Xây dựng mô hình các hạng mục chính theo danh mục tại @sec[pv-hang-muc];
- Xây dựng mô hình hệ thống hạ tầng kỹ thuật trong phạm vi công trình{% if f.asbuilt %};
- Cập nhật mô hình trong quá trình thi công và lập mô hình hoàn công khi kết thúc xây lắp{% endif %}.

### pv-dieu-phoi | Điều phối, phối hợp BIM
{% if f.clash %}
Mô hình của các bộ môn được liên kết thành mô hình tổng hợp để phối hợp và phát hiện xung đột. Hồ sơ {{ stage.short }} chỉ được phát hành khi các xung đột đã được giải quyết; các vấn đề phát hiện được ghi nhận, phân công xử lý và theo dõi đến khi đóng trên CDE.
{% else %}
Mô hình của các bộ môn được liên kết để bảo đảm sự ăn khớp giữa các mô hình thành phần. Ở giai đoạn {{ stage.short }}, công tác điều phối tập trung vào rà soát tổng mặt bằng, kiểm tra bố trí không gian và giao diện giữa các hạng mục; các vấn đề phát hiện được ghi nhận, phân công xử lý và theo dõi đến khi đóng trên CDE.
{% endif %}

- Liên kết mô hình các bộ môn thành mô hình tổng hợp theo mốc;
{% if f.clash %}
- Chạy kiểm tra xung đột theo ma trận tại @sec[xung-dot] và lập báo cáo xung đột;
{% endif %}
- Tổ chức họp phối hợp BIM và lập biên bản ghi nhận kết quả.

### pv-hang-muc | Các hạng mục áp dụng BIM
Dự án áp dụng mô hình thông tin công trình (BIM) cho các hạng mục chính sau:

{% for x in p.bim.scope_items %}
- {{ x }}{{ ';' if not loop.last else '.' }}
{% endfor %}

## phan-chia | Phân chia mô hình
Việc phân chia mô hình BIM của dự án thành các mô hình thành phần giúp kiểm soát và quản lý mô hình, thuận tiện cho công tác phối hợp và bàn giao. Ở giai đoạn {{ stage.short }}, mô hình được phân chia theo khu vực/hệ thống và theo bộ môn thiết kế như sau:

[Bảng#phan-chia|7,25,15,53] Bảng phân chia mô hình theo khu vực/hệ thống và bộ môn
{{ tbl(['TT', 'Khu vực/hệ thống', 'Bộ môn', 'Phạm vi cấu kiện thể hiện trong mô hình'], rows(p.models.areas, '#', 'area', 'discipline', 'scope')) }}

[Bảng#ma-hieu|7,22,24,13,34] Danh mục mô hình và mã hiệu
{{ tbl(['TT', 'Khu vực/hệ thống', 'Mô hình thành phần', 'Bộ môn', 'Mã hiệu mô hình'], rows(p.models.files, '#', 'area', 'content', 'discipline', 'code')) }}

[Hình#phan-chia?] Phân chia mô hình và mô hình tổng hợp

## cde | Môi trường dữ liệu chung – {{ CDE }}
Môi trường dữ liệu chung (CDE) là nguồn thông tin duy nhất của dự án, dùng để thu thập, quản lý và phổ biến tất cả các tài liệu được tạo ra bởi các bên tham gia.

{{ p.cde.intro }}

{{ CDE }} quản lý tài liệu theo bốn vùng trạng thái tuân thủ ISO 19650, gồm: Work in Progress (đang xử lý – chỉ nhóm tác giả truy cập), Shared (chia sẻ để các bên xem xét, phối hợp), Published (đã được phê duyệt chính thức) và Archived (lưu trữ lịch sử). Trạng thái được gán ở cấp thư mục và tệp kế thừa trạng thái của thư mục chứa nó; do đó cấu trúc thư mục dự án được thiết lập ngay từ đầu giai đoạn và chỉ thay đổi khi có sự thống nhất giữa các bên.

[Hình#cde?] Các vùng trạng thái và luồng thông tin trên CDE

[Bảng#phan-he|30,70] Các phân hệ {{ CDE }} áp dụng cho dự án
{{ tbl(['Phân hệ', 'Mục đích sử dụng trong dự án'], rows(p.cde.modules, 'name', 'purpose')) }}

Giới hạn kỹ thuật cần lưu ý khi vận hành: tệp mô hình IFC tải lên {{ CDE }} phải nhỏ hơn {{ p.cde.size_limit }}; nếu lớn hơn, mô hình được xuất IFC theo từng khu vực/hệ thống.

Cấu trúc thư mục, ma trận phân quyền theo vai trò và quy định vận hành CDE được trình bày tại {{ pl('pl_cde') }} đính kèm.

## chuyen-giao | Kế hoạch chuyển giao thông tin
### ha-tang | Hạ tầng công nghệ thông tin
{{ p.delivery.it }}

### san-pham | Sản phẩm BIM bàn giao
{{ A }} sử dụng các định dạng trao đổi sau đây cho việc chuyển giao thông tin của các sản phẩm đầu ra:

{% for x in p.delivery.formats %}
- {{ x }}{{ ';' if not loop.last else '.' }}
{% endfor %}

[Bảng#chuyen-giao|8,47,25,20] Kế hoạch chuyển giao thông tin
{{ tbl(['TT', 'Sản phẩm BIM', 'Định dạng', 'Mốc chuyển giao'], rows(p.delivery.deliverables, '#', 'name', 'format', 'milestone')) }}

{{ p.delivery.review_products }}

Kế hoạch chuyển giao chi tiết theo từng nhóm thực hiện (TIDP) và kế hoạch tổng thể (MIDP) được trình bày tại {{ pl('pl_midp') }} đính kèm.

### bao-cao-bim | Cấu trúc Báo cáo mô hình thông tin công trình BIM {when: p.delivery.report_outline}
Báo cáo mô hình thông tin công trình BIM của từng đợt và báo cáo khi kết thúc giai đoạn được lập theo cấu trúc sau:

{% for x in p.delivery.report_outline %}
{% if x[:1].isdigit() and '.' in x.split(' ')[0] and x.split(' ')[0].strip('.').count('.') >= 1 %}
  + {{ x }}
{% else %}
- {{ x }}
{% endif %}
{% endfor %}

## lod | Mức độ phát triển thông tin (LOD)
Mức độ phát triển thông tin (Level of Development – LOD) bao gồm thông tin hình học và phi hình học của các thành phần, cấu kiện, phù hợp với yêu cầu của dự án và các quy định cụ thể liên quan đến sản phẩm mô hình. Trong một mô hình BIM ở mỗi giai đoạn thiết kế nhất định, các thành phần trong mô hình có thể có mức độ phát triển khác nhau.

{% if stage.code == 'TKCS' %}
Ở giai đoạn thiết kế cơ sở, các thành phần mô hình được thể hiện bằng đồ họa với các thể hiện tương đối về số lượng, kích thước, hình dạng và vị trí gần đúng của các hạng mục, thiết bị chính nhằm trực quan hóa ý tưởng thiết kế.
{% else %}
Ở giai đoạn {{ stage.short }}, các thành phần mô hình thể hiện đầy đủ hình học, kích thước, cao độ, vị trí, chủng loại và đặc tính của vật liệu, cấu kiện, cùng quan hệ lắp ghép, giao diện với các hệ thống khác, đủ để phối hợp, phát hiện xung đột và phục vụ thi công. Mức độ phát triển thông tin chung của dự án là LOD {{ LOD }}.
{% endif %}

Mức độ phát triển thông tin của các đối tượng mô hình theo từng bộ môn cụ thể như sau:

[Bảng#lod|7,38,10,45] Mức độ phát triển thông tin của mô hình
{{ tbl(['TT', 'Tên cấu kiện', 'LOD', 'Thông tin phi hình học cần đính kèm'], grows(p.models.lod, 'group', '#', 'element', 'lod', 'info')) }}

{% if 'pl_lod' in docs|map(attribute='doc') %}
Định nghĩa các mức LOD, bộ tham số thông tin bắt buộc và quy định quản lý tham số được trình bày tại {{ pl('pl_lod') }} đính kèm.
{% endif %}

# phoi-hop | QUY TRÌNH PHỐI HỢP
## quy-trinh | Quy trình phối hợp và tạo lập mô hình BIM
[Hình#quy-trinh] Quy trình phối hợp và tạo lập mô hình BIM

[Bảng#quy-trinh|9,26,65] Diễn giải quy trình phối hợp và tạo lập mô hình BIM
| Bước | Vai trò | Nội dung công việc |
|---|---|---|
| 1 | Quản lý BIM, Chuyên gia quản lý dữ liệu | Họp thống nhất: nhóm thực hiện BIM trao đổi và thống nhất kế hoạch, quy trình thực hiện và cách thức trao đổi; vai trò, trách nhiệm của mỗi thành viên, bộ môn; hệ tọa độ và điểm gốc dự án; các mốc phối hợp; cách thức lưu trữ và phát hành. |
| 2 | Kỹ thuật viên BIM | Lập mô hình BIM bộ môn ở mức LOD {{ LOD }} theo quy ước đặt tên, hệ tọa độ và phạm vi cấu kiện đã thống nhất. |
| 3 | Trưởng nhóm BIM bộ môn | Kiểm tra nội bộ bộ môn: sự đầy đủ của cấu kiện theo phạm vi, quy ước đặt tên, mức độ LOD, hệ tọa độ và cao độ. Khi chưa đạt, mô hình được trả lại Bước 2 để cập nhật. |
| 4 | Điều phối BIM | Liên kết mô hình các bộ môn thành mô hình tổng hợp và lưu tại thư mục dùng chung đã thống nhất ở Bước 1. |
{% if f.clash %}
| 5 | Điều phối BIM | Chạy kiểm tra xung đột trên mô hình tổng hợp theo ma trận tại @sec[xung-dot]; lập báo cáo xung đột, ghi nhận từng xung đột bằng chức năng Issues trên CDE, phân công xử lý và theo dõi đến khi đóng; mô hình được cập nhật theo vòng lặp về Bước 2. |
{% else %}
| 5 | Điều phối BIM | Kiểm tra phối hợp trực quan trên mô hình tổng hợp; rà soát tổng mặt bằng, khoảng cách bố trí và giao diện giữa các hạng mục. Các vấn đề phát hiện được ghi nhận bằng chức năng Issues/Markup trên CDE, phân công xử lý và theo dõi đến khi đóng; mô hình được cập nhật theo vòng lặp về Bước 2. |
{% endif %}
{% if f.supervisor %}
| 6 | Quản lý BIM; Tư vấn giám sát, quản lý BIM | Quản lý BIM phê duyệt chuyển mô hình sang trạng thái Shared; Tư vấn giám sát kiểm tra độc lập mô hình tổng hợp, lập báo cáo xung đột và sai sót thiết kế (nếu có); các ý kiến được ghi nhận trên CDE và xử lý theo vòng lặp về Bước 2. |
| 7 | Quản lý BIM, Chuyên gia quản lý dữ liệu | Bàn giao và phát hành mô hình BIM cho Chủ đầu tư theo đúng trạng thái CDE và mốc chuyển giao đã thống nhất. |
{% else %}
| 6 | Quản lý BIM, Chuyên gia quản lý dữ liệu | Bàn giao và phát hành mô hình BIM cho Chủ đầu tư theo đúng trạng thái CDE và mốc chuyển giao đã thống nhất. |
{% endif %}

## kiem-tra | Cách thức phối hợp và kiểm tra ở giai đoạn {{ stage.short }}
{% if f.clash %}
Ở giai đoạn {{ stage.short }}, mô hình BIM là cơ sở để phối hợp giữa các bộ môn trước khi phát hành hồ sơ thiết kế. Ngoài kiểm tra trực quan và kiểm tra tuân thủ BEP, dự án áp dụng kiểm tra xung đột bằng công cụ chuyên dụng (xem @sec[xung-dot]). Các nội dung kiểm tra được áp dụng như sau:
{% else %}
Ở giai đoạn {{ stage.short }}, mô hình BIM đóng vai trò phác thảo và trực quan hóa ý tưởng thiết kế; thông tin về hình dáng, kích thước của các hạng mục và thiết bị chính mới ở mức sơ khởi. Do đó công tác phối hợp tập trung vào kiểm tra trực quan và rà soát tổng thể, chưa thực hiện kiểm tra va chạm tự động giữa các bộ môn. Các nội dung kiểm tra được áp dụng như sau:
{% endif %}

[Bảng#kiem-tra|20,32,18,15,15] Cách thức phối hợp và kiểm tra mô hình
{{ tbl(['Nội dung kiểm tra', 'Mô tả', 'Trách nhiệm', 'Phần mềm', 'Tần suất'], rows(p.coordination.checks, 'name', 'description', 'responsible', 'software', 'frequency')) }}

{% if not f.clash %}
Định hướng cho giai đoạn tiếp theo: từ giai đoạn {{ stage.next }}, khi mức độ phát triển thông tin đạt LOD 300 trở lên, dự án sẽ áp dụng kiểm tra va chạm tự động bằng công cụ chuyên dụng theo ma trận va chạm giữa các cặp bộ môn, kèm quy định về dung sai, phân loại mức độ nghiêm trọng và quy trình đóng va chạm. Ma trận va chạm và các quy định này sẽ được xây dựng trong BEP của giai đoạn {{ stage.next }}.
{% endif %}

## xung-dot | Phát hiện và xử lý xung đột {when: f.clash}
Điều phối BIM chạy kiểm tra xung đột trên mô hình tổng hợp tại mỗi mốc phối hợp và trước mỗi đợt phát hành hồ sơ. Xung đột được phân thành ba loại:

- Xung đột cứng: hai đối tượng giao cắt, chồng lấn về hình học;
- Xung đột mềm: vi phạm khoảng hở yêu cầu cho thi công, vận hành, bảo trì hoặc an toàn;
- Xung đột trình tự: mâu thuẫn giữa biện pháp, trình tự thi công với hiện trạng hoặc với hoạt động vận hành.

Các cặp đối tượng kiểm tra, dung sai và trách nhiệm như sau:

[Bảng#xung-dot|30,16,14,22,18] Ma trận kiểm tra xung đột
{{ tbl(['Cặp đối tượng kiểm tra', 'Loại xung đột', 'Dung sai', 'Trách nhiệm', 'Tần suất'], rows(p.coordination.clashes, 'pair', 'kind', 'tolerance', 'responsible', 'frequency')) }}

[Hình#cong-trinh?] Sơ đồ công trình và vị trí kiểm tra xung đột

Mỗi xung đột được ghi nhận thành một vấn đề (Issue) trên CDE kèm vị trí, hình ảnh, bộ môn chịu trách nhiệm và thời hạn xử lý. Bộ môn chịu trách nhiệm cập nhật mô hình; Điều phối BIM chạy lại kiểm tra để xác nhận và đóng vấn đề. Hồ sơ {{ stage.short }} của từng đợt chỉ được phát hành khi các xung đột thuộc phạm vi đợt đó đã được giải quyết hoặc đã có phương án xử lý được Chủ đầu tư chấp thuận.

[Hình#xung-dot?] Vòng phát hiện và xử lý xung đột

{% if 'pl_clash' in docs|map(attribute='doc') %}
Quy trình chi tiết, phân loại mức độ và mẫu báo cáo xung đột được trình bày tại {{ pl('pl_clash') }} đính kèm.
{% endif %}

## phan-mem | Phần mềm và phiên bản sử dụng
Các phần mềm sử dụng cho dự án được thống nhất theo bảng dưới đây. Các bộ môn sử dụng cùng một phiên bản phần mềm dựng mô hình trong suốt giai đoạn để tránh lỗi khi liên kết và nâng cấp tập tin.

[Bảng#phan-mem|26,14,24,16,20] Phần mềm và phiên bản sử dụng
{{ tbl(['Ứng dụng', 'Trách nhiệm', 'Phần mềm và phiên bản', 'Định dạng gốc', 'Định dạng chuyển giao'], rows(p.coordination.software, 'use', 'responsible', 'software', 'native', 'exchange')) }}

## toa-do | Đơn vị đo lường, hệ tọa độ và điểm gốc dự án
- Đơn vị đo lường: {{ p.coordination.units }};
- Tỷ lệ mô hình: 1:1;
- Hệ tọa độ: {{ p.coordination.coord_system }};
- Điểm gốc dự án (Project Base Point) và hướng bắc dự án được Điều phối BIM thiết lập trên tệp mẫu và phát hành cho các bộ môn trước khi bắt đầu dựng mô hình; các bộ môn không được tự thay đổi điểm gốc và hệ tọa độ chia sẻ.

Thông số hệ tọa độ và điểm gốc dự án: {{ p.coordination.coord_params }}

## trao-doi | Trao đổi dữ liệu
Các bên cần tuân thủ các quy định sau:

- Toàn bộ dữ liệu được trao đổi qua môi trường dữ liệu chung. Việc phối hợp, trao đổi và xem xét thông tin dự án (bao gồm mô hình BIM) sử dụng các chức năng xem xét, trình duyệt, phân phối tài liệu và quản lý vấn đề của {{ CDE }} theo đúng vai trò của mỗi bên;
- Việc đặt tên tập tin và thư mục tuân thủ quy ước đặt tên nêu tại @sec[dat-ten] và {{ pl('pl_naming') }};
- Mọi mô hình được tải lên ở định dạng đã thống nhất; mô hình chỉ được chuyển sang trạng thái Shared sau khi đã qua kiểm tra nội bộ bộ môn;
- {{ A }} bàn giao mô hình tổng hợp giai đoạn {{ stage.short }} ở định dạng *.nwd và *.ifc cho Chủ đầu tư;
{% for x in p.coordination.exchange_extra %}
- {{ x }};
{% endfor %}
- Không trao đổi mô hình và tài liệu dự án qua các kênh ngoài CDE (thư điện tử cá nhân, dịch vụ lưu trữ đám mây công cộng, thiết bị lưu trữ rời) trừ trường hợp được Chủ đầu tư chấp thuận bằng văn bản.

## dat-ten | Quy ước đặt tên tập tin
### nguyen-tac | Nguyên tắc chung
- Các ký tự được phép dùng để đặt tên thư mục và tập tin là a-z, A-Z, chữ số, dấu gạch ngang (-) và dấu gạch dưới (_). Không sử dụng dấu cách, chữ cái có dấu tiếng Việt và các ký tự đặc biệt vì có thể gây lỗi tìm kiếm, lỗi ký tự hoặc lỗi khi mở bằng một số phần mềm;
- Tên thư mục và tập tin đặt ngắn nhất có thể do giới hạn độ dài đường dẫn của hệ điều hành (không vượt quá 256 ký tự);
- Quy tắc đặt tên tập tin gồm các trường thông tin chính, phân cách bằng dấu gạch ngang "-";
- Trong một trường thông tin, các nội dung chính và phụ được phân cách bằng dấu gạch dưới "_".

### quy-uoc | Quy ước đặt tên
Quy ước đặt tên tập tin của dự án như sau:

> {{ p.naming.syntax }}

{{ p.naming.example }}

Diễn giải chi tiết nội dung của các trường và bảng mã tương ứng được trình bày tại {{ pl('pl_naming') }} – QUY ĐỊNH ĐẶT TÊN TẬP TIN đính kèm.

## dat-ten-cau-kien | Quy ước đặt tên cấu kiện và vật liệu
> <TenCauKien>_(TruongBoSung1)_(TruongBoSung2)_(TruongBoSung3)

- Đặt cho Family đối với Loadable Family và cho Type đối với System Family;
- Đặt tên bằng tiếng Anh, không sử dụng khoảng trống, viết hoa chữ cái đầu mỗi từ, sử dụng dấu "-" để phân cách trong cùng một trường;
- Không đưa tên Family Name xuống Type Name, ngoại trừ đối tượng Model In Place hoặc Generic Model;
- Tên đặt ngắn nhất có thể, khuyến khích sử dụng từ viết tắt; thông tin trong <> là bắt buộc, trong () là không bắt buộc.

Quy ước đặt tên vật liệu:

> <VatLieu>_(ThuocTinh1)_(ThuocTinh2)_(ThuocTinh3)

- Tên vật liệu phải chỉ ra sự khác biệt cơ bản giữa các loại vật liệu (loại, màu sắc, hoàn thiện) và thể hiện kích thước tiêu chuẩn nếu cần;
- Trong nhóm thông số "Identity" điền thêm: "Model" – mã vật liệu; "Description" – mô tả vật liệu (ví dụ: Bê tông B30); "Mark" – công tác thi công; "Manufacturer" – tên đơn vị sản xuất;
- Ví dụ: Betong_B30_P01.

# chat-luong | KIỂM SOÁT CHẤT LƯỢNG VÀ NGHIỆM THU MÔ HÌNH
## tieu-chi | Tiêu chí chấp nhận mô hình
Mô hình BIM được xem là đạt yêu cầu khi thỏa mãn đồng thời các tiêu chí sau:

- Được phân chia đúng như đã thống nhất tại @sec[phan-chia] và mang đúng mã hiệu quy định;
- Sử dụng đúng hệ tọa độ chia sẻ và điểm gốc dự án; các mô hình thành phần khi liên kết phải trùng khớp về vị trí và cao độ;
- Đầy đủ cấu kiện theo phạm vi quy định, đạt mức độ phát triển thông tin và có đủ thông tin phi hình học theo @[lod];
- Thống nhất và đồng bộ với {{ stage.design_docs }} đã phát hành;
{% if f.clash %}
- Không còn xung đột chưa được giải quyết trong phạm vi đợt phát hành, theo báo cáo xung đột mới nhất;
{% endif %}
- Đã loại bỏ các thành phần, khối lượng công việc và liên kết không cần thiết; không còn đối tượng lỗi hoặc không xác định; các tệp phụ thuộc và liên kết đã được kiểm tra trước khi chia sẻ;
- Tên tập tin, tên cấu kiện và vật liệu tuân thủ quy ước đặt tên của dự án;
- Dung lượng tệp và cấu trúc tệp phù hợp với giới hạn kỹ thuật của CDE.

## ba-lop | Quy trình kiểm tra ba lớp
[Bảng#ba-lop|24,24,52] Các lớp kiểm tra chất lượng mô hình
| Lớp | Người thực hiện | Nội dung kiểm tra |
|---|---|---|
| Lớp 1 – Tự kiểm | Kỹ thuật viên BIM | Sự đầy đủ của cấu kiện theo phạm vi được giao; quy ước đặt tên; cảnh báo và lỗi trong tệp mô hình |
| Lớp 2 – Kiểm tra bộ môn | Trưởng nhóm BIM bộ môn | Mức độ LOD, thông tin phi hình học, tọa độ và cao độ, sự phù hợp với hồ sơ thiết kế của bộ môn |
| Lớp 3 – Kiểm tra tổng hợp | Điều phối BIM, Quản lý BIM | Sự trùng khớp giữa các mô hình thành phần; {% if f.clash %}kết quả kiểm tra xung đột{% else %}kết quả rà soát tổng mặt bằng và giao diện{% endif %}; tình trạng đóng các vấn đề trên CDE |

{% if 'pl_qc' in docs|map(attribute='doc') %}
Danh mục kiểm tra chi tiết cho từng lớp được trình bày tại {{ pl('pl_qc') }} đính kèm.
{% endif %}

## khong-phu-hop | Xử lý sản phẩm không phù hợp
Khi mô hình không đạt một trong các tiêu chí nêu tại @sec[tieu-chi], Điều phối BIM lập ghi nhận trên CDE, nêu rõ nội dung không phù hợp, bộ môn chịu trách nhiệm và thời hạn khắc phục. Mô hình được trả về bước lập mô hình để cập nhật và phải đi lại toàn bộ vòng kiểm tra. Mô hình chưa đạt không được chuyển sang trạng thái Shared hoặc Published trên CDE.

## nghiem-thu | Nghiệm thu và phát hành
- Quản lý BIM tổng hợp hồ sơ nghiệm thu nội bộ gồm: mô hình thành phần, mô hình tổng hợp, kết quả kiểm tra ba lớp và báo cáo tình trạng vấn đề trích xuất từ CDE;
- Sản phẩm sau khi được Chủ nhiệm dự án chấp thuận sẽ được Quản lý BIM phê duyệt phát hành lên vùng dữ liệu của Chủ đầu tư trên CDE ở trạng thái Published;
- Chủ đầu tư tổ chức nghiệm thu sản phẩm BIM theo BEP đã được phê duyệt; kết quả nghiệm thu được ghi nhận bằng biên bản và lưu trên CDE.

# an-toan | AN TOÀN THÔNG TIN
## bao-mat | Bảo mật và an toàn thông tin dự án
Nền tảng {{ CDE }} và toàn bộ quy trình quản lý, khai thác, chia sẻ, lưu trữ dữ liệu BIM trên CDE tuân thủ quy định của pháp luật về an ninh mạng và an toàn, bảo mật thông tin. Các biện pháp kiểm soát được áp dụng gồm:

- Định danh người dùng cá nhân; không sử dụng tài khoản dùng chung;
- Phân quyền theo phân hệ và theo từng thư mục; quyền truy cập được cấp theo vai trò trong ma trận phân quyền tại {{ pl('pl_cde') }};
- Liên kết chia sẻ ra ngoài được bảo vệ bằng mã xác thực và có thời hạn hết hiệu lực;
- Nhật ký hoạt động ghi nhận đầy đủ thao tác tải lên, tải xuống, thay đổi quyền và đổi trạng thái CDE phục vụ kiểm toán;
- Sao lưu dữ liệu định kỳ; dữ liệu dự án được lưu trữ tại hạ tầng đặt trong lãnh thổ Việt Nam.

## sao-luu | Sao lưu, phục hồi và lưu trữ
- Dữ liệu trên CDE được sao lưu định kỳ theo quy định vận hành của nền tảng; nhóm thực hiện BIM không lưu bản làm việc duy nhất trên máy trạm cá nhân;
- Các phiên bản mô hình tại mỗi mốc chuyển giao được đóng gói và chuyển sang vùng Archived, giữ nguyên trạng để phục vụ đối chiếu;
- Khi kết thúc giai đoạn, toàn bộ mô hình ở định dạng gốc và định dạng trao đổi được bàn giao cho Chủ đầu tư theo thỏa thuận tại hợp đồng.
