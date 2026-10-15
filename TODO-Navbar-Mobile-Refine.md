# Mobile Navlist Refinements
Status: Planning

## Plan:
**Information Gathered:**
- Mobile menu: column flex, toggle .active on nav-container.
- Dropdowns: JS click toggle .dropdown.active.
- Issues: spacing uneven, hover/tap, scroll, swipe animation.

**Code Update Plan:**
1. navbar.css mobile .nav-list: even gap 1.5rem, full width, hover background glow, active state.
2. Scrollable: max-height: 80vh; overflow-y: auto; custom scrollbar.
3. Dropdown swipe: transition height/transform smooth, click only (no hover mobile).
4. Hover/tap: :active glow, JS touch events.

**Dependent Files:**
- static/css/navbar.css
- app/templates/_header.html (JS enhance touch?)

**Followup:**
- Test mobile menu open, scroll long list, tap dropdown swipe out.

