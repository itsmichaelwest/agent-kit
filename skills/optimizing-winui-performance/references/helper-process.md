# UI fed by a helper process

Applies to any WinUI app whose data lives in another process: a daemon, a
background service, a worker, a language server. "Connection" below means
whatever carries the messages (named pipe, socket, shared memory). What
follows is about ordering and cost and holds for any transport.

## Start the helper first

In the App constructor, before `InitializeComponent`: check the single
instance key, probe for a running helper, start one if absent. The helper's
own start (about 130 ms for a 21 MB native exe opening a database) then
overlaps the app's XAML initialization instead of following it.

A probe such as `File.Exists` on a named pipe path costs 13 ms unpackaged
and about 45 ms packaged. A helper left resident would make the probe
positive and remove the spawn and the helper's boot from the path, roughly
170 ms. For a true cold-launch target, keeping it resident does not meet the
measurement contract and uses memory while the app is not in use. An
app already running in the tray opens its window almost instantly, which is
the resident case, and the user chooses it.

## The launch burst

Send every request the first screen needs in one go as soon as the
connection is open: summary, inventory, navigation lists, configuration,
subscriptions. Do not wait for one reply before sending the next. Size the
first page requests for the first screen (100 items, not the maximum page),
because the helper's page cost is proportional to the rows requested and the
first tiles answer sooner.

Ask whether the helper can push what every client needs at connect
(configuration, inventory) rather than waiting to be asked. That is a
protocol change, so it needs every client updated; note it as an option
rather than doing it inside a performance pass.

## Serializer cost

- With System.Text.Json, use a `JsonSerializerContext` with
  `[JsonSerializable]` for every message type. Reflection metadata for a
  large union took hundreds of milliseconds to build on first use.
- Warm the codec on the thread pool from the App constructor: serialize and
  deserialize one representative request and one event. Use values that
  pass validation, since a rejected warm-up throws silently and warms
  nothing.
- Give the handshake its own context instance. The first reply and the
  warm-up otherwise contend on one context's lock and the handshake waits.
- Reading one property by wire name out of an arbitrary message: use the
  context's `GetTypeInfo(type).Properties` rather than reflection, and mark
  the accessor with `DynamicallyAccessedMembers` so trimming analysis stays
  quiet.
- Enum converters that read attributes via `GetField` need the same
  annotation.

## Pacing the event stream

Replies are applied immediately. Progress streams (scan, sync, conversion,
indexing) are paced: a pump collects events off the UI thread, flushes at an
interval (100 ms), and posts one batch to the dispatcher. Decide per event
type with a predicate such as `IsPaced(event)`. The first rows must not wait
out the interval: flush at once when nothing is pending.

Fix consumer-side pacing when the producer's event contract must remain
unchanged. Changing that contract affects other consumers and needs its own
scope and validation; it is not a substitute for diagnosing the stuttering UI.

## Deliver batches before the first frame

Post the window reveal at `DispatcherQueuePriority.Low`. Batches already
queued at normal priority then apply before the first frame, so the frame
carries data instead of being followed by a second layout pass.

## Page queries

Whichever process answers a page request, the same shapes cost the same:

- A per-row lookup against a second table makes a page of 100 rows cost 100
  queries. Fold it into the page query as a LEFT JOIN and carry the extra
  column on the row.
- In SQLite, a CTE consulted from a correlated `EXISTS` is re-run per row.
  `WITH x AS MATERIALIZED (...)` fixed one page from 300 ms to 16 ms.
- Collation callbacks written in the host language get called per
  comparison. An ASCII fast path in the comparer, with a parity test against
  the full path, was worth keeping.
- Long-lived read leases should be refreshed at half-life, not on every
  request; renewing on every page was itself a measurable cost.

## Reads that block the helper's loop

A helper whose control loop reads slow hardware or storage while answering
a request holds every other reply behind that read. Move the facts to the
event that produced them (a mount, a device arrival), cache them, and let
the request path use cached facts and read-only services. Invalidate the
cache on every internal path that writes to the source, including restore
and cleanup paths that are easy to forget.

After the app's own launch path is tuned, the helper's reply latency is
usually what gates the first screen: on the reference app the requests left
at about 90 ms and the navigation replies landed around 300 ms later. Trace
the helper's request handling with the same discipline as the UI.
