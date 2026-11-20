import argparse
import random
import matplotlib.pyplot as plt


def simulate_stop_and_wait(
    num_packets=500,
    loss_prob=0.05,
    t_frame=1.0,
    t_prop=10.0,
    timeout=22.0,
    ack_loss_prob=None,
    seed=42,
):
    """Mô phỏng giao thức Stop-and-Wait ARQ."""
    if ack_loss_prob is None:
        ack_loss_prob = loss_prob

    rng = random.Random(seed)
    current_time = 0.0
    seq = 0
    retransmissions = 0

    while seq < num_packets:
        current_time += t_frame
        if rng.random() < loss_prob:
            current_time += timeout
            retransmissions += 1
            continue

        ack_lost = rng.random() < ack_loss_prob
        rtt_ack_arrival = 2.0 * t_prop

        if ack_lost or rtt_ack_arrival > timeout:
            current_time += timeout
            retransmissions += 1
        else:
            current_time += rtt_ack_arrival
            seq += 1

    useful_time = num_packets * t_frame
    efficiency = useful_time / current_time
    return {
        "total_time": current_time,
        "retransmissions": retransmissions,
        "efficiency": efficiency,
    }


def simulate_go_back_n(
    num_packets=500,
    window_size=8,
    loss_prob=0.05,
    t_frame=1.0,
    t_prop=10.0,
    timeout=22.0,
    ack_loss_prob=None,
    seed=42,
):
    """Mô phỏng giao thức Go-Back-N ARQ với cửa sổ trượt kích thước window_size."""
    if window_size < 1:
        raise ValueError("window_size phải >= 1")
    if ack_loss_prob is None:
        ack_loss_prob = loss_prob

    rng = random.Random(seed)
    base = 0
    next_seq = 0
    retransmissions = 0
    inflight = []  # (seq_num, send_time, is_frame_lost)
    current_time = 0.0

    while base < num_packets:
        while next_seq < num_packets and (next_seq - base) < window_size:
            lost = rng.random() < loss_prob
            inflight.append((next_seq, current_time, lost))
            next_seq += 1
            current_time += t_frame

        if not inflight:
            break

        _, head_send_time, head_lost = inflight[0]
        timeout_time = head_send_time + t_frame + timeout

        if head_lost:
            if current_time < timeout_time:
                current_time = timeout_time
            retransmissions += (next_seq - base)
            next_seq = base
            inflight.clear()
        else:
            ack_lost = rng.random() < ack_loss_prob
            ack_arrival_time = head_send_time + t_frame + 2.0 * t_prop

            if not ack_lost and ack_arrival_time <= timeout_time:
                if current_time < ack_arrival_time:
                    current_time = ack_arrival_time
                base += 1
                inflight.pop(0)
            else:
                if current_time < timeout_time:
                    current_time = timeout_time
                retransmissions += (next_seq - base)
                next_seq = base
                inflight.clear()

    useful_time = num_packets * t_frame
    efficiency = useful_time / current_time
    return {
        "total_time": current_time,
        "retransmissions": retransmissions,
        "efficiency": efficiency,
    }


def parse_float_list(raw_text, as_percent=False):
    """Chuyển chuỗi số phân tách bởi dấu phẩy thành danh sách float."""
    items = [x.strip() for x in raw_text.split(",") if x.strip()]
    if not items:
        raise ValueError("Danh sách tham số không được rỗng.")
    vals = []
    for item in items:
        v = float(item)
        if as_percent:
            v = v / 100.0
        vals.append(v)
    return vals


def parse_int_list(raw_text):
    """Chuyển chuỗi số nguyên phân tách bởi dấu phẩy thành danh sách int."""
    items = [int(x.strip()) for x in raw_text.split(",") if x.strip()]
    if not items:
        raise ValueError("Danh sách kích thước cửa sổ không được rỗng.")
    return items


def prompt_interactive_params():
    """Nhập tham số tương tác từ bàn phím (nhấn Enter để dùng giá trị gợi ý)."""
    print("\n--- NHẬP THÔNG SỐ MÔ PHỎNG (Nhấn Enter để giữ mặc định) ---")

    def ask(label, default, cast_fn):
        raw = input(f"{label} [mặc định: {default}]: ").strip()
        if raw == "":
            return default
        return cast_fn(raw)

    num_packets = ask("Số lượng gói tin", 500, int)
    t_frame = ask("Thời gian truyền 1 khung t_frame (ms)", 1.0, float)
    t_prop = ask("Trễ lan truyền 1 chiều t_prop (ms)", 10.0, float)

    suggested_timeout = round(t_frame + 2.0 * t_prop + 1.0, 4)
    timeout = ask("Ngưỡng Timeout (ms)", suggested_timeout, float)

    loss_rates = ask(
        "Các mức tỷ lệ mất gói p tính theo % (vd: 0,2,5,10,20,30)",
        [0.0, 0.02, 0.05, 0.10, 0.20, 0.30],
        lambda s: parse_float_list(s, as_percent=True),
    )

    ack_raw = input("Xác suất mất ACK theo % (Enter = bằng tỷ lệ mất khung p): ").strip()
    ack_loss_prob = None if ack_raw == "" else float(ack_raw) / 100.0

    windows = ask(
        "Danh sách kích thước cửa sổ GBN N (vd: 4,8,16)",
        [4, 8, 16],
        parse_int_list,
    )

    default_window = ask(
        "Kích thước cửa sổ N dùng để so sánh chính với Stop-and-Wait",
        windows[len(windows) // 2],
        int,
    )

    seed = ask("Seed ngẫu nhiên", 42, int)
    save_chart = ask("Lưu biểu đồ ảnh? (y/n)", True, lambda s: s.lower() in ("y", "yes", "1", "true"))
    chart_file = "ket_qua_mo_phong.png"
    if save_chart:
        chart_file = ask("Tên file ảnh biểu đồ", "ket_qua_mo_phong.png", str)

    return {
        "num_packets": num_packets,
        "t_frame": t_frame,
        "t_prop": t_prop,
        "timeout": timeout,
        "loss_rates": loss_rates,
        "ack_loss_prob": ack_loss_prob,
        "windows": windows,
        "default_window": default_window,
        "seed": seed,
        "save_chart": save_chart,
        "chart_file": chart_file,
    }


def run_simulation_and_display(cfg):
    w_main = cfg["default_window"]
    windows = cfg["windows"]

    # Lý thuyết khi p = 0
    a = cfg["t_prop"] / cfg["t_frame"]
    u_sw_theory = 1.0 / (1.0 + 2.0 * a)
    u_gbn_theory = min(1.0, w_main / (1.0 + 2.0 * a))

    print("\n================ TÓM TẮT THÔNG SỐ ĐÃ NHẬP ================")
    print(
        f"Packets={cfg['num_packets']} | t_frame={cfg['t_frame']}ms | "
        f"t_prop={cfg['t_prop']}ms | Timeout={cfg['timeout']}ms | Seed={cfg['seed']}"
    )
    print(
        f"Lý thuyết (p=0%): a={a:.2f}, U_SW={u_sw_theory*100:.2f}%, "
        f"U_GBN(N={w_main})={u_gbn_theory*100:.2f}%"
    )

    # Bảng 1: Stop-and-Wait vs Go-Back-N (default_window)
    print(f"\n--- BẢNG 1: Stop-and-Wait vs Go-Back-N (N={w_main}) ---")
    print(
        f"{'Loss':>6} | {'SW Eff':>8} | {'SW Retx':>8} | {'SW Time':>10} | "
        f"{'GBN Eff':>8} | {'GBN Retx':>9} | {'GBN Time':>10}"
    )
    print("-" * 78)

    s1_rows = []
    for p in cfg["loss_rates"]:
        sw = simulate_stop_and_wait(
            num_packets=cfg["num_packets"],
            loss_prob=p,
            t_frame=cfg["t_frame"],
            t_prop=cfg["t_prop"],
            timeout=cfg["timeout"],
            ack_loss_prob=cfg["ack_loss_prob"],
            seed=cfg["seed"],
        )
        gbn = simulate_go_back_n(
            num_packets=cfg["num_packets"],
            window_size=w_main,
            loss_prob=p,
            t_frame=cfg["t_frame"],
            t_prop=cfg["t_prop"],
            timeout=cfg["timeout"],
            ack_loss_prob=cfg["ack_loss_prob"],
            seed=cfg["seed"],
        )
        s1_rows.append((p, sw, gbn))
        print(
            f"{p*100:5.1f}% | {sw['efficiency']*100:7.2f}% | {sw['retransmissions']:8d} | "
            f"{sw['total_time']:8.1f}ms | {gbn['efficiency']*100:7.2f}% | "
            f"{gbn['retransmissions']:9d} | {gbn['total_time']:8.1f}ms"
        )

    # Bảng 2: Go-Back-N theo các kích thước cửa sổ N
    print(f"\n--- BẢNG 2: Go-Back-N theo cửa sổ N = {windows} ---")
    header = f"{'Loss':>6} | " + " | ".join([f"N={w:<2} Eff | Retx" for w in windows])
    print(header)
    print("-" * len(header))

    by_w = {w: [] for w in windows}
    for p in cfg["loss_rates"]:
        line_parts = [f"{p*100:5.1f}%"]
        for w in windows:
            res = simulate_go_back_n(
                num_packets=cfg["num_packets"],
                window_size=w,
                loss_prob=p,
                t_frame=cfg["t_frame"],
                t_prop=cfg["t_prop"],
                timeout=cfg["timeout"],
                ack_loss_prob=cfg["ack_loss_prob"],
                seed=cfg["seed"],
            )
            by_w[w].append(res)
            line_parts.append(f"{res['efficiency']*100:6.2f}% | {res['retransmissions']:4d}")
        print(" | ".join(line_parts))

    # Vẽ biểu đồ
    x_pct = [p * 100.0 for p in cfg["loss_rates"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=160)

    ax1.plot(x_pct, [r[1]["efficiency"] * 100.0 for r in s1_rows], "o-", label="Stop-and-Wait")
    ax1.plot(x_pct, [r[2]["efficiency"] * 100.0 for r in s1_rows], "s-", label=f"Go-Back-N (N={w_main})")
    ax1.set_title(f"SW vs GBN (N={w_main}, t_prop={cfg['t_prop']}ms)")
    ax1.set_xlabel("Tỷ lệ mất gói p (%)")
    ax1.set_ylabel("Hiệu suất (%)")
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend()

    for w in windows:
        ax2.plot(x_pct, [item["efficiency"] * 100.0 for item in by_w[w]], "d-", label=f"GBN (N={w})")
    ax2.set_title(f"GBN theo kích thước cửa sổ N (t_prop={cfg['t_prop']}ms)")
    ax2.set_xlabel("Tỷ lệ mất gói p (%)")
    ax2.set_ylabel("Hiệu suất (%)")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend()

    plt.tight_layout()
    if cfg["save_chart"]:
        plt.savefig(cfg["chart_file"])
        print(f"\nĐã lưu biểu đồ tại: {cfg['chart_file']}")
    plt.show()


def build_cli_parser():
    parser = argparse.ArgumentParser(
        description="Mô phỏng giao thức Stop-and-Wait ARQ và Go-Back-N ARQ với tham số tùy chỉnh."
    )
    parser.add_argument("--interactive", action="store_true", help="Bật chế độ nhập tương tác từng tham số")
    parser.add_argument("--packets", type=int, default=500, help="Số gói tin (mặc định: 500)")
    parser.add_argument("--t-frame", type=float, default=1.0, help="Thời gian truyền 1 khung ms (mặc định: 1.0)")
    parser.add_argument("--t-prop", type=float, default=10.0, help="Trễ lan truyền 1 chiều ms (mặc định: 10.0)")
    parser.add_argument("--timeout", type=float, default=None, help="Ngưỡng Timeout ms (mặc định: t_frame + 2*t_prop + 1)")
    parser.add_argument(
        "--loss-rates",
        type=str,
        default="0,2,5,10,20,30",
        help="Danh sách tỷ lệ mất gói theo %% phân tách dấu phẩy (mặc định: 0,2,5,10,20,30)",
    )
    parser.add_argument(
        "--ack-loss",
        type=float,
        default=None,
        help="Xác suất mất ACK theo %% (mặc định: bằng tỷ lệ mất khung)",
    )
    parser.add_argument(
        "--windows",
        type=str,
        default="4,8,16",
        help="Danh sách kích thước cửa sổ GBN phân tách dấu phẩy (mặc định: 4,8,16)",
    )
    parser.add_argument(
        "--main-window",
        type=int,
        default=8,
        help="Kích thước cửa sổ N để so sánh với Stop-and-Wait (mặc định: 8)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed ngẫu nhiên (mặc định: 42)")
    parser.add_argument("--no-chart", action="store_true", help="Không lưu ảnh biểu đồ")
    parser.add_argument("--output", type=str, default="ket_qua_mo_phong.png", help="Tên file ảnh biểu đồ")
    return parser


def main():
    parser = build_cli_parser()
    args = parser.parse_args()

    # Nếu chạy không kèm đối số nào thì hỏi nhập tương tác để tiện thay đổi thông số
    import sys
    if args.interactive or len(sys.argv) == 1:
        cfg = prompt_interactive_params()
    else:
        timeout_val = (
            args.timeout
            if args.timeout is not None
            else round(args.t_frame + 2.0 * args.t_prop + 1.0, 4)
        )
        ack_loss_val = None if args.ack_loss is None else args.ack_loss / 100.0
        cfg = {
            "num_packets": args.packets,
            "t_frame": args.t_frame,
            "t_prop": args.t_prop,
            "timeout": timeout_val,
            "loss_rates": parse_float_list(args.loss_rates, as_percent=True),
            "ack_loss_prob": ack_loss_val,
            "windows": parse_int_list(args.windows),
            "default_window": args.main_window,
            "seed": args.seed,
            "save_chart": not args.no_chart,
            "chart_file": args.output,
        }

    run_simulation_and_display(cfg)


if __name__ == "__main__":
    main()
    