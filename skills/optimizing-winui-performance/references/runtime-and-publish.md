# Runtime and publish shape

## Measure runtime startup

Trace the interval before the App constructor as well as managed startup.
Runtime initialization, deployment mode, and framework bootstrap can contribute
to that interval. Compare publish configurations on the same workload and
hardware before choosing one for performance.

ReadyToRun can reduce JIT work. Native AOT changes compilation and interop
requirements and needs its own functional validation. Treat tiered compilation
and PGO as workload-dependent choices; a startup gain can trade against
steady-state behavior. Inspect first-use serializer metadata cost separately.

If a ReadyToRun build fails around WinRT projection types, inspect the exact
SDK targets and supported exclusions before changing publish properties. Keep
version-specific workarounds tied to a reproduced diagnostic rather than making
them defaults for every application.

## Trimming and Native AOT

A trimmed build can launch while losing runtime-bound content. Check generated
property providers and WinRT interface exposure for every type handed to XAML.
A successful compile does not establish that reflection-dependent paths survive.

Check support and requirements for the installed toolchain, then apply the
changes indicated by its diagnostics:

1. In the csproj: `PublishAot=true` under the publish condition,
   `AllowUnsafeBlocks=true` (the generated vtable code needs it),
   `CsWinRTAotWarningLevel=2`, and `IsAotCompatible=true` on class
   libraries. Drop ReadyToRun; AOT supersedes it.
2. Build and read the `CsWinRT1028` warnings. Each names a class that
   crosses the WinRT boundary and is not `partial`. Make it partial. Nothing
   else changes.
3. For every source of a classic `{Binding}` or `DisplayMemberPath`, add
   `[WinRT.GeneratedBindableCustomProperty]` to a partial part of the type.
   Put those parts in one file of their own when a test project
   link-compiles the view-model sources without a WinRT reference.
   `DependencyObject` sources whose bound members are dependency properties
   need nothing.
4. `[RelayCommand]` on a type with whole-type bindable metadata can produce
   `MVVMTK0046`: one generator cannot see a property another generator emits.
   Limit `GeneratedBindableCustomProperty` to the handwritten properties used
   by runtime bindings. If runtime binding needs the command itself, declare
   it by hand (`_x ??= new RelayCommand(...)`).
5. A library targeting the Windows SDK can use the CsWinRT attributes without
   referencing WinUI. Check its generator mode: `IsAotCompatible` alone does
   not expose every concrete collection returned through an interface.
   `x:Bind` avoids runtime property lookup but still crosses the native ABI
   when assigning `ItemsSource`. See [native boundaries](native-boundaries.md)
   for concrete collection exposure and an ABI regression probe. For image
   URIs, use an explicit conversion function when the binding needs one.
6. Check `WMC1510` runtime-binding warnings against the actual data contexts
   and generated property providers. An attribute alone does not prove that
   the full property path or its collection interfaces survive AOT.

When UI Automation is permitted, inspect the window's element tree to verify
that lists have items and text blocks have text
(see `measuring.md`). Check the wizard, every `{Binding}` window, and every
`DisplayMemberPath` combo box, not only the launch page. Inspect screenshots or
recordings separately for visual correctness; UI Automation does not prove it.
When app interaction is excluded, use generated-code inspection and a native
ABI probe, then request manual reproduction on the matched package.

Native linking requires the matching C++ toolchain and SDK. Diagnose missing
compiler or linker discovery from the invoked tool paths and environment. Use
the supported developer shell when the build relies on its setup.

Build, deploy, and publish targets can produce different layouts. Inspect the
actual targets and profile instead of inferring Native AOT from a configuration
name. Validate the output of the native publish and packaging pipeline.

## Publish hygiene

- Publish into a fresh output directory so stale files cannot produce a mixed
  layout. If cleaning an existing generated directory, verify its resolved path
  and preserve user data or artifacts that are not disposable build output.
- Assets referenced from code (`SetIcon`, tray icons) must be
  `CopyToOutputDirectory`, or the unpackaged layout lacks them.
- Confirm the MSIX contains the intended publish output by comparing content
  hashes of the relevant binaries in the published and extracted layouts.
  File sizes are a diagnostic clue, not proof of artifact identity.

### Resource and native dependency layout

Treat executable code, XBF, PRI, and native dependencies as one build output.
A successful native link or MSIX creation does not establish a usable layout.

- Stage compiled XBF and library assets at the paths encoded by the resource
  index. A PRI pointing to a build-tree prefix such as `AppX/Library/Assets`
  can package successfully while the files live elsewhere. Inspect a PRI dump
  and validate every file-backed candidate against the final package root.
- Rebuild or stage resource indexes for the intended final layout. Preserve
  dependency resource registration required by the chosen self-contained
  Windows App SDK deployment; copying only the application PRI is insufficient.
  Missing embedded WinUI themes can fail at startup with a missing
  `ms-appx:///Microsoft.UI.Xaml/Themes/themeresources.xaml` resource even when
  loose XBF files are present. Merge the UI dependency PRI content and check
  the embedded candidates as well as file-backed entries.
- Include the runtime's native resource libraries, renderer DLLs, and their
  architecture-matched dependencies. Inspect PE machine types using the
  toolchain's supported ARM64/ARM64X rules, rather than rejecting legitimate
  hybrid binaries or accepting an arbitrary mixed layout.
- Verify the manifest's executable, identity, resource paths, and architecture
  against extracted contents. Hash the intended publish payload and packaged
  payload, then confirm which registered executable the launch actually uses.

Keep compiler success, package layout validation, activation, rendered content,
playback, and clean exit as separate results. Run only the checks permitted by
the task; name any remaining manual check.

## A helper process built by MSBuild

When the csproj builds a helper executable with another toolchain (a native
compiler, a package manager, a script) as a target:

- Guard the target with `'$(DesignTimeBuild)' != 'true'`, or the IDE's
  design-time restore runs the build and reports the project as failing to
  load.
- Separate interactive build and distribution optimization settings when the
  helper's full optimization cost is unsuitable for normal development. Select
  the profile explicitly from the build contract.
- The build output folder must contain the helper exe or the app fails at
  its first connect; verify it in a target rather than at runtime.

## Packaged versus unpackaged

Package identity and activation can change measured startup costs. Compare
matching profiles and separate activation from in-process work. Preserve any
identity-dependent features when evaluating deployment alternatives.
