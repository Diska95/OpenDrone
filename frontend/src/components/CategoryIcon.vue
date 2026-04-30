<template>
  <svg viewBox="0 0 80 80" fill="none">
    <!-- Agricoltura: pianta -->
    <template v-if="category === 'agricoltura'">
      <path d="M40 60 V30" stroke="#5dff9f" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M40 30 C 30 25, 22 28, 18 38" stroke="#5dff9f" stroke-width="1.5" fill="none"/>
      <path d="M40 36 C 50 30, 58 33, 62 43" stroke="#5dff9f" stroke-width="1.5" fill="none"/>
      <ellipse cx="40" cy="65" rx="20" ry="3" stroke="#ff9060" stroke-width="1.2"/>
    </template>
    <!-- Ispezione: lente -->
    <template v-else-if="category === 'ispezione'">
      <circle cx="34" cy="34" r="18" stroke="#5dff9f" stroke-width="1.5"/>
      <line x1="48" y1="48" x2="64" y2="64" stroke="#5dff9f" stroke-width="2" stroke-linecap="round"/>
      <circle cx="34" cy="34" r="8" stroke="#ff9060" stroke-width="1.2"/>
    </template>
    <!-- Fotografia: camera -->
    <template v-else-if="category === 'fotografia'">
      <rect x="15" y="25" width="50" height="35" rx="6" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="40" cy="42" r="10" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="40" cy="42" r="5" stroke="#ff9060" stroke-width="1.5"/>
      <rect x="32" y="18" width="16" height="8" rx="3" stroke="#5dff9f" stroke-width="1.2"/>
    </template>
    <!-- Ricerca: atomo -->
    <template v-else-if="category === 'ricerca'">
      <ellipse cx="40" cy="40" rx="26" ry="10" stroke="#5dff9f" stroke-width="1.5"/>
      <ellipse cx="40" cy="40" rx="26" ry="10" stroke="#5dff9f" stroke-width="1.5" transform="rotate(60 40 40)"/>
      <ellipse cx="40" cy="40" rx="26" ry="10" stroke="#5dff9f" stroke-width="1.5" transform="rotate(-60 40 40)"/>
      <circle cx="40" cy="40" r="4" fill="#ff9060"/>
    </template>
    <!-- Racing: bandiera scacchi -->
    <template v-else-if="category === 'racing'">
      <rect x="20" y="20" width="40" height="40" stroke="#5dff9f" stroke-width="1.5"/>
      <rect x="20" y="20" width="10" height="10" fill="#5dff9f"/>
      <rect x="40" y="20" width="10" height="10" fill="#5dff9f"/>
      <rect x="30" y="30" width="10" height="10" fill="#5dff9f"/>
      <rect x="50" y="30" width="10" height="10" fill="#5dff9f"/>
      <rect x="20" y="40" width="10" height="10" fill="#5dff9f"/>
      <rect x="40" y="40" width="10" height="10" fill="#5dff9f"/>
      <rect x="30" y="50" width="10" height="10" fill="#5dff9f"/>
      <rect x="50" y="50" width="10" height="10" fill="#5dff9f"/>
    </template>
    <!-- Sicurezza: scudo -->
    <template v-else-if="category === 'sicurezza'">
      <path d="M40 14 L62 24 V42 C62 54, 52 62, 40 66 C28 62, 18 54, 18 42 V24 Z"
            stroke="#5dff9f" stroke-width="1.5" fill="none"/>
      <path d="M32 40 L38 46 L50 34" stroke="#ff9060" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </template>
    <!-- Educazione: tocco accademico -->
    <template v-else-if="category === 'educazione'">
      <path d="M14 30 L40 20 L66 30 L40 40 Z" stroke="#5dff9f" stroke-width="1.5" fill="none"/>
      <path d="M22 34 V50 C22 54, 30 58, 40 58 C50 58, 58 54, 58 50 V34" stroke="#5dff9f" stroke-width="1.5" fill="none"/>
      <line x1="62" y1="32" x2="62" y2="48" stroke="#ff9060" stroke-width="1.5"/>
    </template>
    <!-- Industria: ingranaggio -->
    <template v-else-if="category === 'industria'">
      <circle cx="40" cy="40" r="14" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="40" cy="40" r="6" stroke="#ff9060" stroke-width="1.2"/>
      <g stroke="#5dff9f" stroke-width="1.5" stroke-linecap="round">
        <line x1="40" y1="20" x2="40" y2="26"/>
        <line x1="40" y1="54" x2="40" y2="60"/>
        <line x1="20" y1="40" x2="26" y2="40"/>
        <line x1="54" y1="40" x2="60" y2="40"/>
        <line x1="26" y1="26" x2="30" y2="30"/>
        <line x1="50" y1="50" x2="54" y2="54"/>
        <line x1="54" y1="26" x2="50" y2="30"/>
        <line x1="26" y1="54" x2="30" y2="50"/>
      </g>
    </template>
    <!-- Default: drone -->
    <template v-else>
      <rect x="30" y="30" width="20" height="20" rx="4" stroke="#5dff9f" stroke-width="1.5"/>
      <line x1="40" y1="30" x2="40" y2="10" stroke="#5dff9f" stroke-width="1.5"/>
      <line x1="40" y1="50" x2="40" y2="70" stroke="#5dff9f" stroke-width="1.5"/>
      <line x1="30" y1="40" x2="10" y2="40" stroke="#5dff9f" stroke-width="1.5"/>
      <line x1="50" y1="40" x2="70" y2="40" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="40" cy="10" r="5" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="40" cy="70" r="5" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="10" cy="40" r="5" stroke="#5dff9f" stroke-width="1.5"/>
      <circle cx="70" cy="40" r="5" stroke="#5dff9f" stroke-width="1.5"/>
    </template>
  </svg>
</template>

<script setup>
defineProps({
  category: { type: String, default: '' }
})
</script>

<style scoped>
svg { width: 100%; height: 100%; }
</style>
