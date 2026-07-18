# 🚀 StudyMate AI — 3D Website Master Prompt

> Use this prompt to rebuild the ultimate 3D landing website for StudyMate AI.
> Share this with any developer or AI to recreate the exact vision.

---

## 🎯 PROJECT OVERVIEW

**Brand:** StudyMate AI — *Your AI-Powered Learning Companion*
**Tone:** Premium, futuristic, academic, energetic
**Target:** Students (ages 16–30), self-learners, competitive students
**Colors:** Primary `#7C4DFF` (purple) | Secondary `#448AFF` (blue) | Accent `#FFD700` (gold)
**Background:** `#08081A` (deep midnight)
**Fonts:** Headings → Poppins (700–900) | Body → Inter (400–600)

The website must feel like a **AAA game trailer meets a premium product landing page** — smooth 3D, glassmorphism, micro-animations everywhere, and ultra-responsive.

---

## 🏗️ SECTION-BY-SECTION SPECIFICATION

### 0. GLOBAL ELEMENTS

**Navbar (fixed top):**
- Glassmorphism: `background: rgba(8,8,26,0.75); backdrop-filter: blur(24px) saturate(2)`
- Border bottom: `1px solid rgba(124,77,255,0.08)`
- Left: Logo "◆ StudyMate AI" with gold-purple gradient text
- Right: Links → Features, Process, Stack, Screens + external links to PPT/Trailer
- **Behavior:** Hides on scroll down, reappears on scroll up (use `transform: translateY(-100%)`)
- Link hover: underline slide animation (`::after` pseudo-element width 0→100%)

**3D Background Canvas (fixed position):**
- `position: fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none`
- Rendered with Three.js r152 — WebGL with alpha, antialias, ACESFilmicToneMapping
- Must NOT interfere with UI interaction

**Ambient Glow Orbs (CSS):**
- 3 floating blurred circles behind content
- Orb 1: 600px, `rgba(124,77,255,0.06)`, top-right
- Orb 2: 450px, `rgba(68,138,255,0.05)`, bottom-left
- Orb 3: 350px, `rgba(255,215,0,0.03)`, center
- Animation: slow float with translate transforms, 25s cycle, staggered delays

---

### 1. 🎬 HERO SECTION

**Layout:** Two-column grid (`1fr 1fr`) — text left, 3D phone right

**Left Column:**
- Badge: pill shape, `rgba(124,77,255,0.12)` background, gold text "🚀 Your AI-Powered Learning Companion", letter-spaced, fade-down animation
- Main title: Poppins 900, `clamp(44px, 6vw, 80px)`, line-height 1.05
  - "STUDYMATE" in purple→blue gradient
  - "AI" in gold→orange gradient
- Subtitle: Inter, 16–18px, color `#A0A0C0`, max-width 480px, line-height 1.8
- Two buttons side by side:
  - Primary: gradient purple→blue, 30px radius, `box-shadow: 0 8px 32px rgba(124,77,255,0.3)`, hover lifts 3px + shadow increases
  - Secondary: `rgba(255,255,255,0.04)` bg, `1px solid rgba(255,255,255,0.12)`, blur backdrop, hover gets purple border
- Stats row: 4 items → "150+ Dart Files", "20 Screens", "23 Achievements", "38 Subjects"
  - Numbers: Poppins 32px 900, gradient purple→gold, animated counter (counts up on scroll)
- **Animation:** Each element staggers in with `fadeUp` (opacity 0→1, translateY 30→0), delays 0s→0.15s→0.3s→0.45s→0.6s

**Right Column — 3D Phone Mockup:**
- CSS 3D perspective container: `perspective(1200px)`
- Phone: 260×520px, `border-radius:36px`, gradient dark background, `2px solid rgba(124,77,255,0.2)`, 3D shadow
- Mockup screen content:
  - Notch at top (110×22px, black, rounded bottom)
  - Header: "◆ StudyMate" logo + live clock (updates every 10s via JS)
  - Stats row: three chips (XP Today 1,280 | 🔥 Streak 7 | Lv.8)
  - Progress bars: Mathematics 78%, Physics 45%, CS 92% — animated width
  - "5 flashcards due" text
  - Dot indicators (5 dots, center active)
  - Glare overlay: `linear-gradient(135deg, rgba(255,255,255,0.06), transparent)`
- **Animations:**
  - Floating: `@keyframes phoneFloat` — translateY(0→-24px) + rotateY(-5°→5°) + rotateX(3°→-3°) over 6s, infinite
  - Mouse tilt: on mousemove, calculate offset from center → apply `rotateY(±25deg) rotateX(±25deg) translateZ(30px)` via JS
  - On mouseleave: smoothly return to floating animation state

---

### 2. ✨ FEATURES SECTION

**Header:**
- Label pill: "✦ Features"
- Title: "Everything You Need to Master Learning" with "Master Learning" in purple-blue gradient
- Subtitle: centered, max-width 560px

**Feature Cards Grid:** `grid-template-columns: repeat(auto-fit, minmax(320px, 1fr))`, gap 20px

**Each card (6 total):**

| # | Icon | Title | Tag | Tag Color |
|---|------|-------|-----|-----------|
| 1 | 🧠 | FSRS Spaced Repetition | Smart Learning | `#7C4DFF` |
| 2 | 🤖 | AI Mentor (Gemini) | Artificial Intelligence | `#448AFF` |
| 3 | 🎮 | Gamification Engine | Gamification | `#FFD700` |
| 4 | 📊 | Analytics Dashboard | Analytics | `#4CAF50` |
| 5 | 👥 | Social Learning | Social | `#00BCD4` |
| 6 | ⏱️ | Focus Timer | Productivity | `#FF9800` |

**Card Design:**
- Background: `rgba(26,26,46,0.7)` with `backdrop-filter: blur(16px)`
- Border: `1px solid rgba(124,77,255,0.12)`, hover becomes `rgba(124,77,255,0.35)`
- Border-radius: 20px, padding: 36px 28px
- Icon: 52px, transitions with `cubic-bezier(0.34, 1.56, 0.64, 1)` — on hover: `scale(1.2) rotate(8deg)`
- Title: 18px, 700 weight
- Description: 14px, `#A0A0C0`, line-height 1.7
- Tag: pill at bottom, 10px uppercase letter-spaced

**Card Micro-interactions:**
- **Mouse-follow glow:** `::before` pseudo-element with `radial-gradient(ellipse at var(--mx) var(--my), rgba(124,77,255,0.15), transparent 70%)` — update `--mx`/`--my` CSS vars on mousemove
- **Hover lift:** `translateY(-10px) scale(1.02)` with `box-shadow: 0 30px 80px rgba(124,77,255,0.15)`, border brightens
- **Scroll reveal:** `translateY(60px) scale(0.95)` + `opacity: 0` → on scroll intersection, add class `.v` → `translateY(0) scale(1)` + `opacity: 1` with `transition: all 0.6s cubic-bezier(0.22, 1, 0.36, 1)`
- Stagger delays: 0ms, 100ms, 200ms, 300ms, 400ms, 500ms via `data-d` attribute

---

### 3. ⚡ PROCESS / HOW IT WORKS SECTION

**Header:** "How StudyMate AI Works" with "StudyMate AI" in gradient

**Step Cards (5 steps):**
- Vertical list, max-width 700px, centered
- Each card: flex row with step number (left) + text content (right)
- Background: `rgba(26,26,46,0.6)`, border-radius 18px, backdrop-filter blur 14px
- Step number: Poppins 34px 900, purple→blue gradient text, min-width 48px, centered
- Step title: 15px 700 weight
- Step description: 13px, `#A0A0C0`

**Steps:**
1. Open & Sync — Splash screen with auto-login, dashboard with XP goal, due flashcards, streak
2. Review Flashcards — FSRS algorithm, rate Again/Hard/Good/Easy, memory pattern learning
3. Focus Session — Pomodoro timer, XP per minute, distraction-free studying
4. Take a Quiz — Subject-wise quizzes, performance tracking, weak area identification
5. Analyze & Repeat — Analytics, daily rewards, leaderboards, continuous improvement

**Animations:**
- **Alternating slide-in:** odd cards `translateX(-40px)`, even cards `translateX(40px)`
- On scroll: `translateX(0)` + `opacity: 1` with `.v` class
- Hover: `scale(1.01)`, border brightens

---

### 4. 🔧 TECH STACK SECTION

**Header:** "Built With Modern Tools" with "Modern Tools" in gradient

**Tech Chips:** Flex-wrap centered grid, gap 10px

| Icon | Name | Version |
|------|------|---------|
| 🦋 | Flutter | 3.44.4 |
| 🎯 | Dart | 3.12.2 |
| 🗄️ | SQLite | sqflite |
| 🔮 | Riverpod | 2.6.1 |
| 🤖 | Gemini AI | API |
| 📈 | fl_chart | 0.69.2 |
| 📷 | mobile_scanner | • |
| 📦 | SharedPrefs | 2.2.3 |
| 🏗️ | Gradle | 8.11.1 |
| 🎨 | Google Fonts | 6.2.1 |
| 👤 | Google Sign-In | • |
| 🧪 | Flutter Test | • |
| 🔄 | FSRS | Algorithm |
| 🧊 | Three.js | r152 |

**Chip Design:**
- Background: `rgba(26,26,46,0.6)`, border `rgba(124,77,255,0.1)`
- Border-radius: 25px, padding: 8px 18px
- Icon 18px, name 13px 600 weight, version 10px muted

**Animations:**
- Scroll reveal: `scale(0.8)` + `opacity: 0` → `.v` → `scale(1)` + `opacity: 1`
- Transition: `all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)` — elastic feel
- Hover: `translateY(-4px) scale(1.06)` + glow

---

### 5. 📱 SCREENS CAROUSEL

**Header:** "20+ Beautifully Designed Screens" with "Designed Screens" in gradient

**Horizontal Scroll Container:**
- `display: flex; overflow-x: auto; scroll-snap-type: x mandatory`
- Custom scrollbar: 3px height, purple thumb
- Gap: 16px, padding: 20px 0

**Screen Cards (13):**
- Min-width 180px, height 360px, border-radius 22px
- Dark gradient background, `1px solid rgba(124,77,255,0.1)`
- Content: 36px emoji icon, title (13px bold), description (11px muted)
- Hover: `scale(1.04) translateY(-8px)`, border brightens

**Screens showcase:**
🏠 Home → ⏱️ Focus → 📝 Notes → 🃏 Flashcards → 📊 Quizzes → 🧠 AI Mentor → 📈 Analytics → 👥 Friends → 🏆 Leaderboard → 🎯 Achievements → ⭐ Daily Rewards → 👤 Profile → ⚙️ Settings

---

### 6. 🎯 CALL TO ACTION

**Layout:** Centered, padding 120px 24px
- Large title: "Ready to Level Up?" with "Level Up" in gold gradient
- Subtitle: 16px, `#A0A0C0`, max-width 480px
- Three buttons: Feature Presentation, How It's Made, Watch Trailer

---

### 7. FOOTER
- Centered, small text, border-top separator, "Built with ❤️ by Suzume for Rushikesh • July 2026"

---

## 🧊 THREE.JS 3D SCENE SPECIFICATION

**Scene Setup:**
- PerspectiveCamera: FOV 55, z-position 14
- ACESFilmic tone mapping, exposure 1.0
- 2 directional lights: purple `#7c4dff` (intensity 3) from top-right, blue `#448aff` (intensity 1.5) from bottom-left
- Ambient light: `#303050`

**Objects:**

1. **Torus Knot** (center-left):
   - Geometry: radius 1.6, tube 0.5, 180 segments, 24 tubular segments
   - Material: MeshPhysicalMaterial, color `#7C4DFF`, emissive `#448AFF`, emissiveIntensity 0.08, metalness 0.2, roughness 0.3, clearcoat 0.6, opacity 0.65, transparent
   - Position: `(-3.5, 0.5, 0)`
   - Rotation: +0.005/x, +0.01/y, +0.003/z per frame
   - Pulsing emissive: `0.05 + 0.1 * abs(sin(time * 2))`

2. **Outer Ring** (surrounding torus knot):
   - TorusGeometry: radius 2.2, tube 0.05, 64 segments
   - Color `#448AFF`, emissive `#7C4DFF`, emissiveIntensity 0.05, metalness 0.4, roughness 0.25, opacity 0.2
   - Rotated: `PI/3` on x, `PI/4` on z
   - Follows knot position + rotation

3. **6 Floating Icosahedrons** (around the scene):
   - IcosahedronGeometry with detail 0
   - Sizes: 0.28–0.55
   - Colors alternating: purple, blue, gold
   - Each has orbital motion via `sin(time * 0.3 + i)` and `cos(time * 0.4 + i * 1.5)`
   - Slow self-rotation: ±0.003/x, ±0.005/y per frame

4. **Particle Field** (1,500 points):
   - Sphere distribution: radius 9–16, random theta/phi
   - Colors: purple (40%), blue (30%), gold (30%)
   - Size: 0.035, additive blending, opacity 0.4
   - Slow rotation: 0.0003/x, 0.0006/y per frame

5. **Connecting Lines** (180 segments):
   - Between random nearby particles (distance < 1.8)
   - Color `#7C4DFF`, opacity 0.04
   - Follows particle rotation

**Mouse Interaction:**
- Track mouse position normalized to `(-1, 1)` range
- Smooth interpolation: `current += (target - current) * 0.03`
- Camera position shifts: `x = mouseX * 0.4`, `y = mouseY * 0.3`
- Camera always looks at `(0, 0, 0)`
- Torus knot position: `x += (mouseX * 0.8 - 3.5 - currentX) * 0.02`

---

## 🎬 ANIMATION REFERENCE

| Element | Trigger | Animation | Duration | Easing |
|---------|---------|-----------|----------|--------|
| Hero badge | Page load | fadeDown | 0.8s | ease |
| Hero title | Page load | fadeUp + 0.15s delay | 0.8s | ease |
| Hero subtitle | Page load | fadeUp + 0.3s delay | 0.8s | ease |
| Hero buttons | Page load | fadeUp + 0.45s delay | 0.8s | ease |
| Hero stats | Page load | fadeUp + 0.6s delay | 0.8s | ease |
| Counters | Scroll | Number count-up (eased) | 2s | cubic-out |
| Feature cards | Scroll | translateY+scale+opacity | 0.6s | cubic-bezier(.22,1,.36,1) |
| Feature hover | Mouse | translateY+scale+border+shadow | 0.5s | cubic-bezier(.22,1,.36,1) |
| Feature hover (icon) | Mouse | scale+rotate | 0.6s | cubic-bezier(.34,1.56,.64,1) |
| Feature glow follow | Mouse | radial position | 0.5s | ease |
| Step cards | Scroll | slide from left/right | 0.6s | cubic-bezier(.22,1,.36,1) |
| Tech chips | Scroll | scale+opacity | 0.5s | cubic-bezier(.34,1.56,.64,1) |
| Phone float | Auto | translateY+rotate | 6s | ease-in-out infinite |
| Phone mouse tilt | Mouse | rotateY+rotateX+translateZ | direct | none |
| 3D objects | Frame | rotation | per-frame | linear |
| 3D emissive pulse | Frame | emissiveIntensity | per-frame | sine |
| Camera parallax | Mouse | position | per-frame | 0.03 lerp |
| Navbar | Scroll | translateY(-100%) | 0.5s | cubic-bezier(.22,1,.36,1) |
| Nav link underline | Hover | width 0→100% | 0.3s | ease |

---

## 📱 RESPONSIVE BREAKPOINTS

**768px (tablet):**
- Hero grid → single column, centered text
- Stats → flex-wrap, smaller gap
- Phone → 200×400px
- Feature grid → 1 column
- Section padding → 60px 16px

**480px (phone):**
- Phone → 160×320px
- Hero title → 32px
- Smaller phone screen padding

---

## 📂 ASSETS TO CREATE

| Asset | Description |
|-------|-------------|
| `index.html` | Main 3D landing page (all CSS+JS inline) |
| Three.js CDN | `https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js` |
| Font CDN | Google Fonts: Inter + Poppins |

**No external images needed** — all visuals are emoji + Three.js + CSS.

---

## 🔗 LINK STRUCTURE

| Link | Target |
|------|--------|
| `/#features` | Scroll to features section |
| `/#process` | Scroll to process section |
| `/#tech` | Scroll to tech stack section |
| `/#screens` | Scroll to screens section |
| `presentation/features.html` | 20-slide features PPT |
| `presentation/how-its-made.html` | 22-slide dev deep-dive PPT |
| `studymate_cinematic.mp4` | 80s cinematic trailer |

---

## ✅ DELIVERABLE CHECKLIST

- [ ] Three.js scene renders with all 3D objects
- [ ] Mouse parallax works on camera + torus knot
- [ ] Phone mockup floats and tilts with mouse
- [ ] All 6 feature cards have glow-follow + hover lift
- [ ] Scroll reveals work for cards, steps, chips
- [ ] Counters animate up on scroll
- [ ] Navbar hides/shows on scroll direction
- [ ] Live clock on phone mockup
- [ ] Responsive at 768px and 480px
- [ ] Smooth scroll for anchor links
- [ ] Glassmorphism on all cards and navbar
- [ ] Gold/purple/blue gradient text on titles
- [ ] No JavaScript errors in console
- [ ] Deployed to GitHub Pages

---

> **Built by Suzume • July 2026**
> *Share this prompt to recreate the exact StudyMate AI 3D experience.*
