### react-native reliability

- Wrap the navigation root in an error boundary; a crashing screen must degrade
  to a recovery view, never a white screen.
- Every data-fetching screen handles three states explicitly: loading, error
  (with retry), and empty.
- Treat the network as absent by default: queue or fail writes gracefully when
  offline, and test that path.
- Wire crash reporting before the first store release; an unreported crash on a
  user's device is invisible debt.
