# HiFi Charts API (`HiFi-charts`)

Automated trending music chart playlists and regional index provider for **[HiFi Music](https://github.com/saferill/HiFi)**.

This repository serves as a zero-cost, static API backend hosted directly via GitHub raw storage, giving the mobile and desktop clients fast, cacheable access to trending music lists across different regions.

---

## Endpoints

* **Production Feed**: [`api/playlists.json`](./api/playlists.json)  
  Raw URL: `https://raw.githubusercontent.com/saferill/HiFi-charts/refs/heads/main/api/playlists.json`

---

## Data Schema

The feed indexes curated playlists grouped by category and country codes:

```json
{
  "lastUpdated": "2026-11-11T00:00:00Z",
  "version": 1,
  "regions": ["id", "global"],
  "categories": [
    {
      "id": "trending",
      "title": "Trending Charts",
      "playlists": [
        {
          "id": "PL4fGSIFgk540-X_eYp_mE11a5A_gBq0wX",
          "title": "Top 50 - Indonesia",
          "subtitle": "Daily most-streamed tracks in Indonesia",
          "thumbnail": "https://i.ytimg.com/vi/...",
          "country": "id"
        },
        {
          "id": "PL4fGSIFgk542k_3M19B86f8K8i0x6wB4r",
          "title": "Global Top 100",
          "subtitle": "Most popular tracks worldwide",
          "thumbnail": "https://i.ytimg.com/vi/...",
          "country": "global"
        }
      ]
    }
  ]
}
```

---

## How It Works in HiFi

1. On launch, the HiFi client issues an asynchronous GET request to `api/playlists.json`.
2. The response is cached locally in SQLite/DataStore. If the device is offline, cached charts are displayed seamlessly.
3. Users can switch their chart region directly from the home feed or settings drawer without reloading the app.

---

## Maintenance

Charts are verified and updated on a regular schedule via `scripts/sync-charts.sh`. Broken playlists are replaced with active official charts to ensure continuous playback availability.

---

## License

Open-source under the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).
