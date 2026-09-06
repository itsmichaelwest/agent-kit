# Native boundaries and teardown

This reference covers AOT failures during binding, renderer creation, and shutdown. Find the exact boundary before changing metadata or lifetime rules. Compilation and launch exercise only a small part of the native path.

## Collections assigned to ItemsSource

A compiled binding can fail inside `ItemsRepeater.set_ItemsSource` with `ArgumentException` (`0x80070057`) even though the managed property is a valid `IReadOnlyList<T>`. Inspect both the property's declared type and the actual objects it returns on initial load, hydration, and reset.

An empty collection expression assigned to `IReadOnlyList<T>` can become an array. A populated value produced by `ToList()` has a different concrete type. Marshalling and interface exposure are separate steps. Test the interfaces required by the control for empty, populated, and reset values; otherwise a populated-data test can miss an initial-load failure.

Use an explicit concrete type for collections directly handed to native item controls, and preserve it across those states:

```csharp
public IReadOnlyList<Item> Items { get; private set; }
    = new List<Item>();

// Populate
Items = incoming.Select(MapItem).ToList();

// Reset
Items = new List<Item>();
```

Expose the actual types using the CsWinRT generator when the owning library uses `OptIn` mode or automatic discovery misses them:

```csharp
[assembly: WinRT.GeneratedWinRTExposedExternalType(
    typeof(List<Item>))]
```

Check the installed generator's mode and emitted lookup. `IsAotCompatible=true` enables analysis; it does not by itself expose every collection produced by a library. `GeneratedBindableCustomProperty` addresses runtime property lookup, which is separate from collection interface exposure. The Windows SDK projection can provide these attributes to a library without a WinUI reference. See the [CsWinRT AOT guide](https://github.com/microsoft/CsWinRT/blob/master/docs/aot-trimming.md) for the installed version's supported patterns and collection-expression limits.

Limit the correction to the native boundary. Managed-only arrays do not need a blanket conversion, and listing every possible array and generic type in a metadata file still does not expose the interface a control requires.

### Verify the ABI without opening the app

When GUI interaction is excluded but native helper execution is allowed, a small console probe can test the boundary:

1. Reference copies of the actual model assembly and its matched dependencies. Use separate baseline and fixed output directories. Disable the probe's CsWinRT optimizer so it cannot supply metadata missing from the library.
2. Publish the probe for the same native architecture and runtime as the app. Verify the native compiler response file resolves the intended assembly. SDK reference candidate searches can select a sibling baseline DLL ahead of a changed hint path; isolate the directories or give hint paths priority.
3. Construct synthetic initial, populated, and reset entities. Pass each bound collection as `object` through `MarshalInspectable<object>.FromManaged`.
4. Query the native interfaces the control consumes. For bindable collections, test `IBindableVector` and `IBindableIterable` independently. Marshal success alone is insufficient, and one unsupported interface does not rule out another supported collection shape.
5. Enumerate through the native interface or read its count, compare with the expected synthetic values, and release every returned COM reference.

Require the expected interfaces and values in every tested state. Confirm the affected UI separately on the matching package, manually when required.

## Classic COM inside an otherwise native renderer

Inspect the exact dependency implementation before concluding that a native renderer host supports AOT. A wrapper can still call built-in COM conversion such as `Marshal.GetIUnknownForObject`, or construct interface wrappers through reflection. Trimming roots cannot repair an unsupported runtime API.

Prefer a supported dependency update or extension point. If a local host is necessary and within scope, preserve its swap-chain configuration, size metadata, DPI scaling, fallback behavior, and license attribution. Acquire WinUI objects through the supported projection, query the required native interface, and balance each COM reference.

Check generic wrapper factories and their reachable callers. Explicit native wrapper constructors can avoid reflection where the interface type is known. A warning from a rooted metadata provider may refer to an unused original control; establish reachability before expanding a replacement. Avoid turning a bounded interop repair into an unplanned renderer fork.

Await the renderer's stop operation before releasing its device and swap chain. Immediate disposal in `Unloaded` can race asynchronous stop. Give the owner an explicit release operation, prevent recreation after release, and retain native cleanup when XAML detachment must be skipped during application teardown.

## Shutdown keeps its dispatcher contract

Trace shutdown as carefully as startup. Service disposal can raise property notifications or call WinRT objects, even if the method name sounds like storage cleanup. Keep those operations and their awaited continuations on the UI dispatcher. Move only documented non-UI flush work to the thread pool.

For asynchronous close, distinguish shutdown started from shutdown complete. Handle repeated close requests while cleanup awaits; allow the intentional final close only after completion. Preserve event unsubscription and stop order.

Low-priority callbacks queued by `Unloaded` can run after XAML teardown begins. Check whether deferred visual writes are needed at all; ordinary unload may retain an image for navigation. When a teardown guard is needed, set a static managed lifecycle flag before the first shutdown await and read it before any `IsLoaded`, dependency-property, or `Application.Current` access. Continue cancellation and nonvisual resource release. Catching and ignoring wrong-thread exceptions leaves the lifecycle bug in place.

When execution is allowed, verify normal close with the exact native package: retain a process handle, observe its exit code, and correlate recent fatal events. A vanished window says nothing about the exit code. When execution is excluded, report the source review and leave the native exit check pending.
