## 🌐 Network & Poster Loading Note

**CineVerse** fetches movie and anime posters dynamically from external APIs (**Jikan**, **Wikipedia**, and **TMDB**) with automatic caching (`@st.cache_data`).

- **Graceful Fallback:** If your network, ISP, or firewall blocks or times out on external poster APIs (such as `api.themoviedb.org`), the app will **not** crash. Instead, it displays a clean fallback card with the title, category, genres, and story summary.
- **Optional DNS Fix (Windows):** If posters fail to load due to ISP/DNS restrictions, switching to public DNS (`8.8.8.8` / `1.1.1.1`) often resolves the timeout issue:
  1. Press `Win + R`, type `ncpa.cpl`, and press **Enter**.
  2. Right-click your active connection (**Wi-Fi** or **Ethernet**) → **Properties** → **Internet Protocol Version 4 (TCP/IPv4)** → **Properties**.
  3. Select **Use the following DNS server addresses**:
     - **Preferred DNS server:** `8.8.8.8`
     - **Alternate DNS server:** `1.1.1.1`
  4. Click **OK**, refresh the browser (`http://localhost:8501`), and press `C` in Streamlit to clear the cache.