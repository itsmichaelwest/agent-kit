# UI fed by a helper process

This reference covers UIs whose data comes from another process. Pipes, sockets, and other transports have the same dependency and latency questions.

## Overlap independent startup

Once single-instance ownership is settled, probe for the helper and start it if needed. Its startup can overlap XAML initialization when the dependencies allow it. Time the probe, process creation, connection, and handshake individually.

A resident helper changes launch work and consumes resources while idle. Measure it as a separate case without changing the intended process lifecycle.

## Request the first screen

Once connected, send independent requests together instead of placing each behind an unrelated reply. The initial page should cover the visible content plus a measured buffer. Configuration and subscription prerequisites still run in their required order.

Pushing initial state from the server removes round trips but changes the protocol. Do it only when that contract and every consumer are in scope.

## Serializer cost

For known message types, use `System.Text.Json` source generation and find any reflection paths left behind. If first-use metadata appears in the trace, warm representative valid messages away from the UI thread. Confirm that warm-up actually removes the cost.

Before adding serializer instances, check whether warm-up contends with the first real request on shared state. Generated type metadata suits many dynamic property accesses. Declare the reflection that remains so trimming analysis can check it.

## Pace event streams

Coalesce frequent progress events away from the UI thread, then post bounded batches. Set the interval from the response budget and measurements. Ordering, terminal events, and non-mergeable updates must survive batching. Initial content should not wait for the first batch interval.

If the producer's contract cannot change, pace events in the consumer. A low-priority reveal may let queued batches land before the first frame. Measure both the reveal delay and the layout work.

## Data-source latency

Inspect query plans and request handling when data arrives after the UI is ready. Look for per-row lookups, repeated correlated work, expensive comparison callbacks, and unnecessary lease or connection maintenance. Keep semantic parity when changing queries or adding fast paths.

A control loop blocked on slow hardware or storage delays unrelated replies. Move reads to an appropriate worker or maintain event-driven cached facts when freshness permits. Cover every write, restore, and cleanup path with cache invalidation. Trace request handling with the same discipline as UI startup.
