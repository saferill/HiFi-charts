# HiFi Charts API (`HiFi-charts`)

Automated trending music chart playlists and regional index provider for **[HiFi Music](https://github.com/saferill/HiFi)**.

This repository serves as a zero-cost, static API backend hosted directly via GitHub raw storage, giving the mobile and desktop clients fast, cacheable access to trending music lists across different regions.

---

## Endpoints

* **Production Feed**: [`api/playlists.json`](./api/playlists.json)  
  Raw URL: `https://raw.githubusercontent.com/saferill/HiFi-charts/refs/heads/main/api/playlists.json`

---

## Data Schema

The feed indexes curated YouTube Music chart playlists consumed directly by `com.maxrave.kotlinytmusicscraper.models.response.HiFiChartResponse`:

```json
{
  "success": true,
  "data": [
    {
      "id": "chart-id-top50",
      "name": "Top 50 - Indonesia",
      "description": "Lagu-lagu terpopuler dan paling sering diputar minggu ini di Indonesia",
      "country": "id",
      "youtubePlaylistId": "PL4fGSIndQ80V87lTz4hLdEsm7A_7a_Bwb",
      "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80V87lTz4hLdEsm7A_7a_Bwb",
      "createdAt": "2026-11-12T11:41:17Z"
    },
    {
      "id": "chart-global-top50",
      "name": "Top 50 - Global",
      "description": "Lagu paling populer dan viral di seluruh dunia minggu ini",
      "country": "global",
      "youtubePlaylistId": "PL4fGSIndQ80Z1hO4kKkL4Qz8S-aF8f-6E",
      "youtubeUrl": "https://music.youtube.com/playlist?list=PL4fGSIndQ80Z1hO4kKkL4Qz8S-aF8f-6E",
      "createdAt": "2026-11-12T11:41:17Z"
    }
  ],
  "meta": {
    "total": 13,
    "weekStart": "2026-11-12T11:41:17Z",
    "weekEnd": "2026-11-12T11:41:17Z"
  }
}
```

---

## Supported Regions

| Code | Region | Primary Chart |
|------|--------|---------------|
| `id` | Indonesia | Top 50 & Pop Teratas |
| `global` | Global | Top 50 & Today's Biggest Hits |
| `us` | United States | Top 50 United States |
| `kr` | South Korea | Top 50 South Korea (K-Pop) |
| `jp` | Japan | Top 50 Japan (J-Pop) |
| `uk` | United Kingdom | Top 50 United Kingdom |
| `vn` | Vietnam | Top 50 Vietnam |
| `br` | Brazil | Top 50 Brazil |
| `mx` | Mexico | Top 50 Mexico |
| `es` | Spain | Top 50 Spain |
| `it` | Italy | Top 50 Italy |

---

## Automated Synchronization

Charts are verified and refreshed every 12 hours via GitHub Actions (`.github/workflows/sync-charts.yml`) using `scripts/sync-charts.py`.

---

## License

Open-source under the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).
