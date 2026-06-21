/**
 * ==============================================================================
 * main.tsx - Entry Point React
 * ==============================================================================
 * Titik awal (entry point) tempat aplikasi React di-render (ditempelkan) ke 
 * dalam elemen HTML DOM browser. Menginisialisasi CSS Tailwind dan App utama.
 * ==============================================================================
 */
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./styles/index.css";

// Unregister any legacy PWA service workers and clear caches
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    for (const registration of registrations) {
      registration.unregister();
    }
  });
}
if ("caches" in window) {
  caches.keys().then((keys) => {
    for (const key of keys) {
      caches.delete(key);
    }
  });
}

createRoot(document.getElementById("root")!).render(<App />);
