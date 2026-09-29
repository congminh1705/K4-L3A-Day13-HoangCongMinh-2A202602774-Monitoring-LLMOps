# Nguồn evidence

Các ảnh dưới đây được chụp trực tiếp từ lệnh chạy trong repository hoặc project Langfuse cá nhân. Các lệnh Python dùng interpreter của virtualenv trên Windows. Ảnh Langfuse cần hiển thị project `day13-k4-l3a-2A202602774`; không chụp trang API Keys.

| Ảnh | Nguồn cụ thể |
|---|---|
| `01-pytest.png` | Terminal tại thư mục repository, chạy `.venv\Scripts\python.exe -m pytest -q`; ảnh ghi nhận 26 tests passed. |
| `02-log-validator.png` | Terminal, chạy `.venv\Scripts\python.exe scripts/validate_logs.py`; kết quả 100/100 trên `data/logs.jsonl` (202 records, 97 correlation IDs, 0 PII). |
| `03-dashboard-validator.png` | Terminal, chạy `.venv\Scripts\python.exe scripts/validate_dashboard.py`; kiểm tra dashboard contract có 6/6 panels hợp lệ. |
| `04-structured-log.png` | File `data/logs.jsonl`, record `event=response_sent`, `correlation_id=req-028f8a91`, timestamp `2026-09-29T08:01:27.368313Z`; structured log đã scrub PII. |
| `05-pii-redaction.png` | Terminal, chạy `.venv\Scripts\python.exe scripts/demo_pii_redaction.py`; dữ liệu kiểm tra là dữ liệu tổng hợp, không phải PII thật. |
| `06-trace-list.png` | Langfuse Cloud → project `day13-k4-l3a-2A202602774` → Tracing, date range 2026-09-29 15:21–15:22; filter root observations, workload `day13-agent-request`, 14 root traces. |
| `07-trace-waterfall.png` | Langfuse Cloud → cùng project → trace ID `27510434a1fb73890bf4bf983cad9908`; root `lab-agent-run` (0.15 s), children `fake-llm-generation` and `knowledge-retrieval`. |
| `08-trace-metadata.png` | Langfuse Cloud → cùng project → trace ID `3236e7c329b3e29be0978294e13bf883`, generation observation; prompt `day13-chat` v1, label `production`, correlation ID `req-945cdf1f`. |
| `09-prompt-versions.png` | Langfuse Cloud → cùng project → Prompts → `day13-chat`; v1 (`baseline`, `production`) and v2 (`candidate`, `latest`), created 2026-09-29 15:21:35–15:21:36. |
| `10-prompt-rollback.png` | Langfuse Cloud → cùng project → prompt `day13-chat`; v1 has `production` and `baseline`, v2 has `candidate`; linked generations shown for the rollback verification. |
| `11-dashboard-overview.png` | Ảnh chụp dashboard HTML cục bộ được tạo từ `data/logs.jsonl` bởi `.venv\Scripts\python.exe scripts/build_dashboard.py`; dashboard có sáu panel. |
| `12-incident-metric.png` | Ảnh chụp dashboard incident HTML được tạo từ `data/logs.jsonl` bởi `.venv\Scripts\python.exe scripts/build_dashboard.py --output submission/evidence/12-incident-metric.html`; snapshot lúc `2026-09-29 13:38:56 UTC`, 10 requests, P95 2,737 ms. HTML sinh tạm đã bỏ khỏi evidence; PNG là bản nộp. |
| `13-incident-log.png` | File `data/logs.jsonl`, record tại `2026-09-29T13:38:45Z`, `correlation_id=req-eb15ed00`, `event=response_sent`, `latency_ms=2737`, HTTP 200. |

Hai ảnh incident 12–13 là lần chạy tái hiện lúc 13:36–13:38 UTC. Chuỗi điều tra ban đầu lúc 09:40 UTC dùng correlation ID `req-00b906f4`, được đối chiếu với `data/logs.jsonl` và trace `0ae007add84a88ef92662fa2e6df6a7d`; bản trích xuất observation đã xác minh được lưu tại `14-incident-trace.txt`. Chưa có ảnh PNG Langfuse riêng cho trace này, vì vậy không gắn nhãn tệp text đó như ảnh chụp.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối, ví dụ:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không đưa secret, API key, PII thô hoặc evidence của học viên/lớp khác vào submission.
