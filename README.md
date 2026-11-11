# bimpro

Ứng dụng chạy cục bộ để biên soạn Kế hoạch thực hiện BIM (BEP) và các phụ lục theo giai đoạn dự án. Nội dung sinh từ thư viện mẫu cộng dữ liệu dự án, xuất ra Word.

## Chạy

Cần Python 3.11 trở lên.

- Windows: bấm đúp `run.bat` (lần đầu sẽ tự cài), trình duyệt mở `http://127.0.0.1:8765`.
- Dòng lệnh:

```bash
pip install -e .
```

```bash
bimpro serve
```

Xuất không cần giao diện:

```bash
bimpro build projects/dh3mr_bvtc
```

```bash
bimpro check projects/dh3mr_bvtc
```

Tệp Word nằm ở `projects/<mã>/output/`. Khi mở, Word hỏi cập nhật trường: chọn Yes để có mục lục và số trang.

## Dự án có sẵn

| Thư mục | Nội dung |
|---|---|
| `projects/_mau_tkcs` | BEP mẫu giai đoạn thiết kế cơ sở, 4 phụ lục. Dữ liệu riêng để trống, in `«…»`. |
| `projects/dh3mr_bvtc` | BEP giai đoạn BVTC dự án Mở rộng mái che kho than NMNĐ Duyên Hải 3 MR, 7 phụ lục. |

Tạo dự án mới ở trang chủ bằng cách nhân bản một dự án có sẵn.

## Cách dùng

1. **Dữ liệu dự án**: điền từng nhóm ở thanh bên. Bảng nhập dạng lưới, thêm/xóa/đổi thứ tự dòng.
2. **Hồ sơ đầu vào**: khai báo đường dẫn thư mục hồ sơ (ví dụ thư mục OneDrive đã đồng bộ), bấm quét. Ở mỗi nhóm dữ liệu, ô tra cứu bên phải tìm trong PDF, Word, Excel; "Chép vào ô" đưa đoạn trích vào ô đang chọn và lưu nguồn (tệp, trang). PDF scan không có lớp chữ được đánh dấu để đọc tay.
3. **Xem trước, sửa mục**: bấm ✎ cạnh một mục để sửa nội dung riêng cho dự án hoặc tắt mục đó. "Khôi phục nội dung mẫu" để quay về thư viện.
4. **Kiểm tra nhất quán**: lỗi về số phụ lục, mã hiệu, phiên bản, ngày chuyển giao, mô hình trong MIDP/TIDP, ma trận RACI; và danh sách chỗ còn `«…»`.
5. **Xuất Word**.

## Cấu trúc

- `src/bimpro/library/documents/*.md`: mẫu BEP và phụ lục (Markdown rút gọn + biến Jinja2). Cú pháp ghi ở đầu `src/bimpro/compose.py`.
- `src/bimpro/library/stages.yaml`: tên gọi theo giai đoạn (TKCS, TKKT, BVTC).
- `src/bimpro/models.py`: lược đồ dữ liệu dự án; mỗi nhóm là một trang nhập liệu.
- `projects/<mã>/project.yaml`: dữ liệu một dự án.
- `docs/specs/`: bản thiết kế.

Số phụ lục (PL-01, PL-02…) tự đánh theo thứ tự trong nhóm "Kiểm soát tài liệu"; thêm phụ lục bằng cách thêm dòng với mã mẫu (`pl_raci`, `pl_naming`, `pl_midp`, `pl_cde`, `pl_lod`, `pl_clash`, `pl_qc`).

## Kiểm thử

```bash
pip install -e ".[dev]"
```

```bash
pytest
```
