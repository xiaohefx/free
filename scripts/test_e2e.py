#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端真实小批量测试: 抓取真实订阅 → 解析 → 端口预检 → sing-box 真实测活 → 分类
限制节点数, 快速验证全链路可用性与准确率。"""
import os, sys, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main_v2 as mv

# 小批量测试配置
LIMIT_PROTOCOLS = 25  # 每种协议最多测几个 (覆盖全部协议)
mv.MAX_WORKERS_TEST = 16

def main():
    t0 = time.time()
    mv.ensure_directories()
    # 复用已下载的本地资产, 跳过重新下载
    print("[*] 跳过内核下载 (本地已有), 直接抓取订阅 ...")

    raw_nodes = mv.fetch_raw_nodes()
    # 按协议分组取样
    by_proto = {}
    for uri in raw_nodes:
        for prefix in mv.PARSERS:
            if uri.startswith(prefix):
                parsed = mv.parse_node_uri(uri)
                if parsed:
                    by_proto.setdefault(parsed[0]["type"], []).append((uri,) + parsed)
                break

    print("\n[*] 各协议解析统计:")
    candidates = []
    for proto, lst in sorted(by_proto.items(), key=lambda x: -len(x[1])):
        sample = lst[:LIMIT_PROTOCOLS]
        candidates.extend(sample)
        print(f"    {proto:14s}: 共 {len(lst):4d} 解析成功, 取样 {len(sample)}")

    print(f"\n[*] 取样 {len(candidates)} 个节点进入端到端测试")

    # 端口预检
    candidates = mv.prefilter_candidates(candidates)

    # 真实测活
    results = mv.run_liveness_test(candidates)

    # 输出测活详情
    print("\n" + "=" * 90)
    print("测活详情 (协议 | 服务器 | 出口IP | 国家 | 延迟ms | 速度KB/s | MITM | WARP | 断流)")
    print("=" * 90)
    for r in sorted(results, key=lambda x: x["latency_ms"]):
        print(f"{r['proto']:12s} | {r['server'][:32]:32s} | {str(r['exit_ip'])[:16]:16s} | "
              f"{str(r['exit_country_online'] or '?'):4s} | {r['latency_ms']:5d} | "
              f"{r['speed_bps']//1024:6d} | {'MITM!' if r['mitm_risk'] else 'ok':4s} | "
              f"{'WARP' if r.get('is_warp') else '-':4s} | {'断流' if r['is_stalled'] else 'ok'}")

    # 分类
    unique, residential, non_res = mv.classify_and_export(results)
    print(f"\n[*] 分类完成: 总 {len(unique)} | 家宽/移动 {len(residential)} | 普通 {len(non_res)}")
    print("\n家宽节点:")
    for n in residential:
        print(f"  {n['country']} {n['net_type']:12s} {n['exit_ip']:16s} ASN{n.get('asn')} {n.get('org','')[:40]}")

    # 保存原始测试数据供审查
    dump = []
    for r in results:
        dump.append({k: v for k, v in r.items() if k != "outbound"})
    with open(os.path.join(mv.OUTPUT_DIR, "e2e_test_report.json"), "w", encoding="utf-8") as f:
        json.dump(dump, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n[*] 明细已存 output/e2e_test_report.json")
    print(f"[*] 总耗时 {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
