
# Chronos: Temporal Legacy Vault

> "Capturing the fragments of today for the clarity of tomorrow."

**Chronos** is a luxury minimalist digital sanctuary designed for intentional reflection. It acts as a **nervous system regulator**—an anti-doomscrolling tool that allows you to compose letters, attach "visual echoes" (photos), and record audio to be delivered to your future self. By locking memories behind a temporal gate, Chronos transforms social posting into a private ritual of mindfulness, quarantining your mental noise.

---

## 📜 The Purpose

In an era of instant gratification and ephemeral content, Chronos asks you to slow down. Human brains hate "open loops." If you have an intrusive thought and put it in a standard notes app, you just keep re-reading it. If you lock it in Chronos and the math physically refuses to let you see it for a month, your brain is forced to drop the loop. 

## ✨ Key Features

- **Compose Across Time**: Write rich, serif-styled letters to the future with an elegant editor.
- **Visual & Voice Echoes**: Attach images and audio recordings to your capsules to ground your memories in reality.
- **Temporal Gates**: Choose your horizon—from a single "Moment" (1 day) to a full "Decade."
- **The Vault**: A curated gallery of your pending and revealed history, styled as an elegant stationery collection with a dramatic editorial layout.
- **Reflections**: Once a capsule is revealed, add a modern perspective to your past thoughts to see how much you've grown.
- **Premium Waitlist**: Long-term horizons (Year, Decade) and unlimited Moon capsules are locked behind a premium tier (currently a demo waitlist).
- **Share the Void**: Generate a high-resolution, cryptographic-style "tombstone" card to share on social media, proving you locked a thought without revealing the content.

---

## ⚙️ Technical Deep Dive & Architecture

Chronos is built as a **Local-First Single Page Application (SPA)**. The architecture is designed to prioritize absolute user privacy, meaning the application logic runs entirely within the client's browser.

### 1. Data Persistence & Media Handling
- **Storage Engine**: Data is persisted using the browser's native `localStorage` API. 
- **Media Encoding**: Images and audio are not uploaded to a CDN. Instead, the `FileReader` API converts images, and the `MediaRecorder` API converts microphone streams (`audio/webm`), directly into **Base64 Data URIs**. These strings are then encrypted and stored locally.
- *Note on Scaling*: `localStorage` typically has a 5MB limit. Future iterations will migrate to `IndexedDB` to support larger media payloads.

### 2. Security & Encryption (Local-First)
- **AES-256 Encryption at Rest**: Before any capsule is committed to `localStorage`, the sensitive fields (`content`, `reflection`, `imageUrl`, `audioUrl`) are mathematically locked using `crypto-js` AES encryption. 
- **Targeted Encryption**: The UI metadata (`unlockAt`, `title`, `id`) remains in plain text. This allows the React frontend to render the Vault gallery, calculate countdown timers, and manage state without needing to decrypt the private payloads.
- **Zero-Knowledge**: Your data never leaves your device. There is no database, no cloud sync, and no backend API receiving your thoughts. You can verify this by monitoring the Network tab in your browser's Developer Tools.
- *MVP Note*: The current iteration uses a static client-side key for AES encryption. A production release will implement PBKDF2 to derive a unique encryption key from a user-provided master password.

### 3. "Share the Void" Card Generation
To allow users to share their commitment on social media without compromising privacy, Chronos features a client-side image generator.
- **html2canvas**: When a user clicks "Share the Void", the app renders a hidden DOM element containing the "tombstone" design (using the *Spectral* typeface).
- **Canvas Export**: `html2canvas` traverses this DOM node, paints it to an HTML5 `<canvas>` at 3x scale for high-resolution retina displays, and exports it as an `image/png` Data URI, triggering a native browser download.

### 4. Tech Stack
- **Frontend Framework**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS
- **Typography**: Cormorant Garamond (Serif), Spectral (Serif), Inter (Sans), JetBrains Mono (Mono)
- **Cryptography**: `crypto-js`
- **Backend (Payments Only)**: Express.js server utilizing the `stripe` Node SDK to generate secure Checkout Sessions for the Premium tier.

---

## 🚀 Getting Started

### Prerequisites

- Node.js (v18+)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## ⚖️ License

Distributed under the **MIT License**. See the footer of the application for more details. This project is open for anyone to use, modify, and chronicle their own journeys.

---

*Curated with continuity in mind.*
