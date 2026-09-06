# Artwork, recycling, and connected animations

This reference applies when grids stutter, artwork changes during navigation, or memory work causes image flashes. Time layout, decoding, and network work, then measure retained objects. A cache change can help one while hurting another.

## Share the presented asset

Use one foreground-image policy for thumbnails and detail views. During a connected animation, source and destination should resolve to the same asset and decoded image. A low-resolution tile replaced by a different detail image mid-animation can break the visual handoff even when both requests finish successfully.

Set the shared decode bound from the largest foreground presentation. Preserve aspect ratio and do not upscale a smaller original. Large backdrops are a different use case. The shared policy need not retain every image at its original resolution.

Keep resource use bounded:

- Coalesce downloads and decodes for the same asset. A consumer that unloads stops waiting without canceling work still needed by another consumer.
- Bound decode/download concurrency and retain a small hot set with both an item limit and a decoded-byte budget. Weak overflow entries still need bounded indexing and cleanup. Visible controls own their images independently of the cache's retention budget.
- Include content revision and the relevant account/server scope in cache identity. Reject stale completions after a source, item, or session change.
- Keep decoded WinUI object creation and assignment on their owning dispatcher; move network and file work off it. Retain cancellation and generation checks through both stages.

## Unload is not necessarily eviction

A page can unload while its visual tree remains useful for back navigation or a connected animation. Clearing every image on unload causes a placeholder flash on return and can invalidate the outgoing animation surface. Deferring the clear to a low-priority callback introduces a second problem: the callback may touch XAML after shutdown has begun.

Give the cache, page, control, and request separate lifetimes. On ordinary unload, cancel that consumer's pending work and unsubscribe external events.
Retain an already loaded surface when the same control and source will return. On reload, avoid issuing another image request if the matching surface is still present. Clear or replace it when the item/source changes or the recycling contract actually releases the element.
Guard late completions against the current item and source identity.

Bounded retention avoids image flashes. Test navigation-cache ownership and repeated navigation under memory pressure before calling a leak fixed. A cache byte limit covers pinned cache entries, not references held by visible or cached pages. See [native boundaries](native-boundaries.md) for the shutdown callback failure mode.

## Virtualization and collection changes

Keep virtualization enabled and limit realization to the viewport and a justified buffer. Look for nested unbounded scrolling, full-list measurement, per-item subscriptions, repeated image decoding, and expensive template work before replacing a grid implementation. Recycled elements must detach from the previous item and reject its asynchronous completions.

Apply item-level collection changes when possible. Removing one item by replacing the entire source forces unnecessary realization and can flash the view. Remove the item from its existing observable collection, then derive the empty state from the resulting count. Use a batch or reset only when its cost and semantics fit the actual update.

Share card templates and state transitions where presentations should match. Independent near-duplicate image controls drift in padding, clipping, hover timing, and pressed states. Preserve keyboard, touch, selection, and accessibility behavior when consolidating them. A simpler template is a performance candidate until a trace shows the saving.

## Connected-animation handoff

Track each navigation pair by stable item identity. Prepare the source before navigation, realize the correct destination, and start once its layout and image surface are ready. Use bounded retries for delayed layout and cancel them when navigation changes, the element is recycled, or the page unloads.

Check that both elements belong to the expected visual root before transforming bounds. Test forward, back, and detail-to-detail routes separately. One route cannot stand in for the others. Off-screen or recycled targets need a deliberate fallback instead of an animation to the wrong item.

Size-responsive effects need current geometry. Derive circular clips and shadow masks from actual dimensions, and refresh them when the artwork changes size. For layout animations, capture the final arranged bounds and avoid leaving a transform that snaps back when layout catches up. Preserve easing and the system animation preference.

Keep visual and performance validation distinct. Test narrow and wide layouts, rapid navigation, filter/sort changes, and back navigation when interaction is permitted. Use the user's manual reproduction when it is not. Lower-end grid performance and retained-memory improvements require their own measurements.
