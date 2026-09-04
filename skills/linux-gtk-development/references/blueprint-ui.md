# Blueprint UI and Rust

Use Blueprint for declarative GTK 4 and libadwaita widget trees when the repository already uses it or the user selects it for a new application. Keep state, commands, async work, domain policy, and complex behavior in Rust.

Blueprint is a source language. `blueprint-compiler` converts `.blp` files to GTK Builder XML. GTK does not load Blueprint syntax at runtime.

## Interpret GNOME Workbench correctly

Workbench separates an example into three concerns:

- **Code** contains Rust behavior and state;
- **UI** contains the Blueprint widget tree, properties, accessibility relations, and simple bindings;
- **Style** contains CSS;
- **Preview** renders their combined result.

Selecting Rust changes the code language. It does not make the widget tree procedural Rust. The Blueprint pane remains useful because GTK UI definitions are language-neutral after compilation.

A Workbench example is a prototype and API demonstration. Before moving it into an application:

1. Match its GTK, libadwaita, and Blueprint compiler features to the application's version floor.
2. Decide whether the UI belongs to an existing composite template, a new widget subclass, or a small builder-loaded object graph.
3. Replace Workbench-only object lookup and global helpers with the application's state, actions, and ownership model.
4. Add the `.blp` file to the build, resources, translation extraction, and packaging inputs.
5. Test startup, resource lookup, narrow layout, accessibility, and installed or Flatpak execution.

Workbench is for learning and live prototyping. Its panes do not prescribe a complete application architecture.

## Choose Blueprint deliberately

Choose Blueprint when:

- the UI has a stable hierarchy with many properties, child roles, style classes, or accessibility relations;
- visual structure changes more often than domain behavior;
- GNOME Builder or the Blueprint language server is part of the workflow;
- composite templates give each reusable widget ownership of its internal tree;
- translation extraction and GResource compilation already run in the build.

Build widgets in Rust when:

- the repository has a clear code-only convention;
- the tree is small or created from dynamic data;
- introducing `blueprint-compiler` would add an unsupported build or packaging dependency;
- a generated structure would be harder to understand than the Rust that creates it.

Preserve the existing construction method unless the user requests a migration. Do not convert working Rust or XML trees merely to standardize syntax.

Blueprint remains marked experimental by its own documentation. Pin a tested compiler release or obtain it from the selected GNOME SDK. Do not follow an unpinned `main` branch in release builds. Review Blueprint compiler updates as source-language and build-tool changes.

## Preferred production boundary

For a substantial view, give each application widget or window subclass its own composite template:

```text
src/window.rs                 Rust subclass, state, actions, callbacks
data/ui/window.blp            Blueprint source owned by that subclass
data/ui/window.ui             generated build output, when the build emits it
data/app.gresource.xml        resource manifest for compiled UI and assets
build.rs or data/meson.build  generation and resource dependency graph
```

Commit `.blp` source. Generate `.ui` during the build unless the repository deliberately vendors generated output. Apply changes to `.blp`, never to generated XML.

Use a normal top-level object for a small `gtk::Builder` graph. Use a `template` when the UI defines the internals of a Rust GObject subclass. GTK applies a template to an instance during construction, so an ordinary Builder cannot load it as a general object graph.

## Blueprint template

This template defines the presentation and the child IDs used by Rust:

```blueprint
using Gtk 4.0;
using Adw 1;

template $ExampleWindow : Adw.ApplicationWindow {
  title: _("Example");
  default-width: 720;
  default-height: 540;

  content: Adw.ToolbarView {
    [top]
    Adw.HeaderBar {}

    content: Adw.StatusPage status_page {
      title: _("Nothing Here Yet");
      description: _("Create an item to begin.");

      child: Button create_button {
        label: _("Create Item");
        action-name: "win.create-item";
        styles ["suggested-action", "pill"]
      };
    };
  };
}
```

Match the external type name after `$` to the Rust subclass `ObjectSubclass::NAME`. Match the parent after `:` to `ParentType`. Keep IDs only for objects that Rust, another Blueprint object, a binding, or a test must address.

Prefer detailed actions such as `win.create-item` for commands. This keeps button, menu, shortcut, and accessibility activation on the same command path. Use signal callbacks in templates only when the callback is local presentation behavior and the gtk-rs callback binding is explicit.

## Rust composite template from a resource

An installed application can compile Blueprint to XML, embed the XML in GResource, and load it from a Rust subclass:

```rust
use adw::subclass::prelude::*;
use gtk::{CompositeTemplate, glib, subclass::prelude::*};

#[derive(Default, CompositeTemplate)]
#[template(resource = "/com/example/App/ui/window.ui")]
pub struct Window {
    #[template_child]
    pub status_page: TemplateChild<adw::StatusPage>,
}

#[glib::object_subclass]
impl ObjectSubclass for Window {
    const NAME: &'static str = "ExampleWindow";
    type Type = super::Window;
    type ParentType = adw::ApplicationWindow;

    fn class_init(klass: &mut Self::Class) {
        klass.bind_template();
    }

    fn instance_init(obj: &glib::subclass::InitializingObject<Self>) {
        obj.init_template();
    }
}

impl ObjectImpl for Window {}
impl WidgetImpl for Window {}
impl WindowImpl for Window {}
impl ApplicationWindowImpl for Window {}
impl AdwApplicationWindowImpl for Window {}
```

Register the compiled resource before the class is first instantiated. The resource path must match the GResource prefix and generated `.ui` filename exactly.

Expose only children Rust needs through `TemplateChild<T>`. Keep ordinary internal widgets private to Blueprint. Application state belongs in Rust fields or model objects, not in a collection of widgets used as an implicit model.

## Direct gtk-rs Blueprint compilation

Current gtk-rs also supports Blueprint directly in `CompositeTemplate` when the `gtk4` crate enables its `blueprint` feature:

```toml
[dependencies]
gtk = { package = "gtk4", version = "...", features = ["blueprint"] }
```

```rust
#[derive(Default, gtk::CompositeTemplate)]
#[template(file = "window.blp")]
pub struct Window {
    #[template_child]
    pub status_page: gtk::TemplateChild<adw::StatusPage>,
}
```

This form invokes the `blueprint-compiler` executable during Rust macro expansion. Every local, CI, Flatpak, and distribution build environment must provide it. Current gtk-rs accepts `file` or `string` for this mode. Its `resource` form expects compiled Builder XML.

Choose one build path per template:

- compile `.blp` to `.ui`, embed the `.ui`, and use `#[template(resource = "...")]`; or
- enable gtk-rs Blueprint support and use `#[template(file = "...")]`.

Use one path for each template. Prefer the repository's established resource pipeline. A resource template fits projects that already bundle UI, CSS, icons, and menus in one GResource.

## Build and packaging contract

The build graph must make the generated XML an explicit dependency of resource compilation:

```text
window.blp
    -> blueprint-compiler
window.ui
    -> glib-compile-resources
application.gresource
    -> Rust binary or installed resource bundle
```

For Meson, use `blueprint-compiler batch-compile` in a `custom_target` and pass that target as a dependency of `gnome.compile_resources`. For a Cargo-native build, preserve the repository's `build.rs` or task-runner integration and declare every input so changing a `.blp` file rebuilds the resource.

Treat `blueprint-compiler` as a build dependency. It also needs the typelibs for every imported namespace, including `Gtk-4.0.typelib` and `Adw-1.typelib` when `using Adw 1;` appears. Language-server hover documentation can also require the matching GIR files.

Flatpak and offline builders must receive the compiler from the selected SDK or a pinned manifest module. An offline release build cannot depend on a Meson wrap fetching `main`.

## Translation and accessibility

Mark user-visible text with `_()` in Blueprint and include `.blp` source in translation extraction. Avoid extracting the same strings from both `.blp` and generated `.ui` output.

Blueprint can express accessibility properties and relations beside the widget they describe. Use that for stable structure, as in the Workbench accessibility examples. Rust must still update names, descriptions, states, and relations when they depend on runtime data.

Run the Blueprint linter. It catches some HIG and accessibility problems, but it does not replace keyboard, screen-reader, large-text, high-contrast, or focus-order testing.

## Common failures

| Failure | Corrective pattern |
|---|---|
| Treating `.blp` as a runtime GTK format | Compile it to Builder XML or use gtk-rs compile-time Blueprint support |
| Copying a Workbench page directly into an app | Place it behind the app's widget, action, state, resource, and version contracts |
| Loading a `template` with ordinary `gtk::Builder` | Bind it from the matching GObject subclass during class and instance initialization |
| Mismatched `$Type`, `ObjectSubclass::NAME`, and `ParentType` | Keep all three names and parent types identical in meaning |
| Editing generated `.ui` | Edit committed `.blp` and rebuild |
| Using every widget ID as application state | Expose only required template children and keep state in models or Rust fields |
| Calling domain logic from many template callbacks | Route commands through actions and keep policy in Rust |
| Enabling `gtk4/blueprint` without provisioning the compiler | Install or package `blueprint-compiler` in every build environment |
| Using `#[template(resource = "...")]` with raw Blueprint | Put compiled XML at that resource path |
| Copying syntax from a newer Workbench or compiler | Pin the compiler and validate against the application's GTK and libadwaita floor |
| Extracting `.blp` and generated `.ui` | Extract translations once from Blueprint source |
| A successful preview treated as completion | Build the packaged app and test behavior, focus, accessibility, and adaptive states |

## Validation

For a changed Blueprint view, compile it and inspect the affected behavior. Select additional checks from the affected contracts below; use the full set for resource-pipeline changes or release validation:

- compile or lint every `.blp` file in the same environment as the application build;
- rebuild resources; use a clean build when generated-input tracking or stale output is in question;
- confirm no generated file needs a manual edit;
- start the application through its installed or Flatpak entry point;
- exercise every referenced action and template child;
- test narrow and wide sizes, light and dark appearance, high contrast, large text, keyboard navigation, and translated strings;
- fail CI when Blueprint compilation, resource generation, or translation extraction fails.

## Primary sources

- [Blueprint overview](https://gnome.pages.gitlab.gnome.org/blueprint-compiler/)
- [Blueprint setup](https://gnome.pages.gitlab.gnome.org/blueprint-compiler/setup.html)
- [Blueprint composite templates](https://gnome.pages.gitlab.gnome.org/blueprint-compiler/reference/templates.html)
- [Blueprint diagnostics and linter](https://gnome.pages.gitlab.gnome.org/blueprint-compiler/reference/diagnostics.html)
- [Blueprint packaging notes](https://gnome.pages.gitlab.gnome.org/blueprint-compiler/packaging.html)
- [gtk-rs composite templates](https://gtk-rs.org/gtk4-rs/stable/latest/book/composite_templates.html)
- [gtk-rs `CompositeTemplate` derive](https://gtk-rs.org/gtk4-rs/stable/latest/docs/gtk4_macros/derive.CompositeTemplate.html)
- [GNOME Workbench](https://teams.pages.gitlab.gnome.org/Websites/apps.gnome.org/Workbench/)
