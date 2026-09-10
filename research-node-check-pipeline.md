# Research Report: Free-tier stack for a GitHub Actions proxy-node health-check pipeline

**Methodology note:** `web_search` failed in this session (no DEEPSEEK_API_KEY configured). Instead, every claim below marked **[VERIFIED]** was confirmed *first-hand* on 2026-09-09 via live HTTP requests from this machine: actual API calls, fetches of official docs pages (ip-api.com/docs, ipapi.is/free-tier.html), the GitHub REST API (repo existence, releases, release notes, source trees), and raw.githubusercontent.com file downloads. This is primary-source evidence, stronger than search snippets. Items I could not confirm live are marked **[UNVERIFIED — best-effort knowledge]**.

---

## 1. IP intelligence APIs with free tiers

### 1.1 `ip-api.com` — the only keyless API with proxy/hosting/mobile flags

| Property | Value | Status |
|---|---|---|
| Free quota | **45 req/min per IP** (HTTP 429 on excess; persistent abuse → 1 h ban) | **[VERIFIED]** docs page http://ip-api.com/docs/api:json |
| HTTPS on free tier | **NO — HTTP only.** `https://ip-api.com/json/...` returns **403**. Docs: "256-bit SSL encryption is not available for this free API" | **[VERIFIED live]** (403 reproduced) |
| Batch endpoint | `POST http://ip-api.com/batch`, JSON array, **up to 100 IPs** per request; >100 → HTTP 422. Batch limit **15 req/min** (= 1500 IPs/min) | **[VERIFIED]** docs + live POST (2 IPs, got proxy/hosting/mobile for both) |
| `proxy` / `hosting` / `mobile` fields | **FREE — not PRO-gated.** Live response for 8.8.8.8: `{"proxy":false,"hosting":true,"mobile":false,...}` | **[VERIFIED live]** |
| PRO tier adds | SSL (HTTPS), unlimited queries, commercial use. "We do not allow commercial use of this endpoint" (free) | **[VERIFIED]** docs |
| Rate-limit headers | `X-Rl` (remaining in window), `X-Ttl` (seconds to reset) — docs instruct clients to honor these | **[VERIFIED]** docs |
| Full free field list | status, message, continent, continentCode, country, countryCode, region, regionName, city, district, zip, lat, lon, timezone, offset, currency, isp, org, as (`"AS15169 Google LLC"`), asname, reverse, **mobile, proxy, hosting**, query | **[VERIFIED]** docs field table + live response |

Key correction to the prompt's premise: **no per-field free/PRO split exists** — all listed fields, including `proxy`/`hosting`/`mobile`, are free; PRO is about transport/security/quota/commercial rights. Example call that worked:
`http://ip-api.com/json/8.8.8.8?fields=status,message,proxy,hosting,mobile,isp,as,countryCode,query`

- Docs: http://ip-api.com/docs/api:json · http://ip-api.com/docs/api:batch
- Semantics: `hosting:true` = datacenter/colocated; `proxy:true` = "Proxy, VPN or Tor exit address". This is a usable free **datacenter vs residential** signal. A residential node ⇒ `hosting:false, proxy:false`.

### 1.2 `api.ipapi.is` — free tier CHANGED; prompt's assumption is outdated

**[VERIFIED]** from https://ipapi.is/free-tier.html (fetched live):

- Anonymous (no key): **30 lookups per client IP per UTC day**, then 429 for 10 requests; ignoring 429 → firewall-blocked 24 h.
- **Detection flags removed from anonymous tier**: `is_datacenter`, `is_vpn`, `is_proxy`, `is_tor`, `is_abuser` — "these need an API key now". Anonymous also gets **403 `ERR_FORBIDDEN_API_KEY_REQUIRED`** for bulk/ASN queries.
- Free account (key, no credit card): **1,000 lookups/day** and the complete response (all detection flags, full field set).
- Live anonymous response for `https://api.ipapi.is/?q=8.8.8.8`:
  `{"ip":"8.8.8.8","is_bogon":false,"company":"Google LLC","asn":"AS15169 Google LLC","city":"Mountain View","region":"California","country":"United States","lat":…,"lon":…,"timezone":"America/Los_Angeles","docs":"https://ipapi.is/free-tier.html"}`
  - Query format is **`?q={ip}`** (bare `https://api.ipapi.is/8.8.8.8` → 404 — verified).
  - `country` is the **full name** ("United States"), **not** an ISO code — no `location.country_code` in the anonymous response (that shape belongs to the keyed/full response).
  - Anonymous fields = ip, is_bogon, company, asn, city, region, country, lat, lon, timezone only.
- So: "1000 lookups/day WITHOUT a key" is **no longer true**; 1000/day requires a **free key**, and that key is also what unlocks `is_datacenter/is_vpn/is_proxy/is_tor/is_abuser` (+ presumably `is_residential`, `is_crawler`, `is_mobile`, `rir`, `location.country_code` in the full response — those specific remaining field names **[UNVERIFIED]**, but the flags listed on the free-tier page are verified).

### 1.3 `ipinfo.io/json` without token

- **[VERIFIED live]** tokenless works: `https://ipinfo.io/json` and `https://ipinfo.io/8.8.8.8/json` both return 200. Response: `{"ip","hostname","city","region","country"(ISO2),"loc","org":"AS15169 Google LLC","postal","timezone","readme":"https://ipinfo.io/missingauth","anycast":true}`.
- Fields are the **legacy free API**: `org` merges AS number + name (no separate ASN). **No proxy/VPN/datacenter detection at all.**
- The `missingauth` page (fetched live) says the legacy free API still works "with or without an authentication token", may "receive less updates and be discontinued in the future", and nudges to a free Lite account.
- Exact tokenless quota ("1000/day per IP") **[UNVERIFIED]** — commonly cited, but not stated on the missingauth page; treat as soft/undocumented.

### 1.4 Other free APIs (all verified live, 2026-09-09)

| API | HTTPS | Key | Verified live response (8.8.8.8 or self) | Country code | ASN/ISP name | Datacenter/residential detection | Quota |
|---|---|---|---|---|---|---|---|
| `https://ipwho.is/{ip}` | ✅ | none | full geo JSON incl. `connection:{asn:15169,org:"Google LLC",isp:"Google LLC",domain}` | `country_code` | ✅ | ❌ | **1,000 req/day** per ipwhois.io homepage ("Free · 1,000 requests / day", "No API key required", commercial use allowed on Free) **[VERIFIED from homepage]** |
| `https://ipapi.co/{ip}/json/` | ✅ | none (403 with default PS UA; 200 with browser/curl UA) | `{"asn":"AS15169","org":"Google LLC","country_code":"US","network":"8.8.8.0/24",…}` | ✅ | ✅ | ❌ | 1,000/day free, 30k/mo keyed **[UNVERIFIED]** |
| `https://api.ip.sb/geoip` | ✅ | none | `{"ip","country","country_code","region","city","asn":36352,"asn_organization":"HostPapa","organization","isp","timezone","latitude","longitude",…}` | ✅ | ✅ (numeric + org) | ❌ | undocumented; historically generous **[UNVERIFIED]** |
| `https://ifconfig.co/json` | ✅ | none | `{"ip","country","country_iso":"US","asn":"AS8075","asn_org":"MICROSOFT-CORP-MSN-AS-BLOCK",…}` | ✅ (`country_iso`) | ✅ | ❌ | undocumented **[UNVERIFIED]** |

### 1.5 Bottom line for a keyless GH Actions pipeline (US Azure runners)

- **Residential/datacenter verdict, keyless, at scale:** `ip-api.com/batch` is the only viable option — 100 IPs/request × 15 req/min = **1,500 lookups/min**, HTTP-only (fine inside CI), fresh runner IP each job → the 45/15 per-IP limits rarely bite. `proxy`+`hosting`+`mobile` give you the classification.
- **Country + ASN/ISP enrichment:** ipwho.is (1000/day, keyless, commercial-OK) or ip.sb/ifconfig.co as fallbacks.
- **ipapi.is** only becomes useful with a **free key** (1000/day, full flags incl. `is_datacenter/is_vpn/is_proxy/is_tor/is_abuser`) — still zero-cost but not keyless.

---

## 2. MaxMind GeoLite2 free databases (no license key)

### 2.1 P3TERX/GeoLite.mmdb — **VERIFIED, works exactly as the prompt describes**

- Repo exists: https://github.com/P3TERX/GeoLite.mmdb (5,223★; branches: `main`, `download`).
- README lists the raw URLs; I **downloaded both files live**:
  - `https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb` → **8.2 MB** ✅
  - `https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb` → **11.54 MB** ✅
  - `GeoLite2-City.mmdb` also on the branch.
  - Files begin with a binary search tree (mmdb has no magic prefix; metadata "MaxMind.com" key sits near EOF) — sizes match GeoLite2 expectations. Use the `.sha256sum` sibling? (P3TERX publishes none; verify by reading with maxminddb/geoip2 readers.)
- Auto-updated via Actions (repo pushed 2026-09-07). Direct raw URLs are stable.

### 2.2 Dreamacro/maxmind-geoip — exists, but **Country only now**

- Repo exists (800★) but the `master` branch contains only README + workflow. **All mmdb files moved to Releases.** Monthly tags `YYYYMMDD`.
- **[VERIFIED live]** `https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb` → HTTP 200, **8.27 MB** (latest tag 20260812). Concrete: `https://github.com/Dreamacro/maxmind-geoip/releases/download/20260812/Country.mmdb`.
- **No `ASN.mmdb`** in current releases — only Country. So it's an alternative *Country* source, not an ASN source.

### 2.3 Loyalsoldier/geoip — **VERIFIED, richest keyless source**

- 6,506★, releases regenerated **every Thursday**. Latest live release (202609040655) assets verified:
  - `Country.mmdb` (7.47 MB) — `https://github.com/Loyalsoldier/geoip/releases/latest/download/Country.mmdb` **[VERIFIED live, HTTP 200]**
  - `Country-asn.mmdb` (0.2 MB), `Country-without-asn.mmdb` (8.08 MB), `Country-only-cn-private.mmdb`, `geoip.dat` (16.33 MB, v2ray), `geoip-asn.dat`, `cn.dat`, `private.dat` — each with `.sha256sum`.
- Caveat: it's MaxMind GeoLite2-Country CSV **with China-specific overrides** (CN data from gaoyifan/china-operator-ip) plus extra categories (`cloudflare`, `netflix`, `telegram`, `tor`…). For a global country-code lookup the P3TERX/Dreamacro "pure" GeoLite2 files are cleaner; Loyalsoldier wins if you also want v2ray `dat`/sing-box `SRS`/mihomo `MRS` formats.

### 2.4 ipinfo free country/ASN mmdb — **requires (free) token; not keyless**

- `https://ipinfo.io/free-database/` and `/free-database-downloads` → **404** now (verified live).
- `https://ipinfo.io/data/free/country.mmdb` and `asn.mmdb` → **401 Unauthorized** (verified live).
- `https://ipinfo.io/data?format=json` → 200 (catalogue only; downloads are tokenized).
- ipinfo's free DBs (country + ASN, mmdb & csv) exist behind a **free developer account token**. `https://api.ipinfo.io/lookup?token=…` is their API form. **Zero-cost but not keyless** — cannot be dropped into a public keyless pipeline. Their GitHub org only offers `ipinfo/sample-database` (sample mmdb files) — not production data.

**Recommendation:** P3TERX for Country+ASN mmdb, no key, direct raw URLs; Dreamacro as Country fallback; Loyalsoldier for multi-format + weekly freshness.

---

## 3. sing-box protocol support

### 3.1 Latest stable & download URL

- **Latest stable: v1.14.0** (published 2026-08-31; v1.15.0-alpha.2 prereleases exist). Default branch `testing`, stable branch `stable`. **[VERIFIED via GitHub API]**
- **Download pattern VERIFIED live** (HEAD → HTTP 200, 30.17 MB, `application/octet-stream`):
  `https://github.com/SagerNet/sing-box/releases/download/v1.14.0/sing-box-1.14.0-linux-amd64.tar.gz`
  - Note: 1.14.0 ships **three** linux-amd64 variants: `sing-box-1.14.0-linux-amd64.tar.gz` (plain), `-glibc.tar.gz`, `-musl.tar.gz`. The plain one (prompt's pattern) still exists.

### 3.2 Outbound support matrix (each doc page probed live; source tree cross-checked)

Docs sidebar (https://sing-box.sagernet.org/) Outbound list, **[VERIFIED]**: Direct, Bridge, Block, SOCKS, HTTP, Shadowsocks, VMess, Trojan, Naive, WireGuard, Hysteria, ShadowTLS, VLESS, TUIC, Hysteria2, AnyTLS, Snell, Tor, SSH, DNS, Selector, URLTest.

| Protocol / feature | Supported? | Evidence |
|---|---|---|
| **vless** | ✅ | doc HTTP 200; `flow: "xtls-rprx-vision"` documented (VLESS Sub-protocol: xtls-rprx-vision) |
| vless + **reality** | ✅ | TLS shared docs contain **Reality Fields** (`public_key`, `short_id`, handshake, max_time_difference) |
| vless + vision flow | ✅ | same doc example JSON |
| **vmess** | ✅ | doc 200: security, alter_id, global_padding, authenticated_length, network tcp/udp, tls |
| vmess **ws / grpc / h2 / httpupgrade** | ✅ | V2Ray Transport doc: available transports **HTTP, WebSocket, QUIC, gRPC, HTTPUpgrade**. Note: "h2" is the `http` transport type (HTTP/2 negotiated), not a separate `h2` type |
| **trojan** | ✅ | doc 200 |
| **shadowsocks incl. 2022 ciphers** | ✅ | method list verbatim: `2022-blake3-aes-128-gcm`, `2022-blake3-aes-256-gcm`, `2022-blake3-chacha20-poly1305`, `none`, `aes-128-gcm`… plus `udp_over_tcp`, multiplex, SIP003 plugin |
| **hysteria2** | ✅ | doc 200; 1.14.0 even added Hysteria2 NAT traversal + Realm service |
| **TUIC** | ✅ (v5 config shape) | doc 200; option struct has `uuid` + `password` (TUIC **v5** auth shape); no version selector exists → **TUIC v4 (token-only auth) is not configurable in current options; v4 support [UNVERIFIED, likely dropped]** |
| **anytls** | ✅ **added in 1.12.0** | **[VERIFIED]** first stable mention = v1.12.0 release notes: "See AnyTLS Inbound and AnyTLS Outbound" links. So yes — 1.12, not 1.13 |
| **hysteria (v1)** | ✅ **still supported, not removed** | outbound doc HTTP 200 (auth/auth_str/obfs/up_mbps/down_mbps; window options marked deprecated); `protocol/hysteria` present in source tree as of 1.14.0 |
| **mieru** | ❌ **NOT supported** | no outbound doc page (fetch failed/absent), and **not in `protocol/` source tree** (tree lists: anytls, block, bridge, cloudflare, direct, dns, group, http, hysteria, hysteria2, mixed, naive, openconnect, openvpn, redirect, shadowsocks, shadowtls, snell, socks, ssh, tailscale, tor, trojan, tuic, tun, vless, vmess, wireguard). mieru needs its own client (enfein/mieru) |
| **ssh** | ✅ | outbound doc HTTP 200 |
| Snell / ShadowTLS / Tor / WireGuard / naive | ✅ | all in docs sidebar + protocol tree |

### 3.3 Mapping the user's protocol list

- VLESS → ✅ (incl. reality, vision)
- "WMESS" → vmess ✅ (ws/grpc/h2/httpupgrade)
- "H2T" → ambiguous: if **hysteria2** → ✅; if **HTTP/2+TCP transport** (vmess/vless over h2) → ✅ via `transport: {type: "http"}`. Either way sing-box covers it.
- TUIC → ✅ (v5 uuid+password config; v4 unlikely)
- shadowsocks → ✅ (2022 ciphers included)
- trojan ("trajon") → ✅
- anytls → ✅ (since 1.12.0)
- reality → not a protocol; a TLS layer for VLESS/Trojan → ✅ via `tls.reality.*`

---

## 4. Existing open-source node-check tools (best practices)

### 4.1 beck-8/subs-check (Go, 5,210★) — most sophisticated; source read line-by-line

Repo: https://github.com/beck-8/subs-check (source files fetched live).

- **Core engine: NOT sing-box — it embeds mihomo (Clash.Meta)**: `go.mod` requires `github.com/metacubex/mihomo` (v1.19.31). Proxies are parsed to mihomo maps; aliveness/speed/media all run through mihomo's adapter.
- **Pipeline** (README architecture + `check/check.go`): fetch subs (clash YAML or v2ray base64 → converted) → dedup → **alive check** → media-unlock + rename + IP-risk → filter (regex) → **speed test** → output (clash/v2ray base64/sing-box via built-in Sub-Store on :8299/:8199, save to local/R2/Gist/WebDAV/S3).
- **Alive check** (`check/platform/alive.go`): plain GET of config `alive-test-url` through the proxy; pass = HTTP 2xx. **Default: `http://gstatic.com/generate_204`**, timeout default 5000 ms, concurrency default 50.
- **Exit-IP lookup** (`proxy/info.go`, `GetProxyCountry`): fires **four checkers in parallel, first success by priority wins**:
  1. `https://ip.122911.xyz/api/ipinfo` (needs "non-CF, non-rate-limited, ipv4" API — comment explains CF-hosted APIs misreport CF nodes)
  2. `https://api.ipinfo.io/lite/me?token=<hardcoded-obfuscated-free-token>` (the token is stored byte-array-obfuscated in source)
  3. `https://www.cloudflare.com/cdn-cgi/trace` (fallback; returns proxy-IP location for CF-fronted nodes, not true exit)
  4. `https://functions-geolocation.edgeone.app/geo` (Tencent EdgeOne; `eo.geo.countryCodeAlpha2` + `eo.clientIp`)
  - `GetIPSB` (`https://api.ip.sb/geoip`) **exists in code but is NOT in the active checker list** — deprecated for this purpose.
- **Speed test** (`check/platform/speed.go`): GET of configurable `speed-test-url` through the proxy; measures **network-layer bytes** (statsConn counter) over wall time → KB/s; caps at `download-mb` (default 20 MB) and `download-timeout` (10 s); random UA; optional global rate-limit bucket.
  - **Default `speed-test-url` is a GitHub Release artifact** (`…/Waifu2x-Extension-GUI-v2.21.12-Portable.7z`), NOT Cloudflare. README explicitly warns: "避免使用 Speedtest 或 Cloudflare 下载链接，因为部分节点会屏蔽测速网站" — many nodes block known speedtest endpoints; they ship `doc/cloudflare/worker.js` to self-host `?bytes=104857600` URLs on your own domain.
- **IP risk / residential-ish detection** (`check/platform/iprisk.go`): **scrapes `https://scamalytics.com/ip/{ip}` HTML**, locates the "IP Fraud Risk API" marker, parses score → appends e.g. `45%` to node name; users filter with regex `\|[0-4]?[0-9]%`. This is the only "IP quality" signal among these tools.
- Cloudflare R2 is used as an **output storage backend** (`save/method/cloudflare_r2.go`), not for speed testing.

**Cloudflare speed endpoint reality check [VERIFIED live]:** `https://speed.cloudflare.com/__down?bytes=N` works for N=10,000,000 / 26,214,400 / 52,428,800 but returned **403 for N=104,857600 (100 MB)** from this client, and `__downlaod100MB` (the typo URL) is **404**. So the prompt's remembered URL is wrong; use `__down?bytes=` with modest sizes (≤ 25–50 MB) and expect occasional 403s.

### 4.2 mahdibland/V2RayAggregator (4,014★) — real probing on Actions

- Workflows (read live): `Collector.yml` (merge upstream subs via **subconverter v0.7.2** + local node server + `list_merge.py`), `speedtest.yml` + `speedtest_yml.yml` (every 8 h), `test_ip.yml`, `clash_yaml.yml`, `merge.yml`.
- **Liveness+speed engine**: `speedtest2.sh` downloads **LiteSpeedTest (`lite-linux-amd64` from mahdibland/SSAggregator releases)** and runs it with `lite_config.json` (verified: `{"speedtestMode":"all","pingMethod":"googleping","sortMethod":"rspeed","concurrency":15,"testMode":2,"timeout":12,…}`) against the merged base64 subscription. LiteSpeedTest does real per-node ping + download through each proxy.
- `test_ip.yml` runs `utils/speedtest/ip_test.sh` — **file no longer exists (404)**, workflow kept for dispatch history.
- **No residential/datacenter detection.**

### 4.3 Epodonios — collector only, **no probing at all**

- `Epodonios/mass-checker` **does not exist** (API 404). The real repos: **`Epodonios/v2ray-configs`** (3,233★, cron `*/17 * * * *`) and `bulk-xray-v2ray-vless-vmess-…-configs`.
- Read `Files/app.py` live: it downloads base64 subscription URLs from other repos, decodes, filters by protocol keyword, renames remarks to "EPODONIOS", splits by country via `sort.py`, commits. **Zero liveness testing** — "Updating every 17 minutes" is just re-aggregation of upstream lists.

### 4.4 barry-far — same pattern, no probing

- `barry-far/V2ray-Configs` returns 403 via API (renamed/protected); the active repo is **`barry-far/V2ray-Config`** (2,409★, cron `*/15 * * * *`). Its `Files/app.py` (read live) is functionally identical to Epodonios's: fetch → base64-decode → merge → split; **no node testing**.

### 4.5 yebekhe — TelegramV2rayCollector is gone; successor is PSG

- `yebekhe/TelegramV2rayCollector` **404** (deleted). Unrelated forks (Kwinshadow/… 142★) persist.
- Successor: **`itsyebekhe/PSG`** (440★, "Proxy Subscription Generator"), pushed 2026-09-09. Its `auto_update.yml` (read live) runs every 6 h: Python 3.10, `pip install aiohttp geoip2 pyyaml`, runs `main.py` with TG_TOKEN/TG_CHAT_ID secrets, auto-commits `subscriptions/*`, `lite/*`, `api/*`. The `geoip2` dependency is used for geo labeling of collected nodes (mmdb-based, offline); the workflow itself shows **no per-node liveness probing step** (lite variants are upstream-filtered). **[Partially verified — workflow-level only]**

### 4.6 Residential-detection landscape across these tools

| Tool | Real liveness probe | Speed test | Exit-IP source | IP-quality / residential detection |
|---|---|---|---|---|
| beck-8/subs-check | ✅ (gstatic 204 via mihomo) | ✅ (custom URL, GitHub artifact default) | 4-way parallel: ip.122911.xyz → ipinfo.io/lite/me (free token) → cloudflare cdn-cgi/trace → EdgeOne geo | ✅ **Scamalytics fraud-score scrape** (HTML, keyless, no API) |
| mahdibland/V2RayAggregator | ✅ (LiteSpeedTest) | ✅ (LiteSpeedTest rspeed) | LiteSpeedTest internal | ❌ |
| Epodonios/v2ray-configs | ❌ | ❌ | n/a | ❌ |
| barry-far/V2ray-Config | ❌ | ❌ | n/a | ❌ |
| itsyebekhe/PSG | ❌ (aggregation) | ❌ | geoip2 mmdb (labeling) | ❌ |

**Takeaway for your pipeline:** subs-check's design is the reference worth studying — (1) plain-HTTP 204 endpoint for aliveness, (2) *self-hosted / non-speedtest-branded* download URLs for throughput (nodes block known speedtest sites), (3) multi-provider exit-IP lookup with CF-specific caveats, (4) Scamalytics scraping as a free "IP quality" proxy. None of the studied tools use sing-box (mihomo/LiteSpeedTest instead); sing-box remains the better fit for your protocol list (anytls/reality/hysteria2 coverage in one binary).

---

## 5. Corrections to the prompt's assumptions (summary)

1. ip-api.com: `proxy`/`hosting`/`mobile` are **free**, not PRO; free is HTTP-only (403 on HTTPS, verified); batch = 100 IPs @ 15/min (verified); single = 45/min (verified).
2. ipapi.is: **no longer 1000/day keyless** — 30/day anonymous with detection flags removed; 1000/day + full flags with a **free key**; `?q=` query format; anonymous response lacks `country_code`/flags.
3. Dreamacro/maxmind-geoip: releases now carry **Country.mmdb only** (no ASN), via `/releases/latest/download/Country.mmdb`.
4. ipinfo free mmdb: **not keyless** — 401 without token; `/free-database` pages are 404.
5. sing-box: latest stable **1.14.0**; **anytls added in 1.12.0**; **hysteria v1 still present** (deprecated window fields); **mieru NOT supported**; TUIC config is v5-shaped (uuid+password), v4 unlikely; download URL pattern verified, plus new glibc/musl variants.
6. subs-check uses **mihomo, not sing-box**, and its speed-test URL is a **GitHub release artifact, not Cloudflare** (Cloudflare `__down?bytes=` exists but 403'd at 100 MB and `__downlaod100MB` is 404).
7. Epodonios & barry-far repos **do no probing**; only subs-check and mahdibland (LiteSpeedTest) really test nodes; only subs-check does any IP-quality/residential-adjacent check (Scamalytics scrape).

## Key sources (all fetched live 2026-09-09)

- http://ip-api.com/docs/api:json · http://ip-api.com/docs/api:batch
- https://ipapi.is/free-tier.html
- https://ipinfo.io/missingauth · https://ipwhois.io/ (pricing/free tier)
- https://github.com/P3TERX/GeoLite.mmdb (branch `download`) · https://github.com/Dreamacro/maxmind-geoip/releases · https://github.com/Loyalsoldier/geoip/releases
- https://api.github.com/repos/SagerNet/sing-box/releases (+ /latest, v1.12.0/v1.13.0 notes) · https://sing-box.sagernet.org/configuration/outbound/{vless,vmess,trojan,shadowsocks,tuic,hysteria,hysteria2,anytls,ssh}/ · /deprecated/ · /configuration/shared/v2ray-transport/ · /configuration/shared/tls/
- https://github.com/beck-8/subs-check — `go.mod`, `check/platform/{alive,speed,iprisk,pool}.go`, `proxy/info.go`, `config/config.example.yaml`, `README.md`
- https://github.com/mahdibland/V2RayAggregator — `.github/workflows/{Collector,speedtest,test_ip}.yml`, `utils/speedtest/{speedtest2.sh,lite_config.json}`
- https://github.com/Epodonios/v2ray-configs — `.github/workflows/main.yml`, `Files/app.py`
- https://github.com/barry-far/V2ray-Config — `Files/app.py` · https://github.com/itsyebekhe/PSG — `.github/workflows/auto_update.yml`
- Live probes: `speed.cloudflare.com/__down?bytes=…` (25/50 MB 200, 100 MB 403, typo-URL 404)
