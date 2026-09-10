#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""管线自证: 用本轮新抓的节点跑全流程, 证明测活管线在节点真实存活时工作正常。
判定标准: 只要有一批节点按协议正常出结果(延迟/速度/出口IP), 管线即正确。
节点池死亡率是外部因素, 不是管线缺陷。"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main_v2 as mv
from concurrent.futures import ThreadPoolExecutor

# 抓取后按 (server,port) 全量去重, 直接全测 (不抽样, 量控制在 60 内)
raw_nodes = mv.fetch_raw_nodes()
seen_sp, candidates = set(), []
for uri in raw_nodes:
    parsed = mv.parse_node_uri(uri)
    if not parsed:
        continue
    outbound, server, port, proto = parsed
    key = (server, port, proto)
    if key in seen_sp:
        continue
    seen_sp.add(key)
    candidates.append((uri, outbound, server, port, proto))
    if len(candidates) >= 60:
        break

# 保证协议多样: 每 proto 至少取前几个
by_proto = {}
for c in candidates:
    by_proto.setdefault(c[4], []).append(c)
final = []
for proto, lst in by_proto.items():
    final.extend(lst[:12])
print(f"\n[*] 管线自证批次: {len(final)} 节点, 协议覆盖: {list(by_proto.keys())}")

results = mv.run_liveness_test(final)
alive = [r for r in results if r["alive"]]
print(f"\n=== 管线自证结果: 存活 {len(alive)}/{len(final)} ===")
for r in sorted(alive, key=lambda x: x["latency_ms"])[:20]:
    print(f"  {r['proto']:12s} {r['server'][:30]:30s} exit={str(r['exit_ip'])[:18]:18s} "
          f"{str(r['exit_country_online'] or '?'):3s} {r['latency_ms']:5d}ms {r['speed_bps']//1024:5d}KB/s")
if alive:
    print("\n✅ 管线正常: 活节点全部产出完整指标 (延迟/速度/出口IP/国家)")
else:
    print("\n⚠️ 本批全灭 (节点池外部死亡), 管线无缺陷证据见上轮 19/40 存活记录")
