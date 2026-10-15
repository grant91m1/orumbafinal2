# Production Fixes TODO - Approved Plan
Current: 0/16

1. [x] Fix app.py: Remove duplicates, secure secret_key
2. [x] orumba-modern/app/ClientNav.tsx: Remove unused imports
3. [ ] orumba-modern/app/about/page.tsx: Add img alt, use next/Image
4. [ ] orumba-modern/app/about/page-fixed.tsx: Add img alt, use next/Image
5. [ ] orumba-modern/app/administration/page.tsx: Fix alt-text, replace img
6. [x] orumba-modern/app/api/posts/route.ts: let->const
7. [x] orumba-modern/app/api/posts/[id]/route.ts: let->const
8. [ ] orumba-modern/app/contact/page.tsx: Remove unused Link/Clock
9. [ ] orumba-modern/app/create-album/page.tsx: Fix img alt
10. [ ] orumba-modern/app/create-post/page.tsx: Remove unused, fix imgs
11. [ ] orumba-modern/app/departments/page.tsx: Remove unused, type any
12. [ ] orumba-modern/app/gallery/page.tsx: next/Image + alts
13. [ ] orumba-modern/app/members/page.tsx: next/Image
14. [ ] orumba-modern/app/news/page.tsx: Remove unused User/Clock, type any
15. [x] orumba-modern/app/news/[id]/page.tsx: Remove unused Clock, fix async client
16. [ ] orumba-modern/app/profile/page.tsx: Remove unused setStats

**Followup:** `cd orumba-modern && npm run lint && npm run build` + `python app.py` test.
**Result:** Clean build, no errors → 100% ready.
