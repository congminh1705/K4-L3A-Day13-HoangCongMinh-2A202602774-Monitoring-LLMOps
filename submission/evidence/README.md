# Nguồn evidence

Các ảnh dưới đây được chụp trực tiếp từ lệnh chạy trong repository hoặc project Langfuse cá nhân. Các lệnh Python dùng interpreter của virtualenv trên Windows. Ảnh Langfuse cần hiển thị project `day13-k4-l3a-2A202602774`; không chụp trang API Keys.

| Ảnh | Nguồn cụ thể |
|---|---|
| `01-pytest.png` | Working directory `D:\Day13-Lab\K4-L3A-Day13-HoangCongMinh-2A202602774-Monitoring-LLMOps`; lệnh `.venv\Scripts\python.exe -m pytest -q`; kết quả trong ảnh: 26 passed, 1.50 s. |
| `02-log-validator.png` | Cùng working directory; lệnh `.venv\Scripts\python.exe scripts/validate_logs.py`; đúng lần chụp trong ảnh: 54 records, 23 correlation IDs, 0 PII, 100/100. Đây là output cũ hơn lần chạy 202 records được ghi trong báo cáo. |
| `03-dashboard-validator.png` | Cùng working directory; lệnh `.venv\Scripts\python.exe scripts/validate_dashboard.py`; output `HỢP LỆ: 6/6 panel có trong dashboard contract.` |
| `04-structured-log.png` | [data/logs.jsonl, dòng 8](../../data/logs.jsonl#L8): `response_sent`, `correlation_id=req-028f8a91`, session `s04`, timestamp `2026-09-29T08:01:27.368313Z`. Ảnh là bản chụp riêng dòng JSON này. |
| `05-pii-redaction.png` | Cùng working directory; lệnh `.venv\Scripts\python.exe scripts/demo_pii_redaction.py` (mã tại `scripts/demo_pii_redaction.py`); ảnh ghi output demo với bốn giá trị synthetic và xác nhận tất cả đã redacted trước khi ghi JSONL tạm. |
| `06-trace-list.png` | Langfuse Cloud, Organization `congminh1705's Organization`, project `day13-k4-l3a-2A202602774` (project ID `cmumde3dx161aod0d7wybwtt`; [Tracing page](https://cloud.langfuse.com/project/cmumde3dx161aod0d7wybwtt/traces)); date range Sep 29, 15:21–15:22; filter `isRootObservation:true`; `Trace Name=day13-agent-request`; kết quả 14 root traces. |
| `07-trace-waterfall.png` | Langfuse Cloud → cùng project → trace ID `27510434a1fb73890bf4bf983cad9908`; root `lab-agent-run` 0.15 s, children `fake-llm-generation` và `knowledge-retrieval`; generation cost `$0.002352`, 196 tokens. Mở trace này từ Tracing page ở dòng trên. |
| `08-trace-metadata.png` | Langfuse Cloud → cùng project → trace ID `3236e7c329b3e29be0978294e13bf883` → observation `fake-llm-generation`; metadata hiển thị prompt `day13-chat` v1, label `production`, correlation `req-945cdf1f`, timestamp `2026-09-29 15:21:30.634`. Mở trace này từ Tracing page ở dòng trên. |
| `09-prompt-versions.png` | Cùng organization/project → Prompts → `day13-chat` → Versions; v1 (`baseline`, `production`) được tạo `15:21:35 29/9/2026`; v2 (`candidate`, `latest`) được tạo `15:21:36 29/9/2026`. |
| `10-prompt-rollback.png` | Cùng organization/project → Prompts → `day13-chat` → chọn version #1 → Linked Generations; ảnh hiển thị v1 đang gắn `production` + `baseline`, v2 gắn `candidate`, cùng bảng 20 linked generation observations. |
| `11-dashboard-overview.png` | Tạo bởi `.venv\Scripts\python.exe scripts/build_dashboard.py` (script mặc định dùng `config/dashboard.yaml` và [data/logs.jsonl](../../data/logs.jsonl), ghi HTML tạm `submission/evidence/11-dashboard-overview.html`); PNG chụp snapshot `2026-09-29 10:50:16 UTC`: 60 requests, P50 151 ms, P95 153 ms, sáu panel. HTML tạm không nằm trong submission. |
| `12-incident-metric.png` | Tạo bởi `.venv\Scripts\python.exe scripts/build_dashboard.py --output submission/evidence/12-incident-metric.html`; nguồn log là [data/logs.jsonl](../../data/logs.jsonl); PNG chụp snapshot `2026-09-29 13:38:56 UTC`: 10 requests, P50 2,651 ms, P95/P99 2,737 ms, error 0%, retrieval 100%. HTML tạm không nằm trong submission. |
| `13-incident-log.png` | [data/logs.jsonl, dòng 193](../../data/logs.jsonl#L193): `response_sent`, `correlation_id=req-eb15ed00`, timestamp `2026-09-29T13:38:45.561342Z`, latency 2,737 ms, HTTP 200. Ảnh terminal hiển thị cả dòng 192 (request) và dòng 193 (response). |

Hai ảnh incident 12–13 là lần chạy tái hiện lúc 13:36–13:38 UTC. Chuỗi điều tra ban đầu lúc 09:40 UTC dùng correlation ID `req-00b906f4`, được đối chiếu với `data/logs.jsonl` và trace `0ae007add84a88ef92662fa2e6df6a7d`; bản trích xuất observation đã xác minh được lưu tại `14-incident-trace.txt`. Chưa có ảnh PNG Langfuse riêng cho trace này, vì vậy không gắn nhãn tệp text đó như ảnh chụp.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối, ví dụ:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không đưa secret, API key, PII thô hoặc evidence của học viên/lớp khác vào submission.
