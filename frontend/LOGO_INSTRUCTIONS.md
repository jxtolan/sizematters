# 🦍 Logo Integration Instructions

## Current State
The gorilla emoji (🦍) is being used as a placeholder in coral color.

## Where the Logo Appears:
1. **Header** (top bar next to "SizeMatters")
2. **Create Profile Modal** (above the form)
3. **My Profile Modal** (at the top)

---

## How to Replace with Your Custom Logo

### Option 1: Using an Image File (Recommended)

1. **Save your logo:**
   - Put your gorilla logo in: `frontend/public/logo.png` or `logo.svg`
   - Recommended size: 512x512px or larger (will be scaled down)

2. **Update the components:**

**In `app/page.tsx` (Header):**
```tsx
// Replace this:
<span className="text-5xl" style={{ color: 'var(--color-coral)' }}>🦍</span>

// With this:
<Image 
  src="/logo.png" 
  alt="SizeMatters Logo" 
  width={48} 
  height={48}
  className="w-12 h-12"
  style={{ filter: 'brightness(0) saturate(100%) invert(43%) sepia(96%) saturate(2845%) hue-rotate(347deg) brightness(101%) contrast(98%)' }}
/>
```

**In `components/ProfileCompleteModal.tsx` and `components/MyProfile.tsx`:**
```tsx
// Replace this:
<span className="text-7xl" style={{ color: 'var(--color-coral)' }}>🦍</span>

// With this:
<Image 
  src="/logo.png" 
  alt="SizeMatters Logo" 
  width={80} 
  height={80}
  className="w-20 h-20"
  style={{ filter: 'brightness(0) saturate(100%) invert(43%) sepia(96%) saturate(2845%) hue-rotate(347deg) brightness(101%) contrast(98%)' }}
/>
```

3. **Add the import:**
At the top of each file:
```tsx
import Image from 'next/image'
```

---

### Option 2: Using SVG Component

1. **Create a logo component:**

Create `frontend/components/Logo.tsx`:
```tsx
export const Logo = ({ size = 48, className = "" }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 512 512" 
      fill="currentColor"
      className={className}
      style={{ color: 'var(--color-coral)' }}
    >
      {/* Paste your SVG path data here */}
      <path d="YOUR_SVG_PATH_DATA" />
    </svg>
  )
}
```

2. **Use it in components:**
```tsx
import { Logo } from '@/components/Logo'

// In header:
<Logo size={48} />

// In modals:
<Logo size={80} />
```

---

### Option 3: Keep the Emoji (Current Setup)

The emoji is already styled in coral color and works perfectly! No changes needed.

---

## CSS Filter for Coral Color

If your logo is black and you want to make it coral (#FD3021), use this filter:
```css
filter: brightness(0) saturate(100%) invert(43%) sepia(96%) saturate(2845%) hue-rotate(347deg) brightness(101%) contrast(98%);
```

This converts any black image to coral color!

---

## Tips:

1. **SVG is best** - Scales perfectly at any size
2. **PNG with transparency** - Works great too
3. **File size** - Keep under 50KB for fast loading
4. **The logo image you shared** - Save it as `public/logo.png` and follow Option 1!

---

## Current Locations:

1. `frontend/app/page.tsx` - Line ~192
2. `frontend/components/ProfileCompleteModal.tsx` - Line ~166
3. `frontend/components/MyProfile.tsx` - Line ~197

