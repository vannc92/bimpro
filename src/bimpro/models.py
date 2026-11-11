"""Lược đồ dữ liệu dự án.

Mỗi nhóm (lớp con của ``Group``) là một trang nhập liệu trên giao diện web.
Nhãn tiếng Việt lấy từ ``title`` của trường; ``long=True`` hiển thị ô nhập nhiều dòng.
Các trường ``values``/``dates`` dạng chuỗi dùng dấu ``;`` để tách các cột.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class M(BaseModel):
    model_config = ConfigDict(extra="ignore")


def F(title: str, default="", long: bool = False, **kw):
    extra = {"long": True} if long else None
    return Field(default, title=title, json_schema_extra=extra, **kw)


def L(title: str):
    return Field(default_factory=list, title=title)


# ---------------------------------------------------------------- dòng bảng


class KV(M):
    label: str = F("Thông tin")
    value: str = F("Nội dung", long=True)


class Party(M):
    code: str = F("Mã")
    role: str = F("Vai trò trong dự án")
    name: str = F("Tên đơn vị")
    short: str = F("Tên viết tắt")


class Person(M):
    name: str = F("Họ và tên")
    org: str = F("Đơn vị")
    role: str = F("Vai trò")
    email: str = F("Email")


class Milestone(M):
    task: str = F("Nội dung công việc")
    time: str = F("Thời gian dự kiến")


class Standard(M):
    name: str = F("Tên")
    date: str = F("Ngày ban hành")
    description: str = F("Mô tả")
    requirement: str = F("Yêu cầu", "Áp dụng")


class BimUse(M):
    name: str = F("Nội dung áp dụng BIM")
    required: bool = Field(True, title="Bắt buộc")
    description: str = F("Mô tả", long=True)


class ModelArea(M):
    area: str = F("Khu vực/hệ thống")
    discipline: str = F("Bộ môn")
    scope: str = F("Phạm vi cấu kiện thể hiện trong mô hình", long=True)


class ModelFile(M):
    area: str = F("Khu vực/hệ thống")
    content: str = F("Mô hình thành phần")
    discipline: str = F("Bộ môn")
    code: str = F("Mã hiệu mô hình")


class LodRow(M):
    group: str = F("Nhóm")
    element: str = F("Tên cấu kiện")
    lod: str = F("LOD")
    info: str = F("Thông tin phi hình học cần đính kèm")


class Software(M):
    use: str = F("Ứng dụng")
    responsible: str = F("Trách nhiệm")
    software: str = F("Phần mềm và phiên bản")
    native: str = F("Định dạng gốc")
    exchange: str = F("Định dạng chuyển giao")


class Deliverable(M):
    name: str = F("Sản phẩm BIM")
    format: str = F("Định dạng")
    milestone: str = F("Mốc chuyển giao")


class Check(M):
    name: str = F("Nội dung kiểm tra")
    description: str = F("Mô tả")
    responsible: str = F("Trách nhiệm")
    software: str = F("Phần mềm")
    frequency: str = F("Tần suất")


class CodeItem(M):
    table: str = F("Bảng mã (tên trường)")
    code: str = F("Mã")
    meaning: str = F("Diễn giải")
    note: str = F("Ghi chú")


class NamingField(M):
    name: str = F("Trường thông tin")
    length: str = F("Số ký tự")
    required: str = F("Bắt buộc", "Có")
    example: str = F("Ví dụ")
    note: str = F("Diễn giải")


class NameExample(M):
    name: str = F("Tên tập tin")
    meaning: str = F("Diễn giải")


class StatusCode(M):
    code: str = F("Mã")
    name: str = F("Tên")
    zone: str = F("Vùng CDE")
    meaning: str = F("Ý nghĩa")


class Revision(M):
    rev: str = F("Phiên bản")
    date: str = F("Ngày")
    prepared: str = F("Thực hiện")
    checked: str = F("Kiểm tra")
    approved: str = F("Phê duyệt")
    description: str = F("Mô tả")


class RaciRole(M):
    code: str = F("Mã")
    role: str = F("Vai trò")
    org: str = F("Đơn vị")


class RaciTask(M):
    group: str = F("Nhóm nhiệm vụ")
    ref: str = F("TT")
    task: str = F("Nhiệm vụ")
    values: str = F("R/A/C/I theo thứ tự vai trò, cách nhau bằng ;")


class Module(M):
    name: str = F("Phân hệ")
    purpose: str = F("Mục đích sử dụng trong dự án")


class FolderRow(M):
    level1: str = F("Thư mục cấp 1")
    level2: str = F("Thư mục cấp 2")
    content: str = F("Nội dung lưu trữ")
    suit: str = F("Mã phù hợp")


class PermRow(M):
    folder: str = F("Thư mục")
    values: str = F("Quyền theo thứ tự vai trò, cách nhau bằng ;")


class Transition(M):
    change: str = F("Chuyển trạng thái")
    condition: str = F("Điều kiện")
    by: str = F("Người thực hiện")
    function: str = F("Chức năng CDE")


class Round(M):
    name: str = F("Đợt chuyển giao")
    date: str = F("Ngày chuyển giao (dd/mm/yyyy)")


class MidpRow(M):
    group: str = F("Loại sản phẩm")
    file: str = F("Tên tập tin (mã hiệu)")
    description: str = F("Mô tả")
    native: str = F("Định dạng gốc")
    exchange: str = F("Định dạng trao đổi")
    lead: str = F("Bên chủ trì")
    dates: str = F("Ngày theo từng đợt, cách nhau bằng ;")


class TidpRow(M):
    team: str = F("Nhóm thực hiện")
    task: str = F("Nhiệm vụ")
    product: str = F("Sản phẩm (mã hiệu)")
    person: str = F("Người thực hiện")
    inputs: str = F("Đầu vào cần có")
    start: str = F("Bắt đầu")
    finish: str = F("Hoàn thành")
    note: str = F("Ghi chú")


class ClashRow(M):
    pair: str = F("Cặp đối tượng kiểm tra")
    kind: str = F("Loại xung đột")
    tolerance: str = F("Dung sai")
    responsible: str = F("Trách nhiệm")
    frequency: str = F("Tần suất")


class QcItem(M):
    group: str = F("Nhóm")
    ref: str = F("TT")
    item: str = F("Nội dung kiểm tra")


class Param(M):
    name: str = F("Tên tham số")
    kind: str = F("Kiểu dữ liệu")
    scope: str = F("Instance/Type")
    applies: str = F("Áp dụng cho")
    description: str = F("Mô tả")


class DocRef(M):
    doc: str = F("Tài liệu (mã trong thư viện)")
    code: str = F("Mã hiệu tài liệu")
    enabled: bool = Field(True, title="Phát hành")


class Override(M):
    enabled: bool = True
    body: str | None = None


# -------------------------------------------------------------------- nhóm


class Group(M):
    """Một nhóm dữ liệu = một trang nhập liệu."""


class General(Group):
    name: str = F("Tên dự án")
    code: str = F("Mã dự án")
    owner_short: str = F("Chủ đầu tư – tên viết tắt (in ở đầu trang)")
    author_short: str = F("Đơn vị lập BEP – tên viết tắt")
    author_name: str = F("Đơn vị lập BEP – tên đầy đủ")
    author_role: str = F("Cách xưng của đơn vị lập BEP trong văn bản", "Tư vấn")
    package: str = F("Tên gói thầu (nếu có)")
    report_title: str = F("Tên hồ sơ in ở đầu trang (ví dụ: BÁO CÁO NGHIÊN CỨU KHẢ THI)")
    info: list[KV] = L("Bảng thông tin chung của dự án")
    parties: list[Party] = L("Các bên tham gia")


class Basis(Group):
    legal: list[str] = L("Cơ sở pháp lý (mỗi dòng một văn bản)")
    contracts: list[str] = L("Hợp đồng, văn bản riêng của dự án (mỗi dòng một văn bản)")
    note: str = F("Đoạn nêu lý do áp dụng BIM của dự án", long=True)
    standards: list[Standard] = L("Tiêu chuẩn và quy định áp dụng")


class Schedule(Group):
    milestones: list[Milestone] = L("Các mốc tiến độ chính của dự án")


class Features(M):
    drawings: bool = Field(False, title="Triển khai bản vẽ từ mô hình")
    clash: bool = Field(False, title="Kiểm tra va chạm tự động (clash detection)")
    qto: bool = Field(False, title="Bóc tách khối lượng từ mô hình")
    sim4d: bool = Field(False, title="Mô phỏng tiến độ thi công (4D)")
    existing: bool = Field(False, title="Mô hình hiện trạng")
    asbuilt: bool = Field(False, title="Mô hình hoàn công")
    supervisor: bool = Field(False, title="Có tư vấn giám sát/quản lý BIM tham gia")


class Bim(Group):
    lod: str = F("Mức LOD chung của giai đoạn", "200")
    features: Features = Field(default_factory=Features, title="Nội dung triển khai")
    objectives: list[str] = L("Mục tiêu áp dụng BIM (mỗi dòng một mục tiêu)")
    uses: list[BimUse] = L("Nội dung áp dụng BIM")
    limits: list[str] = L("Giới hạn phạm vi áp dụng BIM (mỗi dòng một ý)")
    scope_items: list[str] = L("Hạng mục áp dụng BIM (mỗi dòng một hạng mục)")


class Org(Group):
    chart_image: str = F("Tệp ảnh sơ đồ tổ chức (đặt trong thư mục dự án)")
    people: list[Person] = L("Nhân sự chính tham gia dự án")
    raci_roles: list[RaciRole] = L("Vai trò trong ma trận RACI")
    raci: list[RaciTask] = L("Ma trận RACI")


class Models(Group):
    disciplines: str = F("Các bộ môn tham gia dựng mô hình", "kiến trúc, kết cấu, công nghệ, điện")
    areas: list[ModelArea] = L("Phân chia mô hình theo khu vực/hệ thống và bộ môn")
    files: list[ModelFile] = L("Danh mục mô hình và mã hiệu")
    lod: list[LodRow] = L("Mức độ phát triển thông tin theo cấu kiện")
    params: list[Param] = L("Bộ tham số thông tin chung (LOI)")


class Cde(Group):
    name: str = F("Tên nền tảng CDE", "vCDE")
    provider: str = F("Đơn vị cung cấp, vận hành")
    intro: str = F("Đoạn giới thiệu nền tảng và điều kiện áp dụng", long=True)
    size_limit: str = F("Giới hạn dung lượng tệp IFC", "500 MB")
    modules: list[Module] = L("Các phân hệ CDE áp dụng")
    status_codes: list[StatusCode] = L("Mã trạng thái")
    folders: list[FolderRow] = L("Cây thư mục")
    perm_roles: str = F("Các vai trò trong ma trận phân quyền, cách nhau bằng ;")
    perms: list[PermRow] = L("Ma trận phân quyền")
    transitions: list[Transition] = L("Chuyển trạng thái")


class Delivery(Group):
    it: str = F("Hạ tầng công nghệ thông tin", long=True)
    formats: list[str] = L("Định dạng trao đổi (mỗi dòng một ý)")
    deliverables: list[Deliverable] = L("Kế hoạch chuyển giao thông tin")
    review_products: str = F("Danh mục sản phẩm phục vụ thẩm định/nghiệm thu", long=True)
    rounds: list[Round] = L("Các đợt chuyển giao (MIDP)")
    midp: list[MidpRow] = L("MIDP – kế hoạch chuyển giao thông tin tổng thể")
    tidp: list[TidpRow] = L("TIDP – kế hoạch chuyển giao thông tin nhiệm vụ")
    report_outline: list[str] = L("Cấu trúc Báo cáo BIM (mỗi dòng một mục; để trống nếu không trình bày)")


class Coordination(Group):
    process_image: str = F("Tệp ảnh lưu đồ quy trình phối hợp")
    checks: list[Check] = L("Cách thức phối hợp và kiểm tra mô hình")
    clashes: list[ClashRow] = L("Ma trận kiểm tra xung đột")
    software: list[Software] = L("Phần mềm và phiên bản sử dụng")
    units: str = F("Đơn vị đo lường", long=True)
    coord_system: str = F("Hệ tọa độ, cao độ", long=True)
    coord_params: str = F("Thông số hệ tọa độ và điểm gốc dự án", long=True)
    exchange_extra: list[str] = L("Quy định trao đổi dữ liệu bổ sung của dự án (mỗi dòng một ý)")
    qc: list[QcItem] = L("Danh mục kiểm tra chất lượng mô hình")


class Naming(Group):
    syntax: str = F("Cú pháp đặt tên tập tin")
    example: str = F("Ví dụ và diễn giải", long=True)
    regex: str = F("Biểu thức kiểm tra tên (regex, có thể để trống)")
    fields: list[NamingField] = L("Các trường thông tin")
    codes: list[CodeItem] = L("Bảng mã các trường")
    examples: list[NameExample] = L("Ví dụ đặt tên")


class DocControl(Group):
    revision: str = F("Phiên bản hiện hành", "A")
    issue_text: str = F("Dòng phiên bản in ở cuối trang (ví dụ: Bản A - Tháng 11/2026)")
    month: str = F("Thời gian in trên bìa (ví dụ: Tháng 11/2026)")
    prepared_by: str = F("Người thực hiện")
    checked_by: str = F("Người kiểm tra")
    approved_by: str = F("Người phê duyệt (để trống nếu không in)")
    sign_date: str = F("Ngày ký in trên bìa (ví dụ: …/11/2026)")
    documents: list[DocRef] = L("Danh mục tài liệu phát hành (BEP và phụ lục, theo thứ tự)")
    revisions: list[Revision] = L("Bảng kiểm soát phiên bản")


class Sources(Group):
    folders: list[str] = L("Thư mục hồ sơ đầu vào của dự án (mỗi dòng một đường dẫn)")


GROUPS: dict[str, tuple[str, type[Group]]] = {
    "general": ("Thông tin chung", General),
    "basis": ("Căn cứ và tiêu chuẩn", Basis),
    "schedule": ("Tiến độ dự án", Schedule),
    "bim": ("Mục tiêu và nội dung BIM", Bim),
    "org": ("Tổ chức và nhân sự", Org),
    "models": ("Phân chia mô hình và LOD", Models),
    "cde": ("Môi trường dữ liệu chung", Cde),
    "delivery": ("Chuyển giao thông tin", Delivery),
    "coordination": ("Phối hợp, phần mềm, tọa độ", Coordination),
    "naming": ("Quy ước đặt tên", Naming),
    "doc": ("Kiểm soát tài liệu", DocControl),
    "sources": ("Thư mục hồ sơ đầu vào", Sources),
}


class Project(M):
    id: str = ""
    title: str = ""
    stage: str = "TKCS"
    is_template: bool = False
    general: General = Field(default_factory=General)
    basis: Basis = Field(default_factory=Basis)
    schedule: Schedule = Field(default_factory=Schedule)
    bim: Bim = Field(default_factory=Bim)
    org: Org = Field(default_factory=Org)
    models: Models = Field(default_factory=Models)
    cde: Cde = Field(default_factory=Cde)
    delivery: Delivery = Field(default_factory=Delivery)
    coordination: Coordination = Field(default_factory=Coordination)
    naming: Naming = Field(default_factory=Naming)
    doc: DocControl = Field(default_factory=DocControl)
    sources: Sources = Field(default_factory=Sources)
    # ghi đè nội dung theo mục: {mã tài liệu: {mã mục: Override}}
    overrides: dict[str, dict[str, Override]] = Field(default_factory=dict)
    # nguồn trích dẫn của từng trường: {đường dẫn trường: "tệp, tr. N"}
    citations: dict[str, str] = Field(default_factory=dict)
