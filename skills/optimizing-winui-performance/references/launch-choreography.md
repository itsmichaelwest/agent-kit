# Launch choreography

The startup contract determines which work can overlap. Account for session initialization, storage migrations, and first-run decisions before moving work to another thread or showing the window earlier.

## Safe prewarm

Only prewarm services whose constructors and dependencies can run on the thread pool. Singleton resolution may block the UI while another thread constructs the instance, so its constructor cannot wait for a UI callback. Finish storage migration or fresh-install detection before reading credentials.

Dispatcher-capturing services and XAML objects stay on the UI thread. Expensive optional engines stay lazy until needed, and resolving a facade should not construct them. Start optional integrations after the first frame, but retain an on-demand path for earlier use. If warm-up fails, normal initialization must still work. It should not repeat the same disk read on every call.

## Order work by dependency

1. Record process-relative trace marks and establish single-instance ownership.
2. Start independent background work after its prerequisites are satisfied.
3. Initialize XAML and connect to the data source. Apply incoming data through the UI dispatcher without blocking it on synchronous waits.
4. Resolve the first-run or session decision before exposing the relevant UI. Speculative window construction is useful only if it can be discarded safely.
5. Build the window and the state needed for its initial navigation surface.
6. Reveal it according to the product's contract. Give required remote data a bounded wait and an explicit loading or error state.
7. Defer optional work until the relevant rendered-content mark, with a fallback for empty or failed content loads.

A low-priority reveal may let queued data batches apply before the first frame. Measure whether it saves layout work or simply postpones the window. First content cannot depend on an unbounded background operation.

## Placement and reveal

Separate window construction from activation. Apply saved placement after construction and event registration, just before activation. Native placement APIs can show the window themselves; calling them during construction can expose an incomplete surface. Let the framework arrange the restored size before reconciling responsive controls.

Trace placement, size, and display-mode events when navigation starts in an inconsistent state. Avoid competing assignments to adaptive control properties until the event sequence identifies the conflict.

Keep the root visible by default. A reveal animation that fails must not leave an invisible window. Make completion idempotent and provide a visible fallback. Subscribe to the frame marker before activation, then detach it when the measurement completes. Record first frame and useful content separately.

## Match the product's launch contract

If other supported clients establish when navigation appears and where loading states belong, preserve that behavior unless a change is requested. Evaluate cold startup, warm startup, and revealing a resident process separately.
