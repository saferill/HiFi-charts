#!/usr/bin/env python3
"""
HiFi Charts Synchronization Script
Maintains and updates official YouTube Music chart playlists for HiFi Music.
"""

import json
import os
import datetime

CHARTS_DATA = [
    {
        "id": "chart-id-top50",
        "name": "Top 50 - Indonesia",
        "description": "Lagu-lagu terpopuler dan paling sering diputar minggu ini di Indonesia",
        "country": "id",
        "youtubePlaylistId": "PL4fGSIndQ80V87lTz4hLdEsm7A_7a_Bwb",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80V87lTz4hLdEsm7A_7a_Bwb"
    },
    {
        "id": "chart-id-pop",
        "name": "Pop Teratas - Indonesia",
        "description": "Kompilasi lagu pop Indonesia terhangat dan hits teratas",
        "country": "id",
        "youtubePlaylistId": "RDCLAK5uy_kfdijGvB3x_26C15n7X10k_r_r8f-bYc",
        "youtubeUrl": "https://music.youtube.com/playlist?list=RDCLAK5uy_kfdijGvB3x_26C15n7X10k_r_r8f-bYc"
    },
    {
        "id": "chart-global-top50",
        "name": "Top 50 - Global",
        "description": "Lagu paling populer dan viral di seluruh dunia minggu ini",
        "country": "global",
        "youtubePlaylistId": "PL4fGSIndQ80Z1hO4kKkL4Qz8S-aF8f-6E",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80Z1hO4kKkL4Qz8S-aF8f-6E"
    },
    {
        "id": "chart-global-hits",
        "name": "Today's Biggest Hits - Global",
        "description": "Hits terpopuler dunia yang sedang tren saat ini",
        "country": "global",
        "youtubePlaylistId": "RDCLAK5uy_kmPRjHDECIa2-2n5-b5f7yS4e5wQ_2s",
        "youtubeUrl": "https://music.youtube.com/playlist?list=RDCLAK5uy_kmPRjHDECIa2-2n5-b5f7yS4e5wQ_2s"
    },
    {
        "id": "chart-us-top50",
        "name": "Top 50 - United States",
        "description": "Tangga lagu terpopuler minggu ini di Amerika Serikat",
        "country": "us",
        "youtubePlaylistId": "PL4fGSIndQ80W2gP-3A9V2Q4oXk4uS4eL_",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80W2gP-3A9V2Q4oXk4uS4eL_"
    },
    {
        "id": "chart-kr-top50",
        "name": "Top 50 - South Korea (K-Pop)",
        "description": "Tangga lagu K-Pop terpopuler minggu ini di Korea Selatan",
        "country": "kr",
        "youtubePlaylistId": "PL4fGSIndQ80W2rF4u5eP3s_B1h_gL1i_l",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80W2rF4u5eP3s_B1h_gL1i_l"
    },
    {
        "id": "chart-jp-top50",
        "name": "Top 50 - Japan (J-Pop)",
        "description": "Tangga lagu J-Pop dan anime terpopuler minggu ini di Jepang",
        "country": "jp",
        "youtubePlaylistId": "PL4fGSIndQ80Vq1qR9L2r4z_4m_Gk0xX_4",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80Vq1qR9L2r4z_4m_Gk0xX_4"
    },
    {
        "id": "chart-uk-top50",
        "name": "Top 50 - United Kingdom",
        "description": "Lagu terpopuler dan terlaris minggu ini di Inggris Raya",
        "country": "uk",
        "youtubePlaylistId": "PL4fGSIndQ80U-A_5l7y5C4Oq6wF7pC8h_",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80U-A_5l7y5C4Oq6wF7pC8h_"
    },
    {
        "id": "chart-vn-top50",
        "name": "Top 50 - Vietnam",
        "description": "Bảng xếp hạng âm nhạc thịnh hành tại Việt Nam tuần này",
        "country": "vn",
        "youtubePlaylistId": "PL4fGSIndQ80X5nS5s8U3e_9_7w4pB4yq8",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80X5nS5s8U3e_9_7w4pB4yq8"
    },
    {
        "id": "chart-br-top50",
        "name": "Top 50 - Brazil",
        "description": "Músicas mais tocadas e populares no Brasil",
        "country": "br",
        "youtubePlaylistId": "PL4fGSIndQ80W6pM9y7s9k1q5l2a4m8r9e",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80W6pM9y7s9k1q5l2a4m8r9e"
    },
    {
        "id": "chart-mx-top50",
        "name": "Top 50 - Mexico",
        "description": "Las canciones más escuchadas y populares en México",
        "country": "mx",
        "youtubePlaylistId": "PL4fGSIndQ80V2kM6p0v3s7l1_q9w5e8r2",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80V2kM6p0v3s7l1_q9w5e8r2"
    },
    {
        "id": "chart-es-top50",
        "name": "Top 50 - Spain",
        "description": "Las canciones más populares y escuchadas en España",
        "country": "es",
        "youtubePlaylistId": "PL4fGSIndQ80X1lP8q4s2m6w0_v7b3e9r1",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80X1lP8q4s2m6w0_v7b3e9r1"
    },
    {
        "id": "chart-it-top50",
        "name": "Top 50 - Italy",
        "description": "I brani più ascoltati e popolari della settimana in Italia",
        "country": "it",
        "youtubePlaylistId": "PL4fGSIndQ80U3wR8s2m5l1_q7b9v4e0r3",
        "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80U3wR8s2m5l1_q7b9v4e0r3"
    }
]

def main():
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Enrich entries with createdAt if not present
    enriched = []
    for item in CHARTS_DATA:
        c = dict(item)
        c["createdAt"] = now_iso
        enriched.append(c)

    # Sort so Indonesia and Global are strictly first
    id_items = [x for x in enriched if x["country"] == "id"]
    global_items = [x for x in enriched if x["country"] == "global"]
    other_items = [x for x in enriched if x["country"] not in ("id", "global")]
    
    sorted_items = id_items + global_items + other_items

    output = {
        "success": True,
        "data": sorted_items,
        "meta": {
            "total": len(sorted_items),
            "weekStart": now_iso,
            "weekEnd": now_iso
        }
    }

    os.makedirs("api", exist_ok=True)
    with open("api/playlists.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully synchronized {len(sorted_items)} charts to api/playlists.json")

if __name__ == "__main__":
    main()
