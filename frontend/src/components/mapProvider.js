import { leafletFallback } from './mapFallback';

export const mapKey = import.meta.env.VITE_TIANDITU_KEY || '';
let pending;

// Provider failures must never block the rest of the website from loading.
export function loadMapProvider() {
  if (!pending) pending = new Promise(resolve => {
    if (!mapKey) { resolve(leafletFallback()); return; }
    if (window.T) { resolve(window.T); return; }
    const script = document.createElement('script');
    let settled = false;
    const finish = provider => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve(provider);
    };
    const timer = setTimeout(() => finish(leafletFallback()), 2500);
    script.async = true;
    script.src = `https://api.tianditu.gov.cn/api?v=4.0&tk=${encodeURIComponent(mapKey)}`;
    script.onload = () => finish(window.T || leafletFallback());
    script.onerror = () => finish(leafletFallback());
    document.head.appendChild(script);
  });
  return pending;
}
