---
title: Quy trình phát hiện và xử lý xung đột
short: Quy trình xung đột
summary: Phân loại, dung sai, mức độ nghiêm trọng, thời hạn xử lý và mẫu báo cáo xung đột
kind: appendix
orientation: landscape
---
# muc-dich | MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG
Phụ lục này là bộ phận không tách rời của Kế hoạch thực hiện BIM (mã hiệu {{ code('bep') }}), quy định cách phát hiện, phân loại và xử lý xung đột trên mô hình tổng hợp trong giai đoạn {{ stage.phrase }} của dự án {{ p.general.name }}.

# ma-tran | MA TRẬN KIỂM TRA XUNG ĐỘT
[Bảng#ma-tran|30,20,16,20,14] Ma trận kiểm tra xung đột
{{ tbl(['Cặp đối tượng kiểm tra', 'Loại xung đột', 'Dung sai', 'Trách nhiệm', 'Tần suất'], rows(p.coordination.clashes, 'pair', 'kind', 'tolerance', 'responsible', 'frequency')) }}

# phan-loai | PHÂN LOẠI VÀ MỨC ĐỘ NGHIÊM TRỌNG
[Bảng#muc-do|14,46,20,20] Mức độ nghiêm trọng và thời hạn xử lý
| Mức | Mô tả | Thời hạn xử lý | Điều kiện phát hành |
|---|---|---|---|
| Nghiêm trọng | Xung đột cứng giữa kết cấu chịu lực hoặc với công trình, thiết bị đang vận hành; ảnh hưởng an toàn hoặc khả năng thi công | Trước khi chia sẻ đợt | Bắt buộc xử lý xong |
| Cao | Xung đột cứng giữa các hệ thống, vi phạm khoảng hở yêu cầu | Trong đợt hiện hành | Xử lý xong hoặc có phương án được chấp thuận |
| Trung bình | Xung đột mềm, ảnh hưởng bảo trì, tiếp cận | Trong đợt kế tiếp | Có thể phát hành kèm ghi chú |
| Thấp | Sai khác nhỏ, không ảnh hưởng thi công | Theo kế hoạch cập nhật | Không chặn phát hành |

Thứ tự ưu tiên xử lý: kết cấu hiện hữu và thiết bị đang vận hành, kết cấu mới, hệ thống điện, hệ thống phòng cháy chữa cháy, thoát nước, các hạng mục còn lại.

# quy-trinh | QUY TRÌNH XỬ LÝ
- Điều phối BIM tích hợp mô hình tổng hợp, chạy kiểm tra theo ma trận và xuất danh sách xung đột;
- Mỗi xung đột là một vấn đề (Issue) trên CDE kèm vị trí 3D, hình ảnh, mức độ, bộ môn chịu trách nhiệm và thời hạn;
- Họp điều phối thống nhất phương án; bộ môn chịu trách nhiệm cập nhật mô hình;
- Điều phối BIM chạy lại kiểm tra, xác nhận và đóng vấn đề;
{% if f.supervisor %}
- Tư vấn giám sát kiểm tra độc lập mô hình đã chia sẻ, lập báo cáo xung đột và sai sót thiết kế; các ý kiến được xử lý theo cùng quy trình;
{% endif %}
- Hồ sơ của đợt chỉ được phát hành khi không còn xung đột mức Nghiêm trọng và Cao chưa xử lý.

# bao-cao | NỘI DUNG BÁO CÁO XUNG ĐỘT
Mỗi đợt, Điều phối BIM lập báo cáo xung đột gồm: danh sách mô hình và phiên bản được kiểm tra; ma trận đã chạy; thống kê số xung đột theo cặp và theo mức độ; danh sách xung đột còn mở kèm phương án và thời hạn; xác nhận đóng của các vấn đề đã xử lý.
