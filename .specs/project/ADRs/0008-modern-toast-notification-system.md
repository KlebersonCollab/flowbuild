# ADR 0008: Modern Toast Notification System (Replacing Browser Alerts)

## Status
Accepted

## Context
1. **The Problem**: Previously, workflow validation blocks (such as missing trigger nodes) and format errors triggered native browser `alert()` popups.
2. **UX Friction**: Browser native `alert()` is modal and blocking, halts JavaScript execution, interferes with browser automation, and visually clashes with the Linear Dark design system tokens specified in `DESIGN.md`.
3. **User Intent**: The user explicitly instructed: *"O workflow precisa de pelo menos um nó Trigger inicial... entendo que não deveriamos mais trabalhar com alert e sim outra forma moderna de lidar com avisos e erros"*.
4. **Standard Solution**: A reactive, non-blocking toast notification system with automatic dismissal, clear semantic states (`warn`, `error`, `success`, `info`), and consistent typography and dark tokens.

## Decision
1. **Reactive Toast Store (`toastStore.ts`)**:
   - Provide a global Pinia store exposing convenient notification dispatchers:
     - `toast.warn(message, title?)`
     - `toast.error(message, title?)`
     - `toast.success(message, title?)`
     - `toast.info(message, title?)`
   - Implement automatic expiration (default 4.5s) with unique ID generation and manual dismissal capability.
2. **Visual Toast Component (`ToastContainer.vue`)**:
   - Mount globally in `App.vue` positioned in the bottom-right corner (`fixed bottom-5 right-5 z-50`).
   - Adhere strictly to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) dark palette (`#0e0f12` background, `#23252a` hairline borders, Linear typography, and semantic accent accents: emerald for success, rose for error, amber for warning, lavender `#5e6ad2` for info).
   - Use Vue `<TransitionGroup>` for smooth entrance and exit animations without layout shifts.
3. **Deprecation of Browser `alert()`**:
   - Completely replace all instances of native browser `alert()` in `TopNav.vue` and across the application with `toastStore` calls.

## Consequences
- **Positive**: Smooth, modern, and non-blocking UX matching top-tier developer platforms (Linear, Vercel, Supabase).
- **Positive**: Seamless visual alignment with the application's dark aesthetic without OS-native modal popups.
- **Positive**: Zero blocking during tests or user interactions.
- **Neutral**: Requires `ToastContainer.vue` mounted at root layout (`App.vue`).
