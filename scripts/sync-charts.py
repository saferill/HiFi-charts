#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HiFi Charts Synchronization Script (100+ Countries, Verified Live on YouTube Music)

1. Fetches all official country charts from YouTube Music `FEmusic_charts` (~70 countries + Global).
2. Preserves the 13 flagship charts at the top (ID, Global, US, KR, JP, UK, VN, BR, MX, ES, IT)
   using real, verified YouTube Music playlist IDs.
3. Expands beyond FEmusic_charts to 100+ countries via YouTube Music playlist search.
4. Strictly validates every playlistId via `browseId: VL<playlistId>` (> 0 tracks) before writing.
5. Preserves existing `createdAt` when chart IDs haven't changed so 2-hourly runs never create empty commits.
"""

import base64
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

YT_BROWSE_URL = "https://music.youtube.com/youtubei/v1/browse?prettyPrint=false"
YT_SEARCH_URL = "https://music.youtube.com/youtubei/v1/search?prettyPrint=false"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

BASE_CONTEXT = {
    "client": {
        "clientName": "WEB_REMIX",
        "clientVersion": "1.20250101.01.00",
        "hl": "en",
        "gl": "US",
    }
}

# 13 flagship charts pinned at the very top in exact order
FLAGSHIP_SPECS = [
    {
        "id": "chart-id-top50",
        "name": "Top 50 - Indonesia",
        "description": "Lagu-lagu terpopuler dan paling sering diputar minggu ini di Indonesia",
        "country": "id",
        "source": ("official", "ID", "top"),
    },
    {
        "id": "chart-id-pop",
        "name": "Pop Teratas - Indonesia",
        "description": "Kompilasi lagu pop Indonesia terhangat dan hits teratas",
        "country": "id",
        "source": ("official", "ID", "daily"),
    },
    {
        "id": "chart-global-top50",
        "name": "Top 50 - Global",
        "description": "Lagu paling populer dan viral di seluruh dunia minggu ini",
        "country": "global",
        "source": ("official", "ZZ", "top"),
    },
    {
        "id": "chart-global-hits",
        "name": "Today's Biggest Hits - Global",
        "description": "Hits terpopuler dunia yang sedang tren saat ini",
        "country": "global",
        "source": ("official", "ZZ", "daily"),
    },
    {
        "id": "chart-us-top50",
        "name": "Top 50 - United States",
        "description": "Tangga lagu terpopuler minggu ini di Amerika Serikat",
        "country": "us",
        "source": ("official", "US", "top"),
    },
    {
        "id": "chart-kr-top50",
        "name": "Top 50 - South Korea (K-Pop)",
        "description": "Tangga lagu K-Pop terpopuler minggu ini di Korea Selatan",
        "country": "kr",
        "source": ("official", "KR", "top"),
    },
    {
        "id": "chart-jp-top50",
        "name": "Top 50 - Japan (J-Pop)",
        "description": "Tangga lagu J-Pop dan anime terpopuler minggu ini di Jepang",
        "country": "jp",
        "source": ("official", "JP", "top"),
    },
    {
        "id": "chart-uk-top50",
        "name": "Top 50 - United Kingdom",
        "description": "Lagu terpopuler dan terlaris minggu ini di Inggris Raya",
        "country": "uk",
        "source": ("official", "GB", "top"),
    },
    {
        "id": "chart-vn-top50",
        "name": "Top 50 - Vietnam",
        "description": "Bảng xếp hạng âm nhạc thịnh hành tại Việt Nam tuần này",
        "country": "vn",
        "source": ("official", "VN", "top"),
    },
    {
        "id": "chart-br-top50",
        "name": "Top 50 - Brazil",
        "description": "Músicas mais tocadas e populares no Brasil",
        "country": "br",
        "source": ("official", "BR", "top"),
    },
    {
        "id": "chart-mx-top50",
        "name": "Top 50 - Mexico",
        "description": "Las canciones más escuchadas y populares en México",
        "country": "mx",
        "source": ("official", "MX", "top"),
    },
    {
        "id": "chart-es-top50",
        "name": "Top 50 - Spain",
        "description": "Las canciones más populares y escuchadas en España",
        "country": "es",
        "source": ("official", "ES", "top"),
    },
    {
        "id": "chart-it-top50",
        "name": "Top 50 - Italy",
        "description": "I brani più ascoltati e popolari della settimana in Italia",
        "country": "it",
        "source": ("official", "IT", "top"),
    },
]

# Additional countries with active music scenes beyond YouTube Music's ~70 official chart countries
EXTRA_COUNTRIES = [
    ("my", "Malaysia"),
    ("ph", "Philippines"),
    ("sg", "Singapore"),
    ("th", "Thailand"),
    ("tw", "Taiwan"),
    ("hk", "Hong Kong"),
    ("pk", "Pakistan"),
    ("bd", "Bangladesh"),
    ("lk", "Sri Lanka"),
    ("np", "Nepal"),
    ("kz", "Kazakhstan"),
    ("uz", "Uzbekistan"),
    ("az", "Azerbaijan"),
    ("ge", "Georgia"),
    ("am", "Armenia"),
    ("gr", "Greece"),
    ("ie", "Ireland"),
    ("hr", "Croatia"),
    ("rs", "Serbia"),
    ("sk", "Slovakia"),
    ("si", "Slovenia"),
    ("bg", "Bulgaria"),
    ("lt", "Lithuania"),
    ("lv", "Latvia"),
    ("ee", "Estonia"),
    ("is", "Iceland"),
    ("ma", "Morocco"),
    ("tn", "Tunisia"),
    ("dz", "Algeria"),
    ("gh", "Ghana"),
    ("sn", "Senegal"),
    ("et", "Ethiopia"),
    ("tz", "Tanzania"),
    ("jm", "Jamaica"),
    ("cu", "Cuba"),
    ("ve", "Venezuela"),
    ("uy", "Uruguay"),
    ("py", "Paraguay"),
    ("ec", "Ecuador"),
    ("bo", "Bolivia"),
    ("cr", "Costa Rica"),
    ("pa", "Panama"),
    ("do", "Dominican Republic"),
    ("pr", "Puerto Rico"),
    ("lb", "Lebanon"),
    ("jo", "Jordan"),
    ("kw", "Kuwait"),
    ("qa", "Qatar"),
    ("om", "Oman"),
    ("bh", "Bahrain"),
]


def yt_post(url, payload, timeout=12):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def decode_country_code(form_item_key):
    try:
        raw = urllib.parse.unquote(form_item_key)
        decoded = base64.b64decode(raw + "==").decode("latin1", errors="ignore")
        m = re.search(r"country_menu_\d+([A-Z]{2})", decoded)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def extract_chart_playlists(data):
    """Extract (title, playlistId) tuples from a FEmusic_charts response."""
    results = []

    def walk(obj):
        if isinstance(obj, dict):
            if "musicTwoRowItemRenderer" in obj:
                r = obj["musicTwoRowItemRenderer"]
                title = "".join(x.get("text", "") for x in r.get("title", {}).get("runs", []))
                bid = r.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                if bid.startswith("VL"):
                    results.append((title, bid[2:]))
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    return results


def pick_best_chart_id(playlists, mode="top"):
    if not playlists:
        return None
    if mode == "daily":
        for title, pid in playlists:
            if "daily" in title.lower():
                return pid
        for title, pid in playlists:
            if "trending" in title.lower():
                return pid
    else:
        for title, pid in playlists:
            low = title.lower()
            if "top 100" in low and "live performance" not in low:
                return pid
        for title, pid in playlists:
            if "daily" in title.lower():
                return pid
        for title, pid in playlists:
            if "trending" in title.lower():
                return pid
    return playlists[0][1]


def fetch_official_charts():
    """Fetch all official FEmusic_charts country options and their playlist IDs."""
    base = yt_post(YT_BROWSE_URL, {"context": BASE_CONTEXT, "browseId": "FEmusic_charts"})
    opts = []

    def find_opts(obj):
        if isinstance(obj, dict):
            if "musicMultiSelectMenuRenderer" in obj:
                opts.extend(obj["musicMultiSelectMenuRenderer"].get("options", []))
                return
            for v in obj.values():
                find_opts(v)
        elif isinstance(obj, list):
            for v in obj:
                find_opts(v)

    find_opts(base)

    countries = []
    for opt in opts:
        r = opt.get("musicMultiSelectMenuItemRenderer")
        if not r:
            continue
        name = "".join(x.get("text", "") for x in r.get("title", {}).get("runs", []))
        key = r.get("formItemEntityKey", "")
        code = decode_country_code(key)
        if name and code:
            countries.append((code, name, key))

    charts_by_code = {}

    def fetch_one(code, name):
        try:
            d = yt_post(
                YT_BROWSE_URL,
                {"context": BASE_CONTEXT, "browseId": "FEmusic_charts", "formData": {"selectedValues": [code]}},
            )
            pls = extract_chart_playlists(d)
            return code, name, pls
        except Exception:
            return code, name, []

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(fetch_one, code, name) for code, name, _ in countries]
        for fut in as_completed(futures):
            code, name, pls = fut.result()
            if pls:
                charts_by_code[code] = {"name": name, "playlists": pls}

    return countries, charts_by_code


def search_country_chart_playlist(country_name):
    """Search YouTube for a country's Top Songs/Hits playlist and validate it on YouTube Music."""
    queries = [
        f"Top 50 {country_name} music",
        f"Top Hits {country_name} playlist",
        f"{country_name} Top Songs",
    ]
    web_ctx = {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20250101.01.00",
            "hl": "en",
            "gl": "US",
        }
    }
    for q in queries:
        try:
            d = yt_post(
                "https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
                {"context": web_ctx, "query": q, "params": "EgIQAw%3D%3D"},
            )
            txt = json.dumps(d)
            candidates = list(dict.fromkeys(re.findall(r'"playlistId":\s*"(PL[^"]+|RDCLAK5uy_[^"]+)"', txt)))
            for pid in candidates[:5]:
                if validate_playlist(pid):
                    return pid
        except Exception:
            continue
    return None


def validate_playlist(playlist_id):
    """Verify via YouTube Music browse VL<id> that the playlist exists and has > 0 tracks."""
    if not playlist_id:
        return False
    try:
        d = yt_post(YT_BROWSE_URL, {"context": BASE_CONTEXT, "browseId": f"VL{playlist_id}"})
        txt = json.dumps(d)
        # Must contain at least one playable videoId inside playlist items
        if '"musicResponsiveListItemRenderer"' in txt and '"videoId":' in txt:
            return True
    except Exception:
        pass
    return False


def load_existing_playlists():
    path = "api/playlists.json"
    if not os.path.exists(path):
        return {}, None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        by_id = {x["id"]: x for x in data.get("data", []) if "id" in x}
        return by_id, data
    except Exception:
        return {}, None


def main():
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    existing_by_id, existing_doc = load_existing_playlists()

    print("Fetching official country list & charts from YouTube Music FEmusic_charts...", flush=True)
    official_list, charts_by_code = fetch_official_charts()
    print(f"Found {len(charts_by_code)} official YouTube Music chart regions.", flush=True)

    final_items = []
    seen_ids = set()
    flagship_countries = set()

    # 1. Build the 13 flagship charts in exact order at the top
    for spec in FLAGSHIP_SPECS:
        _, code, mode = spec["source"]
        info = charts_by_code.get(code)
        pid = pick_best_chart_id(info["playlists"], mode=mode) if info else None

        if pid and validate_playlist(pid):
            flagship_countries.add(code)
            final_items.append({
                "id": spec["id"],
                "name": spec["name"],
                "description": spec["description"],
                "country": spec["country"],
                "youtubePlaylistId": pid,
                "youtubeUrl": f"https://music.youtube.com/playlist?list={pid}",
            })
            seen_ids.add(spec["id"])
            print(f"  [FLAGSHIP OK] {spec['id']} -> {pid}", flush=True)
        else:
            print(f"  [FLAGSHIP WARN] Could not validate {spec['id']} ({code})", flush=True)

    # 2. Add all remaining official YouTube Music chart countries (~60 more)
    remaining_official = [
        (code, name)
        for code, name, _ in official_list
        if code not in flagship_countries and code in charts_by_code
    ]

    def validate_official(code, name):
        pid = pick_best_chart_id(charts_by_code[code]["playlists"], mode="top")
        if pid and validate_playlist(pid):
            return code, name, pid
        return code, name, None

    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(validate_official, code, name) for code, name in remaining_official]
        official_validated = {}
        for fut in as_completed(futs):
            code, name, pid = fut.result()
            if pid:
                official_validated[code] = (name, pid)

    for code, name in remaining_official:
        if code in official_validated:
            cname, pid = official_validated[code]
            cid = f"chart-{code.lower()}-top50"
            if cid not in seen_ids:
                seen_ids.add(cid)
                final_items.append({
                    "id": cid,
                    "name": f"Top 100 - {cname}",
                    "description": f"Tangga lagu resmi YouTube Music paling populer di {cname}",
                    "country": code.lower(),
                    "youtubePlaylistId": pid,
                    "youtubeUrl": f"https://music.youtube.com/playlist?list={pid}",
                })

    # 3. Expand to 100+ countries via YouTube Music playlist search
    official_lower = {c.lower() for c, _, _ in official_list} | {"gb"}
    extra_targets = [(cc, cname) for cc, cname in EXTRA_COUNTRIES if cc not in official_lower]

    def resolve_extra(cc, cname):
        pid = search_country_chart_playlist(cname)
        return cc, cname, pid

    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = [pool.submit(resolve_extra, cc, cname) for cc, cname in extra_targets]
        extra_results = {}
        for fut in as_completed(futs):
            cc, cname, pid = fut.result()
            if pid:
                extra_results[cc] = (cname, pid)

    for cc, cname in extra_targets:
        if cc in extra_results:
            _, pid = extra_results[cc]
            cid = f"chart-{cc}-top50"
            if cid not in seen_ids:
                seen_ids.add(cid)
                final_items.append({
                    "id": cid,
                    "name": f"Top Hits - {cname}",
                    "description": f"Kompilasi lagu populer dan tangga lagu pilihan di {cname}",
                    "country": cc,
                    "youtubePlaylistId": pid,
                    "youtubeUrl": f"https://music.youtube.com/playlist?list={pid}",
                })

    # Preserve createdAt if item's youtubePlaylistId is unchanged (avoids empty 2-hourly commits)
    changed = existing_doc is None or len(final_items) != len(existing_doc.get("data", []))
    for item in final_items:
        prev = existing_by_id.get(item["id"])
        if prev and prev.get("youtubePlaylistId") == item["youtubePlaylistId"] and prev.get("name") == item["name"]:
            item["createdAt"] = prev.get("createdAt", now_iso)
        else:
            item["createdAt"] = now_iso
            changed = True

    if not changed and existing_doc is not None:
        print(f"No chart ID or country changes ({len(final_items)} charts). Keeping api/playlists.json untouched.")
        return

    output = {
        "success": True,
        "data": final_items,
        "meta": {
            "total": len(final_items),
            "weekStart": now_iso,
            "weekEnd": now_iso,
        },
    }

    os.makedirs("api", exist_ok=True)
    with open("api/playlists.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully synchronized {len(final_items)} verified charts to api/playlists.json")


if __name__ == "__main__":
    main()
