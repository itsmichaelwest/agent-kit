# UI fed by a helper process

Use this reference when a separate process supplies the UI's data. The same
dependency and latency questions apply to pipes, sockets, and other transports.

## Overlap independent startup

After establishing single-instance ownership, probe for the helper and start
it if needed. When safe, overlap its startup with XAML initialization. Measure
the probe, process creation, connection, and handshake separately.

A resident helper changes both launch cost and idle resource use. Report that
case separately from a cold launch and preserve the product's lifecycle.

## Request the first screen

Send independent requests once the connection is ready rather than serializing
them behind unrelated replies. Size the initial page for the visible content
and a justified buffer. Keep configuration and subscription prerequisites in
order.

Server-pushed initial state may remove round trips, but it changes the protocol.
Consider it only when that contract is in scope and all consumers are covered.

## Serializer cost

Use System.Text.Json source generation for known message types and inspect
remaining reflection paths. If first-use metadata work appears in the trace,
warm representative valid messages off the UI thread. A failed warm-up may
leave the original cost unchanged.

Check whether warm-up and the first real request contend on shared state before
introducing separate serializer instances. For dynamic property access, prefer
generated type metadata where suitable and declare any remaining reflection
requirements so trimming analysis can verify them.

## Pace event streams

Coalesce frequent progress events off the UI thread and post bounded batches.
Choose the interval from responsiveness requirements and measurements. Preserve
ordering, terminal events, and updates that cannot be merged. Deliver initial
content promptly rather than waiting for a batching interval.

When the producer's contract must remain unchanged, implement pacing in the
consumer. A low-priority reveal can allow already queued batches to apply before
the first frame; measure its effect on both reveal latency and layout work.

## Data-source latency

Inspect query plans and request handling when data arrives after the UI is ready.
Look for per-row lookups, repeated correlated work, expensive comparison
callbacks, and unnecessary lease or connection maintenance. Keep semantic parity
when changing queries or adding fast paths.

A control loop blocked on slow hardware or storage delays unrelated replies.
Move reads to an appropriate worker or maintain event-driven cached facts when
freshness permits. Cover every write, restore, and cleanup path with cache
invalidation. Trace request handling with the same discipline as UI startup.
