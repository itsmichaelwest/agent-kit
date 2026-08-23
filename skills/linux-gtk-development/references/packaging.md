# Packaging and release

Use this reference for application identity, installed layout, desktop integration, AppStream, icons, Flatpak, self-hosted repositories, release bundles, native packages, sandbox permissions, release checks, and Flathub eligibility.

## Keep one application identity

Resolve one reverse-DNS application ID and keep it consistent across:

- `gtk4::Application` and D-Bus activation;
- desktop filename and desktop entry ID;
- AppStream component ID and launchable desktop ID;
- icon filename and icon lookup name;
- GSettings schema ID and path;
- GResource prefix;
- D-Bus service and object paths where applicable;
- Flatpak application ID;
- notification and action targets.

Changing the ID affects user settings, desktop favorites, permissions, D-Bus activation, package ownership, and update continuity. Treat it as a migration.

## Installed layout

Install through the build system. A complete GTK desktop application can include:

- executable under the target binary directory;
- desktop entry under `share/applications`;
- AppStream metadata under `share/metainfo`;
- icons in the hicolor hierarchy and symbolic icons in the appropriate theme path;
- GSettings schemas under `share/glib-2.0/schemas`;
- GResource bundles when not linked into the executable;
- translations under `share/locale`;
- D-Bus service files when activation is part of the contract;
- systemd user units only for a declared service;
- licenses and required documentation.

Test the staged or installed tree. Source-tree execution can hide missing install rules and resource paths.

## Desktop entry

The desktop file controls launch, search, MIME and URI handling, categories, actions, and desktop presentation.

- Keep `Type`, `Name`, `Exec`, `Icon`, `Categories`, and `Terminal` correct.
- Use field codes only when the application handles the matching files or URIs.
- Match `DBusActivatable` to a working D-Bus activation setup.
- Declare MIME types only with tested open behavior and matching shared MIME information where required.
- Add desktop actions only for stable commands that work through application actions.
- Validate the installed desktop file with `desktop-file-validate`.

Do not add `StartupWMClass` by habit. Use it only for a tested desktop matching problem and understand its Wayland behavior.

## Icons

Provide a scalable application icon and any raster sizes required by the target package or store. Follow GNOME app-icon guidance for a GNOME-facing application.

- Keep the icon name equal to the application ID when required by the package contract.
- Install symbolic interface icons as resources when the system theme does not provide them.
- Do not recolor symbolic icons manually when GTK can apply semantic color.
- Check the icon in the app grid, window switcher, notifications, light and dark shell contexts, and store metadata.
- Validate that Flatpak exports the icon under the application ID.

## AppStream metadata

AppStream describes the application to software centers and package repositories.

Include the fields required by the current policy, such as:

- component and launchable IDs;
- name, summary, and user-facing description;
- metadata and project licenses with valid SPDX expressions;
- developer identity;
- homepage, bug tracker, donation, help, and source URLs where applicable;
- release entries with versions, dates, and useful notes;
- screenshots that follow current quality rules;
- branding colors and content rating where required;
- provided MIME types and hardware requirements when applicable.

Validate with `appstreamcli validate` and the package store's linter. Check localized installed metadata.

## Flatpak manifest

For GNOME-facing cross-distribution delivery, Flatpak is usually the primary package. Use the current supported GNOME runtime and SDK that meet the application's GTK and libadwaita floor.

A reproducible manifest:

- pins upstream archives or commits with checksums or immutable revisions;
- uses the committed `Cargo.lock`;
- declares every crate source for an offline build;
- keeps the main application module late enough for useful builder caching;
- installs files under `/app` through the normal build system;
- removes development files that the runtime package does not need;
- exports desktop, AppStream, icon, service, and search-provider metadata under the application ID;
- builds for each supported architecture or states an architecture restriction with evidence.

Generate Cargo sources with the current `flatpak-builder-tools` workflow. Run a clean build with network access unavailable during the build phase.

## Sandbox permissions

Start from no extra permission and add the narrowest capability that tested behavior requires.

- Prefer Wayland, with X11 fallback only when the supported desktop contract needs it.
- Add GPU, audio, network, device, or filesystem access only for actual application behavior.
- Prefer portals to broad home-directory access.
- Use specific D-Bus names. Avoid broad session or system bus access.
- Document unusual filesystem or device access in product and store metadata.
- Re-test file selection, drag and drop, URI opening, notifications, secrets, subprocesses, hardware acceleration, and external devices inside the sandbox.

Flatpak permission review is part of feature design. A feature that requires broad host access may need a different interface.

## Flathub eligibility

Check the current [Flathub requirements](https://docs.flathub.org/docs/for-app-authors/requirements) before doing any Flathub work. Its current generative AI policy rejects applications containing AI-generated or AI-assisted code, documentation, or other content. It also prohibits AI tools from generating, opening, automating, reviewing, or writing material for a submission pull request.

An agent may create and validate a repository-neutral Flatpak manifest, AppStream metadata, desktop file, build scripts, and release artifacts for a non-Flathub distribution target. State the target clearly and do not call these artifacts Flathub-ready. If the user later considers Flathub, explain that submitting the same AI-assisted files would still conflict with the current policy. Having a human upload or open the pull request does not change how those files were produced.

If the application or submission contains AI-assisted work, stop before preparing Flathub-specific files or activity. Do not draft the submission pull request, review replies, or an exception request. A developer who wants to pursue Flathub must independently assess eligibility and author the submission material without AI assistance. Flathub states that it may grant exceptions to mature, well-maintained projects, but the developer must also pursue that process without AI assistance.

This restriction applies to Flathub, not to the Flatpak format. The agent may still build and validate a Flatpak for direct distribution, another repository, or local installation when the user requests it.

## Flatpak distribution outside Flathub

Flatpak supports self-hosted repositories and single-file bundles. Choose based on whether automatic updates matter.

### Static repository

Host the repository produced by `flatpak-builder --repo=repo` on an HTTP server. Flatpak's documentation explicitly supports GitHub Pages and GitLab Pages for this use.

A maintained repository should include:

- GPG-signed commits and summary metadata;
- static deltas generated with `flatpak build-update-repo --generate-static-deltas`;
- a `.flatpakrepo` file that describes the remote and embeds its public GPG key;
- a `.flatpakref` file for each application so users can add the remote and install the app in one operation;
- AppStream metadata, icons, and screenshots for software-center presentation;
- enough HTTP storage, bandwidth, and request capacity for repository objects and updates.

GitHub Actions can build the repository and deploy its static files to GitHub Pages. Keep signing keys in protected CI secrets, restrict deployment permissions, pin third-party actions, and prevent pull requests from accessing release credentials. Users install from the published `.flatpakref`, and later repository commits arrive through `flatpak update`.

GitHub Pages is static hosting, not an application store. The developer owns signing, availability, update policy, security response, metadata quality, and user documentation.

### GitHub Release bundle

Create a single `.flatpak` file from a built repository:

```bash
flatpak build-bundle --gpg-sign=KEY_ID repo com.example.App.flatpak com.example.App stable
```

Attach the bundle to a GitHub Release or another download page. Users can install it with:

```bash
flatpak install --user com.example.App.flatpak
```

Publish the signing key and checksums with the bundle. A bundle can name a runtime repository with `--runtime-repo` so Flatpak can obtain a missing runtime.

Single-file bundles do not provide the normal repository update path, and Flatpak's documentation notes that they omit dependencies and AppStream data. Use them for previews, direct downloads, removable media, or small audiences. Use a hosted repository when users need routine updates and software-center metadata.

### Other hosts and repositories

Any suitable static HTTP host can serve a Flatpak repository. A project website, object-storage bucket, CDN, or self-managed web server can replace GitHub Pages if it preserves repository paths and supports efficient HTTP requests. Generate static deltas and enable HTTP keep-alive where the host allows it.

An organization can also publish through another Flatpak repository whose policy accepts the project. Read that repository's current inclusion, signing, metadata, and automation rules before preparing a submission.

## Native packages

Build Debian, RPM, Arch, AppImage, or Snap artifacts only when the release contract requires them. Share one installed layout and one application identity rather than maintaining separate product metadata for each format.

For distribution packages:

- build against the target distribution's supported Rust and system-library floor;
- use distribution dependency names and policies from current official packaging documentation;
- split runtime, development, debug, locale, or license content where policy requires it;
- run package lint tools and test install, upgrade, downgrade policy where supported, and uninstall;
- verify desktop caches, icon caches, schemas, MIME databases, and service reloads through package hooks supplied by the distribution tooling;
- test on a clean target image instead of the development workstation.

For AppImage, account for libc compatibility, GTK and libadwaita policy, GIO modules, icon and desktop integration, schemas, resources, and portals. A copied Rust executable is not a complete desktop package.

## Release compatibility

State the supported matrix:

- CPU architectures;
- minimum Linux distribution or Flatpak runtime;
- GTK and libadwaita floor;
- Wayland and X11 policy;
- GPU or media requirements;
- device permissions;
- locale and accessibility support;
- upgrade and settings migration behavior.

Test the oldest supported contract as well as the development machine. Newer toolkit availability does not prove minimum-version compatibility.

## Release evidence

Before claiming a package is ready, record:

- immutable source revision and dependency lock state;
- clean build command and result;
- package and metadata linter results;
- installed file inspection;
- launch and primary-task test inside the package environment;
- sandbox permissions and portal behavior;
- architecture coverage;
- update and migration checks;
- known distribution, compositor, driver, device, or store-review risk.

## Primary references

- [GNOME Flatpak introduction](https://developer.gnome.org/documentation/introduction/flatpak.html)
- [Flatpak documentation](https://docs.flatpak.org/)
- [Flatpak builder tools](https://github.com/flatpak/flatpak-builder-tools)
- [Hosting a Flatpak repository](https://docs.flatpak.org/en/latest/hosting-a-repository.html)
- [Single-file Flatpak bundles](https://docs.flatpak.org/en/latest/single-file-bundles.html)
- [Flathub requirements](https://docs.flathub.org/docs/for-app-authors/requirements)
- [AppStream metadata](https://www.freedesktop.org/software/appstream/docs/)
- [Desktop entry specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
- [Icon theme specification](https://specifications.freedesktop.org/icon-theme-spec/latest/)
- [XDG base directories](https://specifications.freedesktop.org/basedir-spec/latest/)
