# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:**
- **MSSV:** 2A202602774
- **Lớp:** K4-L3A
- **Repository URL:**
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602774`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.txt` |
| Dashboard validator | `evidence/03-dashboard-validator.txt` |
| Structured log | `evidence/04-structured-log.txt` |
| PII redaction | `evidence/05-pii-redaction.txt` |
| Trace list | `evidence/06-trace-list.txt` |
| Trace waterfall | `evidence/07-trace-waterfall.txt` |
| Trace metadata | `evidence/08-trace-metadata.txt` |
| Prompt versions | `evidence/09-prompt-versions.txt` |
| Prompt rollback | `evidence/10-prompt-rollback.txt` |
| Dashboard runtime | `evidence/11-dashboard-overview.html` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 (29 records, 10 correlation IDs, 0 PII leak) | CP1 đạt. |
| `validate_dashboard.py` | 6/6 panel hợp lệ | 6/6 panel hợp lệ | Có snapshot HTML từ log thực tế. |
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
- **Cách kiểm chứng kết quả:** 25 tests pass; load test 10/10 HTTP 200; log validator 100/100 và không phát hiện PII mẫu. Xem `evidence/02-log-validator.txt`, `evidence/04-structured-log.txt`, `evidence/05-pii-redaction.txt`.

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

- **Dashboard và sáu panel:** Snapshot HTML từ `data/logs.jsonl` theo dashboard contract: latency/TTFT, traffic, errors/retrieval success, cost, tokens và quality.
- **SLO và lý do chọn:** 99.5% request thành công trong ≤3 giây trên cửa sổ 28 ngày; error budget 0.5%. Chọn 3 giây theo threshold P95 của dashboard.
- **Cách tính error budget:** `100% - 99.5% = 0.5%`; tương đương khoảng 3 giờ 21 phút trong 28 ngày.
- **Ba alert và runbook tương ứng:** error rate >2% trong 5 phút; latency P95 >3 giây trong 10 phút; retrieval success <90% trong 5 phút. Cả ba gửi `#day13-alerts`; runbook ở `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
