# MO-PHONG-ARQ-STOP-AND-WAIT-VS-GO-BACK-N-
Đề tài môn **Kỹ thuật Truyền dữ liệu** xây dựng mô hình mô phỏng và đánh giá định lượng hiệu năng của hai giao thức truyền tin cậy **Stop-and-Wait ARQ** và **Go-Back-N ARQ** trên kênh truyền có độ trễ lan truyền và xác suất mất khung/mất ACK.

- **Sinh viên thực hiện:** Đoàn Phạm Minh Quang
- **Mã sinh viên:** 23T1020418
- **Khoa / Trường:** Khoa Công nghệ Thông tin – Trường Đại học Khoa học, Đại học Huế
- **Năm học:** 2026 – 2027

---

## 1. Mục tiêu và nội dung mô phỏng

- Mô phỏng cơ chế gửi/nhận khung, báo nhận (`ACK`), bộ đếm `Timeout` và cửa sổ trượt (`Sliding Window`) kích thước $N$.
- Đo lường các chỉ số: **Hiệu suất sử dụng kênh (`Efficiency`)**, **Tổng số lần truyền lại (`Retransmissions`)** và **Tổng thời gian hoàn tất (`Total Time`)**.
- So sánh **Stop-and-Wait ARQ** và **Go-Back-N ARQ** theo tỷ lệ mất gói $p$ và khảo sát ảnh hưởng của kích thước cửa sổ $N \in \{4, 8, 16\}$.

---
Bộ tham số mặc định trong thực nghiệm chuẩn

Số lượng gói tin: 500

Thời gian truyền 1 khung t_frame (ms): 1.0

Trễ lan truyền 1 chiều t_prop (ms): 10.0

Ngưỡng Timeout (ms): 22.0

Các mức tỷ lệ mất gói p tính theo %: 0,2,5,10,20,30

Xác suất mất ACK theo %: bằng tỷ lệ mất khung p

Danh sách kích thước cửa sổ GBN N (vd: 4,8,16): 4, 8, 16

Kích thước cửa sổ N dùng để so sánh chính với Stop-and-Wait: 8

Seed ngẫu nhiên: 42

Bộ tham số mặc định trong thực nghiệm gợi ý

Số lượng gói tin: 1000

Thời gian truyền 1 khung t_frame (ms): 2.0

Trễ lan truyền 1 chiều t_prop (ms): 4.0

Ngưỡng Timeout (ms): 11.0

Các mức tỷ lệ mất gói p tính theo %: 0,1,3,8,15,25

Xác suất mất ACK theo %: 5

Danh sách kích thước cửa sổ GBN N: 2,4,8,16

Kích thước cửa sổ N dùng để so sánh chính với Stop-and-Wait: 4

Seed ngẫu nhiên: 123

---
Bộ tham số mặc định trong thực nghiệm gợi ý
Số lượng gói tin: 1000
Thời gian truyền 1 khung t_frame (ms): 2.0
Trễ lan truyền 1 chiều t_prop (ms): 4.0
Ngưỡng Timeout (ms): 11.0
Các mức tỷ lệ mất gói p tính theo % : 0,1,3,8,15,25
Xác suất mất ACK theo %: 5
Danh sách kích thước cửa sổ GBN N: 2,4,8,16
Kích thước cửa sổ N dùng để so sánh chính với Stop-and-Wait: 4
Seed ngẫu nhiên: 123

---
