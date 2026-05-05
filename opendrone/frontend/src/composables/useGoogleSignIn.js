// Carica lo script Google Identity Services una volta sola e ritorna una
// promise che si risolve quando `window.google.accounts.id` è disponibile.

const SCRIPT_SRC = 'https://accounts.google.com/gsi/client'
let loadPromise = null

export function loadGoogleScript() {
  if (typeof window === 'undefined') return Promise.reject(new Error('no window'))
  if (window.google?.accounts?.id) return Promise.resolve(window.google)
  if (loadPromise) return loadPromise

  loadPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${SCRIPT_SRC}"]`)
    if (existing) {
      existing.addEventListener('load', () => resolve(window.google))
      existing.addEventListener('error', () => reject(new Error('GSI load error')))
      return
    }
    const s = document.createElement('script')
    s.src = SCRIPT_SRC
    s.async = true
    s.defer = true
    s.onload = () => resolve(window.google)
    s.onerror = () => reject(new Error('GSI load error'))
    document.head.appendChild(s)
  })
  return loadPromise
}

export function getGoogleClientId() {
  return import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
}
