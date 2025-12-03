# Biên Bản Cuộc Họp: Đồ Án Lập Trình Socket - Giai Đoạn 2

**Ngày:** [Ngày/Tháng/Năm]
**Thành viên tham gia:** [Thành viên 1], [Thành viên 2], [Thành viên 3]
**Dự án:** Video Streaming qua giao thức RTSP/RTP

## 1. Review Kỹ Thuật & Các Lỗi Đã Sửa (Technical Fixes)

Đã hoàn thành việc sửa lỗi và kiện toàn mã nguồn cơ bản:

- **ServerWorker.py:** Đã sửa lỗi `IndexError` khi phân tích gói tin RTSP SETUP (xử lý chuỗi `client_port` an toàn hơn).
- **Client.py:** Đã sửa lỗi import `tkMessageBox` (tương thích Python 3) và hoàn thiện logic gửi yêu cầu RTSP.
- **RtpPacket.py:** Đã hoàn thiện hàm `encode` để đóng gói tiêu đề RTP chuẩn (12 bytes header).
- **Cấu trúc dự án:** Đã tổ chức lại thành `src`, `video_stream`, `docs` để dễ quản lý và triển khai.

## 2. Các Yêu Cầu Tính Điểm Cần Làm (Grading Tasks)

Để đạt điểm tối đa, nhóm cần triển khai các tính năng sau:

### A. Thống Kê & Phân Tích (Ưu tiên: Cao)

- **Tỷ lệ mất gói (Packet Loss Rate):** Tính toán % số gói RTP bị mất trong quá trình truyền.
- **Tốc độ truyền dữ liệu (Video Data Rate):** Tính toán tốc độ bit (ví dụ: kbps) của video đang stream.
- **Yêu cầu:** Hiển thị các thông số này lên giao diện Client hoặc in ra console định kỳ.

### B. Bộ Đệm Phía Client (Client-Side Buffering) (Ưu tiên: Trung bình)

- **Mục tiêu:** Giảm hiện tượng giật (jitter) khi mạng không ổn định.
- **Triển khai:** Tạo một hàng đợi (queue) để lưu trữ N frame trước khi hiển thị, thay vì hiển thị ngay lập tức khi nhận được.

### C. Báo Cáo & Lý Thuyết (Ưu tiên: Cao)

- **Định dạng gói RTP:** Giải thích chi tiết các trường (Version, Sequence Number, Timestamp...) trong `RtpPacket.py`.
- **Giao thức RTSP:** Vẽ biểu đồ trạng thái (State Machine: INIT -> READY -> PLAYING) và giải thích quy trình bắt tay (Handshake).
- **Biểu đồ tuần tự (Sequence Diagram):** Mô tả luồng tương tác giữa Client và Server.

## 3. Phân Công Công Việc

| Nhiệm vụ               | Mô tả chi tiết                                                 | Người phụ trách | Hạn chót |
| :--------------------- | :------------------------------------------------------------- | :-------------- | :------- |
| **Thống kê (Stats)**   | Code tính toán Packet Loss & Data Rate trong `Client.py`.      | [Tên TV]        | [Ngày]   |
| **Bộ đệm (Buffering)** | Code logic hàng đợi (Queue) để buffer frame.                   | [Tên TV]        | [Ngày]   |
| **Viết báo cáo**       | Soạn thảo nội dung lý thuyết RTP/RTSP và vẽ biểu đồ.           | [Tên TV]        | [Ngày]   |
| **Kiểm thử (Testing)** | Chạy thử nghiệm toàn bộ hệ thống, đảm bảo không còn lỗi crash. | [Tên TV]        | [Ngày]   |
| **HD Streaming**       | (Tùy chọn) Nghiên cứu phân mảnh MJPEG để hỗ trợ video HD.      | [Tên TV]        | [Ngày]   |

## 4. Kế Hoạch Tiếp Theo

- **Cuộc họp tới:** [Ngày]
- **Mục tiêu:** Review phần Thống kê và bản nháp Báo cáo.
