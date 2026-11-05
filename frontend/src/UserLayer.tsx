import { useState } from "react";
import "./UserLayer.css";

type ModuleStatus = "NOT_RUN" | "BLOCKED" | "FAIL" | "VERIFIED";
type WorkModule = { name: string; priority: "P0" | "P1"; status: ModuleStatus; blocker: string };
const modules: WorkModule[] = [
  { name: "Core pytest", priority: "P0", status: "NOT_RUN", blocker: "Require run-specific CI/Sandbox evidence" },
  { name: "BX42 parser", priority: "P0", status: "NOT_RUN", blocker: "Strict pipe/JSON contract evidence missing" },
  { name: "Signal → Risk → Paper E2E", priority: "P0", status: "BLOCKED", blocker: "Node-to-paper authenticated bridge not verified" },
  { name: "Dashboard API read-only", priority: "P1", status: "NOT_RUN", blocker: "API contract and browser QA required" },
  { name: "MT5 v0.1 Strategy Tester", priority: "P0", status: "BLOCKED", blocker: "MetaEditor F7 and tester log missing" },
  { name: "Exness API adapter", priority: "P1", status: "NOT_RUN", blocker: "Account eligibility and read-only API test required" },
  { name: "MT5 bridge read-only", priority: "P1", status: "NOT_RUN", blocker: "Terminal and data mapping tests required" },
  { name: "n8n workflow connection", priority: "P1", status: "NOT_RUN", blocker: "Authentication and webhook tests required" }
];
const connections = [
  { name: "Exness API", detail: "Independent Exness API account", transport: "REST / WebSocket" },
  { name: "Exness MT5", detail: "MT5 terminal bridge", transport: "Python / MQL5" },
  { name: "n8n", detail: "Notifications and workflow orchestration only", transport: "Webhook" }
];

export default function UserLayer({ page }: { page: "Broker Connections" | "Work 200 Verification" }) {
  const [filter, setFilter] = useState<ModuleStatus | "ALL">("ALL");
  const [selected, setSelected] = useState("Exness API");
  const [mode, setMode] = useState("REVIEW_ONLY");
  const shown = modules.filter((m) => filter === "ALL" || m.status === filter);
  return <section className="user-layer">
    <div className="ul-banner" role="status"><strong>BAOXTRA V3.1 · UI PREVIEW / GIAO DIỆN MẪU</strong><span>REVIEW_ONLY · PAPER FIRST · NO LIVE ORDERS</span></div>
    <div className="ul-heading"><h1>{page === "Broker Connections" ? "Kết nối sàn / Broker Connections" : "Kiểm chứng Work 200 / Verification"}</h1><p>Không có dữ liệu broker trực tiếp. Mọi trạng thái bên dưới là kế hoạch kiểm chứng, không phải kết quả test mới.</p></div>
    {page === "Broker Connections" ? <>
      <div className="ul-grid">{connections.map((item) => <button key={item.name} className={"ul-card " + (selected === item.name ? "ul-selected" : "")} onClick={() => setSelected(item.name)} aria-pressed={selected === item.name}>
        <strong>{item.name}</strong><small>{item.detail}</small><small>{item.transport}</small><span className="ul-tag">CHƯA KẾT NỐI / DISCONNECTED</span>
      </button>)}</div>
      <div className="ul-panel"><h2>{selected} — Thông tin kết nối</h2><p>Trạng thái: CHƯA KẾT NỐI. Không có API key, token, account ID hay endpoint giao dịch nào được lưu trong trình duyệt.</p>
        <label htmlFor="ul-mode">Chế độ thiết kế / Mode</label>
        <select id="ul-mode" value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="REVIEW_ONLY">REVIEW_ONLY (đang hỗ trợ)</option>
          <option value="PAPER">PAPER (thiết kế tương lai)</option>
          <option value="SEMI_AUTO">SEMI-AUTO (chưa khả dụng)</option>
          <option value="FULL_AUTO">FULL-AUTO (chưa khả dụng)</option>
        </select>
        <p className="ul-warning">Lựa chọn chỉ thay đổi bản xem trước. Không gửi yêu cầu mạng, không đặt lệnh, không mở quyền thực thi. Chế độ hiện hành của backend vẫn là REVIEW_ONLY.</p>
        <div className="ul-checks"><span>✓ No order submission</span><span>✓ No browser secrets</span><span>✓ No live broker permission</span></div>
      </div>
    </> : <>
      <div className="ul-panel"><h2>Bộ lọc kiểm thử / Evidence Status</h2><label htmlFor="ul-status">Trạng thái</label><select id="ul-status" value={filter} onChange={e => setFilter(e.target.value as ModuleStatus | "ALL")}><option value="ALL">Tất cả / All</option><option value="VERIFIED">VERIFIED</option><option value="FAIL">FAIL</option><option value="BLOCKED">BLOCKED</option><option value="NOT_RUN">NOT_RUN</option></select><p className="ul-warning">VERIFIED chỉ được cấp sau khi có commit, lệnh chạy, exit code và evidence đối chiếu. Trạng thái tại đây là seed kế hoạch, không đồng bộ GitHub.</p></div>
      <div className="ul-module-list">{shown.map(m => <article className="ul-module" key={m.name}><div><strong>{m.name}</strong><small>{m.blocker}</small></div><span>{m.priority}</span><span className="ul-tag">{m.status}</span></article>)}{shown.length === 0 && <p>Không có module trong bộ lọc này.</p>}</div>
      <div className="ul-panel"><h2>Evidence checklist / Danh sách bằng chứng</h2><p>Repository · Branch · Commit SHA · Test command · Exit code · Logs · Environment · Timestamp · Artifact link.</p><p>GitHub CI, Sandbox pytest, Paper E2E và MT5 Strategy Tester phải được xác minh độc lập.</p></div>
    </>}
  </section>;
}
