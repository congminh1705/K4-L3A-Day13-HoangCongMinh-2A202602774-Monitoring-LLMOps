# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Hoàng Công Minh
- **MSSV:** 2A202602774
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/congminh1705/K4-L3A-Day13-HoangCongMinh-2A202602774-Monitoring-LLMOps.git
- **Commit SHA cuoi:** xem `git log -1 --format=%H` sau commit CP4 va nop SHA nay tren LMS.
- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (cohort K4).
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602774`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Final pytest | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` (dashboard snapshot; source details in `evidence/README.md`) |
| Incident log | `evidence/13-incident-log.png` (`data/logs.jsonl`; source details in `evidence/README.md`) |
| Incident trace | `evidence/14-incident-trace.txt` (verified Langfuse observation extract; PNG not captured) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 (202 records, 97 correlation IDs, 0 PII leaks; CP4 run) | CP1 đạt. |
| `validate_dashboard.py` | 6/6 valid panels | 6/6 valid panels | Runtime screenshot: `evidence/11-dashboard-overview.png`. |
| `pytest` | 22 passed | 26 passed | Dùng `-p no:cacheprovider` và `--basetemp` trong workspace vì thư mục tạm mặc định bị từ chối quyền truy cập. |
| Số traces hợp lệ | 1 root observation | 12 root + 24 child observations | Có retrieval và generation cho cả 12 traces. |
| Số PII leak | 0 | 0 | Log validator không phát hiện PII. |
| Latency P95 / TTFT P95 | | 1,168 ms / 50 ms | Từ 10 response gần nhất trong structured log. |
| Retrieval success rate | | 100% | Từ tool success records trong structured log. |

### CP0 — Setup và baseline

- `/health` trả `ok: true`, `tracing_enabled: true`.
- `python scripts/load_test.py`: 10/10 request nhận HTTP 200; `data/logs.jsonl` tăng từ 24 lên 44 records.
- Langfuse API xác nhận project `day13-k4-l3a-2A202602774` và observation `lab-agent-run` tại `2026-09-29T07:52:59.702Z`, trace ID `8619664a717383a7701ed7b1a74b4691`.
- `validate_logs.py` báo 30/100 là baseline dự kiến của starter; correlation ID và log enrichment thuộc CP1.

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa context cũ ở đầu request, nhận `x-request-id` hợp lệ hoặc sinh `req-<8-hex>`, bind vào structlog, truyền vào agent và trả lại qua response header.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, cùng timestamp, level, event và `correlation_id`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Processor `scrub_event` duyệt đệ quy các giá trị string và chạy trước `JsonlFileProcessor`/`JSONRenderer`; hỗ trợ email, điện thoại Việt Nam, CCCD và thẻ thanh toán.
- **Cách kiểm chứng kết quả:** 26 tests pass; load test 10/10 HTTP 200; log validator 100/100 và không phát hiện PII mẫu. Xem `evidence/02-log-validator.png`, `evidence/04-structured-log.png`, `evidence/05-pii-redaction.png`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Langfuse API xác nhận project `day13-k4-l3a-2A202602774`; CP2 workload tạo 12 trace mới.
- **Cấu trúc root/retrieval/generation observations:** Mỗi trace có root `lab-agent-run`, child `knowledge-retrieval` loại retriever và `fake-llm-generation` loại generation. Generation chứa model, prompt link, usage và cost.
- **Cách nối trace với log:** Dùng correlation ID; hai trace so sánh prompt lần lượt `req-20de1713` và `req-e9c427d1`.
- **Prompt name:** `day13-chat`.
- **Version/label baseline:** v1 / `baseline`.
- **Version/label candidate:** v2 / `candidate`.
- **Trace ID của mỗi version:** baseline `746229ae05246731ab5f589b88a71846`; candidate `7b2733cce47dbce9d3b0094e13bf883`.
- **Cách promote và rollback `production`:** Đã chuyển tạm `production` sang v2, sau đó rollback về v1; đọc lại API xác nhận `production=1`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** runtime screenshot từ `data/logs.jsonl` theo dashboard contract: latency/TTFT, traffic, errors/retrieval success, cost, tokens và quality.
- **SLO và lý do chọn:** 99.5% request thành công trong ≤3 giây trên cửa sổ 28 ngày; error budget 0.5%. Chọn 3 giây theo threshold P95 của dashboard.
- **Cách tính error budget:** `100% - 99.5% = 0.5%`; tương đương khoảng 3 giờ 21 phút trong 28 ngày.
- **Ba alert và runbook tương ứng:** error rate >2% trong 5 phút; latency P95 >3 giây trong 10 phút; retrieval success <90% trong 5 phút. Cả ba gửi `#day13-alerts`; runbook ở `docs/alerts.md`.

## 7. Challenge investigation

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (cohort K4), scenario `rag_slow`.
- **Original investigation window:** 2026-09-29 09:40:14-09:40:27 UTC. All five challenge requests returned HTTP 200; structured response latency was 2,652-2,654 ms, median 2,653 ms, nearest-rank P95 2,654 ms. All 5/5 exceeded the 2,000 ms challenge threshold; there were no request/tool failures and retrieval succeeded 5/5. These original records are in `data/logs.jsonl` under the five challenge correlation IDs; the PNG dashboard is a later reproduction, documented in `evidence/README.md`.
- **Related log/correlation ID:** `req-00b906f4`, `response_sent`, feature `monitoring`, latency 2,653 ms, `tool_success=true`; source record is in `data/logs.jsonl`.
- **Trace/span:** trace `0ae007add84a88ef92662fa2e6df6a7d`, correlation ID `req-00b906f4`; root `lab-agent-run` 2.654 s, child `knowledge-retrieval` 2.501 s, child `fake-llm-generation` 0.151 s. Verified from the personal Langfuse project and recorded in `evidence/14-incident-trace.txt`.
- **Re-run screenshots:** `12-incident-metric.png` and `13-incident-log.png` show a later reproduction on 2026-09-29 13:36-13:38 UTC. The original metric is calculated from the five matching records in `data/logs.jsonl`; its log and trace are joined by `req-00b906f4` in `data/logs.jsonl` and `14-incident-trace.txt`.
- **Root cause:** Injected `rag_slow` makes retrieval wait 2.5 seconds in `app/mock_rag.py`; generation takes about 0.151 seconds.
- **Fix action:** Disabled the incident after evidence capture. Post-mitigation verification returned HTTP 200 in 151 ms (`req-c0ffee01`); source record is in `data/logs.jsonl`.
- **Preventive measure:** Track retrieval P95 separately from request latency; add retrieval timeout/fallback or caching and a latency-budget regression check.

## 8. Reflection

- **Technical decision:** Create the correlation ID in middleware and propagate it through structured logs, the agent, and Langfuse metadata so one request can be followed across telemetry layers.
- **Blocker and resolution:** The challenge command initially failed with connection refused because the API was stopped. Starting Uvicorn with `--env-file .env` enabled Langfuse tracing; `/health` confirmed tracing and incident state before rerunning the workload.
- **Metrics -> Logs -> Traces:** Metrics reveal the latency symptom and time range; a correlation ID locates the affected JSONL request; trace spans identify retrieval as the slow step.
- **Prompt, cost, and SLO:** Prompt labels support baseline/candidate comparisons and rollback. Token/cost fields help quantify model usage. SLO and error budget define acceptable user-facing latency and failure levels.
- **Main lesson:** Overall latency does not identify the cause by itself; correlation IDs and span durations make the investigation actionable.
- **Limitations:** The dashboard is a local snapshot. `#day13-alerts` is configured but has no connected Slack webhook. Incident trace evidence is a sanitized observation extract; a direct Langfuse UI screenshot is still useful for item 14.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
