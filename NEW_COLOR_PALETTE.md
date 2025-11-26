# 🎨 New Color Palette

## Color Scheme

### Primary Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Coral Shimmer** | `#FD3021` | `rgb(253, 48, 33)` | Gradient text, grid lines, primary accents |
| **Dark Teal** | `#001413` | `rgb(0, 20, 19)` | Main background |
| **Off-White** | `#FBFFFE` | `rgb(251, 255, 254)` | Text color |
| **Dusty Pink** | `#CEB6BD` | `rgb(206, 182, 189)` | Subtle accents, secondary gradient |

## What Changed

### Before (Purple/Green Cyberpunk)
- Purple (`#9945FF`) and green (`#14F195`) gradient
- Purple grid lines
- Heavy purple glows

### After (Coral/Teal Sophistication)
- Coral (`#FD3021`) shimmer gradient with dusty pink accents
- Coral grid lines with subtle glow
- Dark teal background
- Off-white text for better readability

## Visual Elements Updated

### 1. **Background**
- Base color: Dark teal `#001413`
- Grid overlay: Coral with 15% opacity

### 2. **Logo/Title Gradient**
```css
background: linear-gradient(90deg, #FD3021, #FF6B5B, #FD3021, #CEB6BD);
```
Animated shimmer effect that cycles through coral tones to dusty pink

### 3. **Glow Effects**
- **Coral glow**: `0 0 20px rgba(253, 48, 33, 0.5)`
- **Pink glow**: `0 0 20px rgba(206, 182, 189, 0.5)`

### 4. **Branding**
- Removed all 💎 diamond emojis
- Clean "SizeMatters" text with coral shimmer
- Whale badge changed from 💎 to 🐋

## How to See Changes

### Run Locally:
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

Then open **http://localhost:3000**

## Design Philosophy

The new palette creates a more **sophisticated, mature** look:
- **Dark teal** feels premium and financial
- **Coral shimmer** is energetic but not jarring
- **Dusty pink** adds warmth and subtle elegance
- **Off-white** text is easier on the eyes than pure white

Perfect for a crypto trading social platform! 🚀

