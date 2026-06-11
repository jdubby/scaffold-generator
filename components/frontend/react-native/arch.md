### react-native (frontend)

React Native owns the user-facing layer: screens, navigation, and client-side
state. Keep screens thin — data fetching and business rules live in hooks and
services, so screens stay testable without a device. Isolate platform-specific
code (iOS/Android) behind small adapters rather than branching inside screens.
