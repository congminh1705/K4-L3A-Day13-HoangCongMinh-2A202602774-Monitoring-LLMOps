# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- **Tên:** Elevated API error rate

- Tên: `Elevated API error rate`
- Severity: critical
- Duration: 5 phút liên tiếp với error rate trên 2%
- Kênh thông báo: Slack
- SLI/SLO liên quan: tỷ lệ request thành công trong SLO `fast_successful_requests`.
- Điều kiện và thời gian duy trì: `request_failed / request_received > 2%` trong 5 phút.
- Ảnh hưởng tới người dùng: request thất bại hoặc trả lỗi tăng.
- Ba bước kiểm tra đầu tiên: xem error rate và `error_type` trên dashboard; lọc `request_failed` trong JSONL theo thời gian; dùng correlation ID để tìm trace/span lỗi.
- Mitigation tạm thời: rollback thay đổi gần nhất; nếu lỗi retrieval tăng, giảm tải hoặc tắt route lỗi trong khi khôi phục dependency.
- Owner: `monitoring-on-call`; Slack `#day13-alerts`.

## Alert 2

- **Tên:** Slow successful requests

- Tên: `Slow successful requests`
- Severity: warning
- Duration: 10 phút liên tiếp với P95 latency trên 3000 ms.
- Kênh thông báo: Slack
- SLI/SLO liên quan: latency P95 của SLO `fast_successful_requests`.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` trong 10 phút.
- Ảnh hưởng tới người dùng: thời gian chờ cao, có thể timeout.
- Ba bước kiểm tra đầu tiên: so sánh P50/P95/P99 và TTFT; lọc log `response_sent` chậm; mở trace cùng correlation ID để so thời gian retrieval và generation.
- Mitigation tạm thời: giảm concurrency đầu vào hoặc áp dụng timeout/fallback cho bước chậm.
- Owner: `monitoring-on-call`; Slack `#day13-alerts`.

## Alert 3

- **Tên:** Low retrieval success rate

- Tên: `Low retrieval success rate`
- Severity: warning
- Duration: 5 phút liên tiếp dưới 90% retrieval thành công.
- Kênh thông báo: Slack
- SLI/SLO liên quan: guardrail `retrieval_success_rate_pct_min`.
- Điều kiện và thời gian duy trì: `tool_success == true / tool_success != null < 90%` trong 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời thiếu ngữ cảnh hoặc request thất bại khi retrieval lỗi.
- Ba bước kiểm tra đầu tiên: xem tool success và error rate; kiểm tra log `request_failed` có `tool_name=retrieval`; mở trace và kiểm tra observation `knowledge-retrieval`.
- Mitigation tạm thời: chuyển sang câu trả lời fallback, kiểm tra/khôi phục vector store rồi xác nhận retrieval success hồi phục.
- Owner: `monitoring-on-call`; Slack `#day13-alerts`.
