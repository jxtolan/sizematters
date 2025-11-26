# 🎨 Centralized Color System

## The Problem We Fixed
Colors were scattered across 20+ files. Changing one color meant updating dozens of places.

## The Solution
**Single source of truth** in `app/globals.css` using CSS variables.

---

## Color Palette

### Primary Colors (in `app/globals.css`)

```css
:root {
  --color-bg-dark: #001413;      /* Dark teal background */
  --color-bg-darker: #000a09;    /* Even darker teal */
  --color-coral: #FD3021;        /* Coral shimmer */
  --color-coral-light: #FF6B5B;  /* Light coral */
  --color-pink: #CEB6BD;         /* Dusty pink */
  --color-text: #FBFFFE;         /* Off-white text */
}
```

---

## How to Use

### Option 1: Tailwind Classes (Recommended)
After running `npm run dev`, these classes are available:

```tsx
<div className="bg-coral">Coral background</div>
<div className="bg-coral-light">Light coral</div>
<div className="bg-pink">Dusty pink</div>
<div className="bg-bg-dark">Dark teal</div>
<div className="text-coral">Coral text</div>
<div className="text-pink">Pink text</div>
<div className="border-coral">Coral border</div>
```

### Option 2: CSS Variables (For custom styles)
```tsx
<div style={{ background: 'var(--color-coral)' }}>
  Using CSS variable
</div>
```

### Option 3: Utility Classes (From globals.css)
```tsx
<button className="bg-coral-gradient">
  Coral gradient button
</button>

<button className="bg-coral-pink-gradient">
  Coral to pink gradient
</button>
```

---

## Pre-made Utility Classes

Located in `app/globals.css`:

- `.bg-coral` - Solid coral background
- `.bg-coral-gradient` - Coral → Light coral gradient
- `.bg-coral-pink-gradient` - Coral → Pink gradient
- `.text-coral` - Coral text
- `.text-pink` - Pink text
- `.border-coral` - Coral border
- `.border-pink` - Pink border
- `.gradient-text` - Animated shimmer text (coral/pink)
- `.glass` - Dark teal glassmorphism
- `.glow-coral` - Coral glow effect
- `.glow-pink` - Pink glow effect

---

## Changing Colors Globally

### To Change the Coral Color:
1. Open `frontend/app/globals.css`
2. Find `:root {`
3. Change `--color-coral: #FD3021;` to your new color
4. Save - ALL components update automatically! ✨

### To Change the Background:
Change `--color-bg-dark: #001413;` and it updates everywhere.

---

## Migration Guide

### Old Way (❌ Don't do this):
```tsx
className="bg-gradient-to-r from-[#FD3021] to-[#FF6B5B]"
```

### New Way (✅ Do this):
```tsx
className="bg-coral-gradient"
// or
style={{ background: 'linear-gradient(90deg, var(--color-coral), var(--color-coral-light))' }}
```

---

## Component-Specific Overrides

### Wallet Adapter Button
Already styled in `globals.css`:
```css
.wallet-adapter-button {
  background: linear-gradient(90deg, var(--color-coral), var(--color-coral-light)) !important;
}
```

### Glass Effect
```css
.glass {
  background: var(--color-bg-dark);
  border: 1px solid rgba(253, 48, 33, 0.2);
}
```

---

## Future Color Changes

Want to try a new palette? Just update these 6 variables:

```css
:root {
  --color-bg-dark: #YOUR_BG_COLOR;
  --color-bg-darker: #YOUR_DARKER_BG;
  --color-coral: #YOUR_PRIMARY_COLOR;
  --color-coral-light: #YOUR_PRIMARY_LIGHT;
  --color-pink: #YOUR_ACCENT_COLOR;
  --color-text: #YOUR_TEXT_COLOR;
}
```

Save → Refresh → Entire app updates! 🎉

---

## Benefits

✅ **One place to change colors** (not 50+ files)  
✅ **Consistent colors** across the entire app  
✅ **Easy to experiment** with new palettes  
✅ **Better performance** (CSS variables are native)  
✅ **Type-safe in Tailwind** config  

---

## Files Modified

1. `frontend/app/globals.css` - Main color definitions
2. `frontend/tailwind.config.js` - Tailwind integration
3. All components now reference these colors

**Next time you want to change colors, just edit `globals.css`!**

