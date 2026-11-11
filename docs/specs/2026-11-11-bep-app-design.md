# Kế hoạch: Ứng dụng biên soạn BEP và phụ lục (bimpro)

## Bối cảnh

Bạn (Quản lý BIM, PECC2) đang soạn BEP thủ công bằng Word cho từng dự án. Bốn bộ BEP tham chiếu (Vũng Áng III – TKCS, Nhơn Hội 220kV – TKKT, Phong Hòa – TKCS, LTIA1 – BVTC) có chung một khung nội dung, chỉ khác dữ liệu dự án và mức độ theo giai đoạn. Soạn tay gây lỗi lệch giữa BEP và phụ lục: trong bộ VA3 có số phụ lục không khớp (PL-03/04/05), ký hiệu phiên bản lẫn lộn (A / v1 / P01 / Ấn bản 1), ngày MIDP đợt 2 sớm hơn đợt 1, danh mục mô hình trong TIDP khác Bảng phân chia mô hình.

Mục tiêu: một web app chạy cục bộ, sinh BEP và phụ lục dạng Word từ **thư viện mẫu theo giai đoạn + dữ liệu dự án**, không dùng AI, chỉ tiếng Việt. Ưu tiên trước mắt:

1. BEP mẫu giai đoạn thiết kế cơ sở (TKCS).
2. BEP giai đoạn BVTC cho dự án "Mở rộng mái che kho than NMNĐ Duyên Hải 3 MR" (DH3MR).

Repo `vannc92/bimpro` hiện trống; nhánh làm việc `claude/ecstatic-planck-nfnh68`.

## Các quyết định đã chốt với bạn

- Web app chạy cục bộ, mở bằng trình duyệt; dữ liệu nằm trong thư mục repo.
- Xuất Word (.docx). Phụ lục dạng bảng (MIDP/TIDP, RACI, LOD) cũng xuất docx, trang ngang.
- Nội dung = mẫu + dữ liệu dự án; chỉ tiếng Việt.
- App kết nối thư mục dự án ở mức **tra cứu và trích dẫn**: đọc chữ trong hồ sơ, tìm theo từ khóa, hiện đoạn trích kèm nguồn cạnh form. Không dùng AI; bạn tự quyết giá trị điền.

## Giả định của tôi (sửa nếu sai)

- Khung chuẩn lấy theo BEP Vũng Áng III (7 chương, bản mới nhất 11/2026); pre-BEP DH3MR cũng theo khung này.
- Máy bạn cài được Python 3.11+. Chạy bằng `run.bat`.
- Hồ sơ gốc trên OneDrive không chép vào repo; tôi đọc lại qua kết nối Microsoft 365 khi viết nội dung mẫu.
- Hình (sơ đồ tổ chức, lưu đồ phối hợp) là ô chèn ảnh do bạn tải lên, app không tự vẽ.

## Kiến trúc

Python 3.11+, FastAPI + Jinja2 + HTMX (không cần bước build), python-docx, pydantic, PyYAML, pytest.

```
pyproject.toml  run.bat  README.md
docs/specs/2026-11-11-bep-app-design.md      # bản thiết kế (chép từ kế hoạch này)
src/bimpro/
  models.py        # lược đồ dữ liệu dự án (pydantic)
  store.py         # đọc/ghi projects/<id>/project.yaml
  compose.py       # dự án + giai đoạn + thư viện -> cây tài liệu trung gian
  render_docx.py   # cây tài liệu -> .docx (bìa, header/footer, mục lục, đánh số Bảng/Hình)
  render_html.py   # cây tài liệu -> HTML xem trước
  validate.py      # kiểm tra nhất quán
  sources.py       # quét thư mục dự án, lập chỉ mục, tra cứu trích dẫn
  cli.py           # bimpro build <dự án> / bimpro serve
  web/             # app.py, templates/, static/
  library/
    base.docx              # style Word: Heading 1–3, thân bài, bảng, chú thích
    stages.yaml            # TKCS, TKKT, BVTC: giá trị mặc định theo giai đoạn
    legal.yaml             # danh mục văn bản pháp lý, tiêu chuẩn
    glossary.yaml  roles.yaml  raci.yaml  bim_uses.yaml  status_codes.yaml
    documents/bep.yaml     # dàn ý: mục, tiêu đề, giai đoạn áp dụng, tệp nội dung
    documents/pl_*.yaml    # dàn ý từng phụ lục
    sections/*.md          # nội dung mục: Markdown + biến {{ }} + lệnh chèn bảng
projects/
  _mau_tkcs/project.yaml
  dh3mr_bvtc/project.yaml
tests/
```

Luồng dữ liệu: `project.yaml` → `compose` (lọc mục và dòng theo giai đoạn, điền biến, áp nội dung ghi đè của dự án) → cây tài liệu → `render_docx` / `render_html`. Một cây tài liệu dùng chung cho xem trước và xuất, nên hai bên luôn khớp.

### Dữ liệu dự án (`models.py`)

Rút từ các biến riêng của 4 bộ tham chiếu:

- Thông tin chung: tên, mã dự án, địa điểm, quy mô, phân cấp, giai đoạn, hợp đồng, căn cứ riêng.
- Các bên và mã đơn vị; nhân sự (họ tên, đơn vị, vai trò, email).
- Tiến độ dự án và mốc chuyển giao.
- Nội dung áp dụng BIM (bắt buộc / tùy chọn), giới hạn phạm vi.
- Hạng mục áp dụng BIM; phân chia mô hình (khu vực, bộ môn, mã hiệu).
- Ma trận LOD / thông tin phi hình học theo cấu kiện.
- Phần mềm, phiên bản, định dạng; CDE (nền tảng, phân hệ, thư mục, phân quyền).
- Đơn vị, hệ tọa độ, điểm gốc.
- **Quy ước đặt tên cấu hình được theo dự án**: danh sách trường, độ dài, bảng mã. VA3 dùng 7 trường; DH3MR bị Chương V E-HSMT ấn định 5 trường với mã dự án `DH3MR.KT`.
- Kiểm soát tài liệu: mã tài liệu, phiên bản, người lập / kiểm tra / phê duyệt, header/footer.
- Văn bản pháp lý chọn từ danh mục, kèm "Áp dụng / Tham khảo".
- `overrides`: nội dung ghi đè theo mục, và bật/tắt mục.

Trường chưa có dữ liệu hiển thị `«…»` trong văn bản và được liệt kê trong bảng kiểm tra.

### Kết nối thư mục dự án (`sources.py`)

Vì app chạy trên máy bạn, nó đọc thẳng thư mục OneDrive đã đồng bộ (ví dụ `...\15-bim-dh3_mr_khothan_bvtc\input`). Chỉ đọc, không sửa hay chép hồ sơ gốc.

- Mỗi dự án lưu một hoặc nhiều đường dẫn thư mục đầu vào trong `project.yaml`.
- **Quét và lập chỉ mục:** trích chữ từ PDF (pypdf), Word (python-docx), Excel (openpyxl); lưu theo trang vào chỉ mục SQLite FTS5 tại `projects/<id>/.index/` (không đưa vào Git). Quét lại chỉ xử lý tệp đã đổi.
- **Tra cứu:** ô tìm kiếm cạnh mỗi nhóm form, có sẵn bộ từ khóa theo nhóm (ví dụ nhóm LOD: "LOD", "mức độ phát triển", "mức độ chi tiết"; nhóm CDE: "CDE", "môi trường dữ liệu chung"). Kết quả là đoạn trích kèm tên tệp và số trang; bấm để mở tệp gốc.
- **Chép vào trường:** nút chép đoạn trích vào trường đang nhập, và lưu nguồn (tệp, trang) cho trường đó để rà soát sau.
- **Tự lập từ tên tệp, không cần đọc nội dung:** danh sách mô hình đầu vào (`.rvt`, `.ifc`, `.nwd`), bản vẽ đầu vào (`.dwg`, `.pdf`), và danh mục văn bản trong thư mục pháp lý để đưa vào mục "Cơ sở thực hiện".
- **Giới hạn:** PDF scan không có lớp chữ thì không tìm được; app đánh dấu các tệp này là "không đọc được chữ" để bạn biết phải đọc tay. Không đọc nội dung bên trong `.rvt`/`.dwg`. Hồ sơ DH3MR tôi đã kiểm tra đều có lớp chữ.

### Kiểm tra nhất quán (`validate.py`)

- Số và mã phụ lục sinh từ một danh sách duy nhất, không gõ tay.
- Ký hiệu phiên bản thống nhất giữa bìa, footer, bảng kiểm soát phiên bản.
- Ngày các đợt chuyển giao tăng dần và nằm trong tiến độ dự án.
- Mọi mô hình trong MIDP/TIDP phải có trong bảng phân chia mô hình.
- Tên tập tin khớp cú pháp đặt tên của dự án.
- Tham chiếu "Bảng n", "mục n" trỏ tới đối tượng có thật.
- Danh sách trường còn `«…»`.

### Giao diện web

- Danh sách dự án; tạo mới từ mẫu theo giai đoạn hoặc nhân bản dự án cũ.
- Trang dự án: các nhóm form theo dữ liệu ở trên, bảng nhập dạng lưới thêm/xóa dòng.
- Trang tài liệu: cây mục bên trái, xem trước ở giữa, sửa nội dung mục (ghi đè) và bật/tắt mục.
- Bảng kiểm tra nhất quán; nút xuất BEP và từng phụ lục ra `projects/<id>/output/`.

## Các bước thực hiện

1. **Khung và lõi sinh tài liệu.** `models`, `store`, `compose`, `render_docx`, `cli`; `base.docx` với bìa, header/footer, mục lục, đánh số Bảng/Hình. Chép bản thiết kế vào `docs/specs/`.
2. **BEP mẫu TKCS.** Viết `bep.yaml` và các mục 1–7 theo khung VA3, danh mục pháp lý, thuật ngữ, vai trò, nội dung áp dụng BIM, quy trình 6 bước, kiểm tra ba lớp, an toàn thông tin. Dự án `_mau_tkcs` điền bằng dữ liệu minh họa trung tính. Sửa các lỗi đã thấy trong bản gốc (ví dụ "INWC", đoạn kinh tuyến trục).
3. **Phụ lục TKCS.** PL-01 RACI (35 nhiệm vụ, nhóm A–E), PL-02 đặt tên tập tin, PL-03 MIDP/TIDP, PL-04 thư mục và phân quyền CDE.
4. **Giao diện web.** Form dữ liệu, xem trước, sửa mục, kiểm tra, xuất.
5. **Kết nối thư mục dự án.** `sources.py`: quét, lập chỉ mục, tra cứu, chép trích dẫn vào trường, lập danh sách mô hình/bản vẽ/văn bản đầu vào.
6. **Giai đoạn BVTC và dự án DH3MR.** Bổ sung mục và dòng riêng BVTC: phát hiện xung đột, 4D, bóc khối lượng, mô hình hiện trạng, hoàn công, cấu trúc báo cáo BIM, vai trò TVGS. Thêm phụ lục ma trận LOD/LOI, quy trình xung đột, danh mục kiểm tra mô hình. Nhập `dh3mr_bvtc/project.yaml` từ pre-BEP, Chương V, NVKT, KHLCNT.

Mỗi bước là một hoặc vài commit trên nhánh; đẩy lên và mở PR nháp sau bước 1.

## Điểm cần bạn quyết khi soạn BEP DH3MR

Hồ sơ đầu vào có bốn chỗ chưa thống nhất. App sẽ để các giá trị này ở dạng chỉnh được; tôi điền theo đề xuất dưới đây và đánh dấu để bạn rà:

| Vấn đề | Hồ sơ nói gì | Đề xuất điền |
|---|---|---|
| Ai cung cấp CDE | KHLCNT và Chương V giao gói 02TV (TVGS); pre-BEP đề xuất vCDE của PECC2 | CDE do CĐT/TVGS cung cấp; vCDE là phương án tạm đến khi bàn giao |
| 5D | NVKT yêu cầu "dự toán chi phí (BIM 5D)"; pre-BEP chỉ bóc khối lượng hỗ trợ | Giữ như pre-BEP, nêu rõ giới hạn trong mục phạm vi |
| Hạn TKBVTC đợt 1 | NVKT: 15 ngày; Chương V mốc T1 và pre-BEP: 30 ngày | 30 ngày theo Chương V |
| Nhân sự, số hợp đồng, ngày hiệu lực | Chưa có | Để `«…»` |

Ràng buộc đã rõ từ E-HSMT: LOD 350, Revit 2024, VN-2000, đặt tên theo §3.3.3 Chương V, TCVN 14177-1/-2 và 14176-2 bắt buộc, BEP nộp trong 14 ngày từ ngày hợp đồng có hiệu lực, BIM đóng thành "Tập 6 – Thiết kế BIM".

## Ngoài phạm vi đợt này

Xuất Excel/PDF, song ngữ, AI hỗ trợ soạn, đăng nhập nhiều người dùng, tự vẽ sơ đồ, các sản phẩm BIM khác ngoài BEP (báo cáo BIM, báo cáo xung đột). Lược đồ giai đoạn để sẵn chỗ cho TKKT, thi công, hoàn công.

## Kiểm chứng

- `pytest`: compose lọc đúng theo giai đoạn; mỗi quy tắc kiểm tra bắt đúng lỗi tương ứng; docx sinh ra có đủ đề mục và số bảng theo dàn ý.
- `bimpro build projects/_mau_tkcs` và `projects/dh3mr_bvtc`: mở lại docx bằng python-docx để đối chiếu mục lục với dàn ý VA3 / pre-BEP; chuyển sang PDF và chụp trang để soát trình bày (bìa, header/footer, bảng ngang).
- Kết nối thư mục: tải một phần hồ sơ DH3MR về thư mục tạm, quét, và kiểm tra tìm "LOD" trả về đúng đoạn "LOD … ở mức 350" tại §3.3.4 Chương V kèm số trang; tệp không có lớp chữ được đánh dấu.
- Chạy web app, dùng Playwright đi hết luồng: tạo dự án từ mẫu TKCS → sửa dữ liệu → xem trước → xuất; chụp màn hình gửi bạn.
- Gửi bạn hai tệp docx (BEP mẫu TKCS, BEP DH3MR) để rà nội dung chuyên môn.
