#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终验收: 全流程 (测活→分类→导出→README) 小批量运行, 验证订阅文件生成正确"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main_v2 as mv

mv.MAX_WORKERS_TEST = 16
LIMIT = 40

raw_nodes = mv.fetch_raw_nodes()
seen, candidates = set(), []
for uri in raw_nodes:
    parsed = mv.parse_node_uri(uri)
    if not parsed:
        continue
    outbound, server, port, proto = parsed
    key = (server, port, proto)
    if key in seen:
        continue
    seen.add(key)
    candidates.append((uri, outbound, server, port, proto))
    if len(candidates) >= LIMIT:
        break

print(f"[*] 验收批次: {len(candidates)} 节点")
results = mv.run_liveness_test(candidates)

# 全流程: 分类+导出
unique, residential, non_res = mv.classify_and_export(results)
total, res = mv.export_all(unique, residential, non_res)
mv.update_readme(total, res)

# 验证输出文件
print("\n===== 订阅文件验收 =====")
checks = [
    ("output/v2ray.txt", "base64 总订阅"),
    ("output/clash.yaml", "Clash YAML"),
    ("output/singbox.json", "sing-box JSON"),
]
for path, desc in checks:
    p = os.path.join(mv.BASEDIR, path)
    if not os.path.exists(p):
        print(f"  ❌ {desc}: 文件不存在 {path}")
        continue
    size = os.path.getsize(p)
    content_ok = False
    try:
        if path.endswith(".txt"):
            import base64
            with open(p) as f:
                dec = base64.b64decode(f.read().strip()).decode()
            lines = [l for l in dec.splitlines() if l.strip()]
            content_ok = len(lines) > 0
            extra = f" | {len(lines)} 节点: {lines[0][:70]}..."
        elif path.endswith(".yaml"):
            import yaml as y
            with open(p, encoding="utf-8") as f:
                cfg = y.safe_load(f)
            n = len(cfg.get("proxies", []))
            content_ok = n > 0 and "proxy-groups" in cfg
            extra = f" | {n} proxies"
        else:
            with open(p, encoding="utf-8") as f:
                cfg = json.load(f)
            n = len([o for o in cfg.get("outbounds", []) if o.get("type") in
                     ("vless", "vmess", "trojan", "shadowsocks", "hysteria2", "tuic", "anytls")])
            content_ok = n > 0
            extra = f" | {n} outbounds"
        print(f"  {'✅' if content_ok else '❌'} {desc}: {size} bytes{extra if content_ok else ' | 空/无效'}")
    except Exception as e:
        print(f"  ❌ {desc}: 解析失败 {e}")

# README
p = os.path.join(mv.BASEDIR, "README.md")
with open(p, encoding="utf-8") as f:
    readme = f.read()
ok = "节点总数" in readme and "家宽" in readme
print(f"  {'✅' if ok else '❌'} README.md: {len(readme)} bytes, 动态表格={'有' if ok else '无'}")
print("\n===== 验收完成 =====")
