# Feature Plan: Modern Toast Notification System

## Problem Statement
The application previously relied on blocking, OS-native browser `alert()` dialogs when execution preconditions failed (e.g., missing trigger nodes) or when JSON import failed. This interrupts user focus and violates modern UI guidelines defined in `DESIGN.md`.

## Goals
1. Implement a reactive global `toastStore` supporting `warn`, `error`, `success`, and `info` toasts.
2. Build a high-polish, dark-themed `ToastContainer.vue` using Linear design system tokens.
3. Automatically dismiss toasts after a calibrated duration (4.5s) while allowing instant manual dismissal.
4. Replace all occurrences of native browser `alert()` with the new toast system.
5. Mount `ToastContainer.vue` at the root layout in `App.vue`.
6. Add unit tests verifying toast dispatch, auto-dismissal, and error/warn integration.

## Non-Goals
- Persistent database-backed notification center (toasts are ephemeral in-memory notifications).

## Proposed Architecture
- `frontend/src/stores/toastStore.ts`: Global reactive notification store.
- `frontend/src/components/ToastContainer.vue`: Global toast viewport with smooth transition animations.
- `frontend/src/App.vue`: Mount `<ToastContainer />`.
- `frontend/src/components/TopNav.vue`: Replace `alert(...)` with `toast.warn(...)` and `toast.error(...)`.
