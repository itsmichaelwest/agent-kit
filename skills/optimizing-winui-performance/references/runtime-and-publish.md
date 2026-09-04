# Runtime and publish shape

## Where the first 100 ms go

On the reference app, the .NET host, runtime, and Windows App SDK bootstrap
spent 85 ms unpackaged and about 120 ms packaged before the App constructor.
Native AOT reduced that cost in its measured configuration; trace the target
app's pre-constructor cost before choosing a publish change.

## Knobs that moved the trace

- `PublishReadyToRun=true`, self-contained. Removes JIT stalls on the
  launch path. Measured 660 ms to rows against roughly 1000 ms for the JIT
  build in the IDE. Superseded by Native AOT once that works (below), which
  reached 560 ms and cut the package from 100 MB to 43 MB.
- Exclude the WinRT projection assemblies from ReadyToRun when
  self-contained, or the app crashes at startup with a `TypeLoad` around
  `ComInterfaceEntry` / `IDynamicInterfaceCastable`:

  ```xml
  <ItemGroup Condition="'$(_IsPublishing)' == 'true' and '$(SelfContained)' == 'true'">
    <PublishReadyToRunExclusions Include="WinRT.Runtime.dll" />
    <PublishReadyToRunExclusions Include="Microsoft.Windows.SDK.NET.dll" />
  </ItemGroup>
  ```

- `TieredPGO=false`. The launch path runs once, so instrumented tiers have
  nothing to repay. Re-measure before keeping it on any app.
- System.Text.Json source generation for every message type the app
  decodes at launch. Reflection metadata for a large union of types took a
  few hundred milliseconds to build on first use, on the UI thread. See
  `helper-process.md`.

## Trimming and Native AOT

In the reference app, enabling `PublishTrimmed` produced blank bindings and
empty lists despite a successful build and launch. Its WinRT
projection needs a generated vtable for each .NET type it hands to XAML,
and `{Binding}` needs a generated property provider; without them both fall
back to reflection the trimmer removed. Check the target app's warnings,
generated metadata, and runtime behavior before assigning the same cause.

Check Native AOT support and trimming requirements for the project's exact
toolchain. On the reference app, the following changes moved rows-rendered
from 660 ms to 560 ms unpackaged. Adapt them to the target's diagnostics:

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
4. `[RelayCommand]` on such a type produces `MVVMTK0046`: the bindable
   generator cannot see a property another generator emits. Declare those
   commands by hand (`_x ??= new RelayCommand(...)`).
5. Types in a WinUI-free library cannot take the attribute. Bind to them
   with `x:Bind` (with `Mode=OneWay`, since x:Bind defaults to OneTime) and
   convert image URIs through a function, because x:Bind does no
   string-to-ImageSource conversion.
6. `XamlCompiler warning WMC1510` lists every remaining `{Binding}`; it is
   informational once the sources carry the attribute.

Verify exposed content with UI Automation: a dump of the window's
element tree shows whether lists have items and text blocks have text
(see `measuring.md`). Check the wizard, every `{Binding}` window, and every
`DisplayMemberPath` combo box, not only the launch page. Inspect screenshots or
recordings separately for visual correctness; UI Automation does not prove it.

The native link needs the Visual Studio C++ tools. Visual Studio 18's
`vcvarsall.bat` looks up `vswhere.exe` by name, so the publish fails at the
linker unless the Visual Studio Installer directory is on `PATH` or the
shell is a Developer PowerShell. The failure message is a garbled linker
path containing "'vswhere.exe' is not recognized".

Visual Studio's Build, Deploy, and F5 never compile AOT; only the publish
pipeline does, so the dev package the IDE registers stays a JIT layout. The
packaging wizard (Package and Publish, Create App Packages) runs the publish
profile and produces the AOT MSIX; register its unpacked contents loosely to
run it (see `measuring.md`).

## Publish hygiene

- Publish into a fresh output directory so stale files cannot produce a mixed
  layout. If cleaning an existing generated directory, verify its resolved path
  and preserve user data or artifacts that are not disposable build output.
- Assets referenced from code (`SetIcon`, tray icons) must be
  `CopyToOutputDirectory`, or the unpackaged layout lacks them.
- Confirm the MSIX contains the intended publish output by comparing content
  hashes of the relevant binaries in the published and extracted layouts.
  File sizes are a diagnostic clue, not proof of artifact identity.

## A helper process built by MSBuild

When the csproj builds a helper executable with another toolchain (a native
compiler, a package manager, a script) as a target:

- Guard the target with `'$(DesignTimeBuild)' != 'true'`, or the IDE's
  design-time restore runs the build and reports the project as failing to
  load.
- Give the IDE's Release configuration a fast optimized profile of the
  helper (minutes) and reserve the fully optimized one (which can take ten
  minutes or more with whole-program optimization) for publish and package
  targets. Select by a property such as `ShipCore` that defaults to true
  when `_IsPublishing` or `GenerateAppxPackageOnBuild` is set.
- The build output folder must contain the helper exe or the app fails at
  its first connect; verify it in a target rather than at runtime.

## Packaged versus unpackaged

Package identity costs about 0.1 s inside the process (runtime start, probe
for the helper, child spawn are all slower) and 0.2 to 0.4 s of activation
before the process starts. Unpackaged distribution avoids both but loses the
identity that toast notifications and some shell integration need. Measure
both and let the user choose.
