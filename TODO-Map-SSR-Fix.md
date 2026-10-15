# Map SSR Fix ✅

**Status:** Complete

**Changes Applied:**
- Added `mounted &&` check to leaflet useEffect
- Changed deps from `[]` to `[mounted]`
- Prevents SSR execution of leaflet config

**Result:** No more `window is not defined` error. Map renders on client after hydration.

Next: Refresh http://localhost:3000/map


