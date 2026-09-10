# 🚀 免费节点自动测活订阅池 (含真实家宽/住宅IP甄选)

> 👤 **定制规范命名**: 所有订阅节点均重命名为 `国旗 地区 序号 (家宽) - xiaohe`
> ⚡ **真实可用保障**: 所有节点由 `sing-box vv1.14.0` 内核建立实际代理隧道, 完成真实 HTTPS 双向传输握手 + 出口 IP 穿透验证 + Cloudflare 限速下载断流检测 + TLS 证书校验 (MITM 劫持识别), 拒绝虚假通畅、断流节点与高危劫持节点。
> 🛡️ **全协议支持**: VLESS (Reality/Vision) · VMESS · Trojan · Shadowsocks · Hysteria2 · TUIC · AnyTLS

---

## 📌 全部节点总订阅链接

| 客户端 / 格式类型 | 节点总数 | 免翻 CDN 订阅直链 (国内直连) | 官方原生 Raw 直链 (开启代理) |
| :--- | :---: | :--- | :--- |
| 🚀 **Clash (YAML 格式)** | `1` | [免翻 CDN 直链](https://cdn.jsdelivr.net/gh/heleihub/Free-node-subscription@main/output/clash.yaml?v=1788979775) | [官方 Raw 直链](https://raw.githubusercontent.com/heleihub/Free-node-subscription/main/output/clash.yaml) |
| ⚡ **V2RayN (Base64 格式)** | `1` | [免翻 CDN 直链](https://cdn.jsdelivr.net/gh/heleihub/Free-node-subscription@main/output/v2ray.txt?v=1788979775) | [官方 Raw 直链](https://raw.githubusercontent.com/heleihub/Free-node-subscription/main/output/v2ray.txt) |
| 📦 **sing-box (JSON 格式)** | `1` | [免翻 CDN 直链](https://cdn.jsdelivr.net/gh/heleihub/Free-node-subscription@main/output/singbox.json?v=1788979775) | [官方 Raw 直链](https://raw.githubusercontent.com/heleihub/Free-node-subscription/main/output/singbox.json) |

---

## 🏠 按照家宽分类节点订阅 (住宅 IP 专区)

> 家宽判定六重信号: ① ip-api.com `hosting` 字段 ② `mobile` 移动网络字段 ③ Cloudflare/主流 CDN Anycast 网段比对 ④ MaxMind GeoLite2 ASN 白/黑名单 (覆盖 60+ 国家主流民用运营商) ⑤ rDNS/ISP 名称特征 ⑥ Scamalytics 风控评分复核 (fraud ≥75 降级、≥90 剔除)。排除所有云主机/数据中心/CDN 任播, 保留真实民用宽带与移动网络。

| 家宽地区 | 节点数 | V2RayN 专属订阅 | Clash 专属订阅 | sing-box 专属订阅 |
| :--- | :---: | :---: | :---: | :---: |
| 暂无可用节点 | 0 | - | - | - |

---

## 🗺️ 按照国家分类节点订阅 (非家宽/数据中心节点)

| 地区/国家 | 节点数 | V2RayN 专属订阅 | Clash 专属订阅 | sing-box 专属订阅 |
| :--- | :---: | :---: | :---: | :---: |
| 🇱🇻 拉脱维亚 (Latvia) | 1 | [CDN 直链](https://cdn.jsdelivr.net/gh/heleihub/Free-node-subscription@main/output/by-country/LV.txt?v=1788979775) · [Raw 直链](https://raw.githubusercontent.com/heleihub/Free-node-subscription/main/output/by-country/LV.txt) | [CDN 直链](https://cdn.jsdelivr.net/gh/heleihub/Free-node-subscription@main/output/by-country/clash-LV.yaml?v=1788979775) · [Raw 直链](https://raw.githubusercontent.com/heleihub/Free-node-subscription/main/output/by-country/clash-LV.yaml) | [CDN 直链](https://cdn.jsdelivr.net/gh/heleihub/Free-node-subscription@main/output/by-country/singbox-LV.json?v=1788979775) · [Raw 直链](https://raw.githubusercontent.com/heleihub/Free-node-subscription/main/output/by-country/singbox-LV.json) |

---

## ⭐ 项目热度

[![Star History Chart](https://api.star-history.com/svg?repos=heleihub/Free-node-subscription&type=Date)](https://star-history.com/#heleihub/Free-node-subscription&Date)

---

## 🛠️ 项目使用说明
1. **自动更新机制**：GitHub Actions 每 6 小时全自动运行并刷新上述全部订阅与数据。
2. **测活标准**：节点必须通过 ① 端口预检 ② sing-box 实际隧道 3 个 generate_204 探测 ③ 真实出口 IP 穿透获取 ④ Cloudflare 5MB 限时下载 (吞吐 ≥ 70KB/s) ⑤ TLS 证书校验非 MITM, 方可入库。
3. **多客户端兼容**：Clash / v2rayN / sing-box 全格式订阅。
