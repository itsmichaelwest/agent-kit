# GNOME Advanced UI Patterns

Patterns for complex apps, verified against libadwaita 1.9 / GTK 4.22. Snippets are Python (PyGObject); for Vala/Rust syntax use the `developing-gtk-apps` language branches.

| Building | Read |
|----------|-----------|
| File manager, photo organizer | Drag & Drop |
| Multi-document app | Tabs |
| Media player, image viewer | Media Display |
| Dashboard with panels | Split/Paned Views |
| First-run experience | Welcome/Onboarding |

## Drag and Drop

GTK 4 DnD is controller-based: `GtkDragSource` on the origin, `GtkDropTarget` on the destination, data wrapped in a `GdkContentProvider`.

### Drag Source

```python
drag_source = Gtk.DragSource()
drag_source.set_actions(Gdk.DragAction.MOVE)

def on_prepare(source, x, y):
    item = get_item_at_position(x, y)
    return Gdk.ContentProvider.new_for_value(item)   # any GObject/GType value

def on_drag_begin(source, drag):
    icon = Gtk.DragIcon.get_for_drag(drag)
    icon.set_child(create_drag_preview(source.get_widget()))

drag_source.connect("prepare", on_prepare)
drag_source.connect("drag-begin", on_drag_begin)
widget.add_controller(drag_source)
```

### Drop Target

```python
drop_target = Gtk.DropTarget.new(MyItem, Gdk.DragAction.MOVE)  # GType filters drops

def on_drop(target, value, x, y):
    insert_at_position(value, x, y)
    return True   # accepted

drop_target.connect("drop", on_drop)
drop_target.connect("motion", lambda t, x, y: Gdk.DragAction.MOVE)  # return action or 0
drop_target.connect("leave", lambda t: hide_drop_indicator())
container.add_controller(drop_target)
```

### Reorderable List

Per row: a drag handle (`list-drag-handle-symbolic` icon) carrying the `GtkDragSource`, and a `GtkDropTarget` on the row itself:

```python
def create_row(self, item):
    row = Adw.ActionRow(title=item.title)
    handle = Gtk.Image(icon_name="list-drag-handle-symbolic")
    row.add_prefix(handle)

    drag_source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
    drag_source.connect("prepare",
        lambda s, x, y: Gdk.ContentProvider.new_for_value(item))
    handle.add_controller(drag_source)          # handle only, not whole row

    drop_target = Gtk.DropTarget.new(type(item), Gdk.DragAction.MOVE)
    drop_target.connect("drop",
        lambda t, value, x, y: self.reorder_item(value, before=item) or True)
    row.add_controller(drop_target)
    return row
```

### File Drops from External Apps

```python
drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)

def on_drop(target, value, x, y):
    for file in value.get_files():
        import_file(file.get_path())
    return True

drop_target.connect("drop", on_drop)
window.add_controller(drop_target)
```

## Undo/Redo Wiring

The undo manager itself is a plain command stack (execute/undo pairs on two stacks — no GTK involvement). The UI contract: expose `app.undo`/`app.redo` actions with `<Control>z` / `<Control><Shift>z`, keep them `set_enabled()` in sync with stack state, and surface destructive-action undo through toasts (see feedback table in SKILL.md). Action registration and accelerators: `developing-gtk-apps`.

## Tabs (AdwTabView)

```python
tab_view = Adw.TabView()

tab_bar = Adw.TabBar()
tab_bar.set_view(tab_view)
header.set_title_widget(tab_bar)

# Grid overview of all tabs + the button that opens it
tab_overview = Adw.TabOverview()
tab_overview.set_view(tab_view)
tab_overview.set_child(toolbar_view)      # wraps the main content

overview_btn = Adw.TabButton()
overview_btn.set_view(tab_view)
header.pack_end(overview_btn)
```

```python
def new_tab(title, content):
    page = tab_view.append(content)
    page.set_title(title)
    page.set_icon(Gio.ThemedIcon.new("text-x-generic-symbolic"))
    tab_view.set_selected_page(page)
    return page
```

Close confirmation uses the two-phase protocol — return `EVENT_STOP` to defer, then finish explicitly:

```python
def on_close_page(view, page):
    if page_has_unsaved_changes(page):
        ask_to_save(page, then=lambda ok: view.close_page_finish(page, ok))
        return Gdk.EVENT_STOP        # we'll decide via close_page_finish
    return Gdk.EVENT_PROPAGATE

tab_view.connect("close-page", on_close_page)
tab_view.connect("notify::selected-page",
                 lambda v, p: update_window_title(v.get_selected_page()))
tab_view.connect("page-reordered", lambda v, p, pos: save_tab_order())

# Per-tab context menu
def on_setup_menu(view, page):
    if page is None:
        return
    menu = Gio.Menu()
    menu.append("Duplicate Tab", "tab.duplicate")
    menu.append("Close Other Tabs", "tab.close-others")
    view.set_menu_model(menu)
tab_view.connect("setup-menu", on_setup_menu)
```

## System Notifications

| Feedback | Use case |
|--------------|----------|
| Toast | In-app events while the user is in the app |
| Banner | Persistent in-app state |
| `GNotification` | Events while backgrounded; survives app windows |

```python
notification = Gio.Notification.new("New Message")
notification.set_body("Alice: Hey, are you free?")
notification.add_button("Reply", "app.reply::alice")          # action with target
notification.set_default_action("app.open-conversation::alice")
notification.set_priority(Gio.NotificationPriority.HIGH)  # LOW/NORMAL/HIGH/URGENT

app.send_notification("message-alice", notification)   # stable ID enables update
app.withdraw_notification("message-alice")             # e.g. once conversation opened
```

## Popovers (Non-Menu)

Small, dismissed by clicking outside, no close button. Attach via `Gtk.MenuButton.set_popover()` or `set_parent()` + `popup()`.

Color picking — `GtkColorDialogButton` (4.10; `GtkColorChooserWidget`/`Button` are deprecated):

```python
color_button = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())
color_button.connect("notify::rgba", lambda b, p: apply_color(b.get_rgba()))
header.pack_end(color_button)
```

Tool palettes: flat `GtkToggleButton`s in a `GtkGrid` inside a `Gtk.Popover`; tool icons like brushes/erasers are not in the system theme — bundle them from the GNOME Icon Library.

## Media Display

### Image Viewer with Zoom Gestures

`GtkPicture` (`content-fit`, `can-shrink`) in a `GtkScrolledWindow`; Ctrl+scroll and pinch both zoom:

```python
scroll = Gtk.EventControllerScroll()
scroll.set_flags(Gtk.EventControllerScrollFlags.VERTICAL)

def on_scroll(controller, dx, dy):
    if controller.get_current_event_state() & Gdk.ModifierType.CONTROL_MASK:
        self.zoom(1.0 - dy * 0.1)
        return True      # consumed - don't scroll the window
    return False

scroll.connect("scroll", on_scroll)
self.add_controller(scroll)

zoom_gesture = Gtk.GestureZoom()
zoom_gesture.connect("scale-changed", lambda g, s: self.zoom(s))
self.add_controller(zoom_gesture)
```

### Player Controls

A `GtkBox` with the `toolbar` class: play/pause `GtkButton` (swap `media-playback-start-symbolic` / `media-playback-pause-symbolic`), seek `GtkScale` with `draw-value=False`, a `numeric`-class time label, volume via `GtkScaleButton` (`GtkVolumeButton` is deprecated):

```python
volume_btn = Gtk.ScaleButton.new(0.0, 1.0, 0.05, [
    "audio-volume-muted-symbolic", "audio-volume-high-symbolic",
    "audio-volume-low-symbolic", "audio-volume-medium-symbolic"])
volume_btn.connect("value-changed", lambda b, v: stream.set_volume(v))
```

## Split/Paned Views

`GtkPaned` for user-resizable panels (for sidebars that collapse adaptively, use `AdwNavigationSplitView`/`AdwOverlaySplitView` instead):

```python
paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
paned.set_start_child(left_panel)
paned.set_shrink_start_child(False)   # can't be dragged to 0
paned.set_resize_start_child(False)   # fixed width; extra space goes right
paned.set_end_child(right_panel)
paned.set_position(250)

# Persist the divider
paned.connect("notify::position",
              lambda p, _: settings.set_int("pane-position", p.get_position()))
```

## Welcome/Onboarding

First-run flow: `Adw.Carousel` of `Adw.StatusPage`s with `Adw.CarouselIndicatorDots`, gated by a GSettings boolean:

```python
carousel = Adw.Carousel(allow_long_swipes=True)
carousel.append(Adw.StatusPage(icon_name="image-x-generic-symbolic",
                               title="Welcome to App Name",
                               description="What your app does, in one line"))

last = Adw.StatusPage(icon_name="go-next-symbolic", title="Ready to Start")
start_btn = Gtk.Button(label="Get Started")
start_btn.add_css_class("pill")
start_btn.add_css_class("suggested-action")
start_btn.connect("clicked", lambda b: finish_onboarding())
last.set_child(start_btn)
carousel.append(last)

dots = Adw.CarouselIndicatorDots()
dots.set_carousel(carousel)
```

## Keyboard Shortcuts in Widgets

Mnemonics: `Gtk.Button.new_with_mnemonic("_Save")` (Alt+S); in menus, `_` in the translatable label.

Widget-scoped keys use a `GtkShortcutController` (app-level accelerators belong to actions — `developing-gtk-apps`):

```python
controller = Gtk.ShortcutController()
controller.add_shortcut(Gtk.Shortcut.new(
    Gtk.ShortcutTrigger.parse_string("Escape"),
    Gtk.CallbackAction.new(lambda w, a: cancel_action())))
controller.add_shortcut(Gtk.Shortcut.new(
    Gtk.ShortcutTrigger.parse_string("Delete"),
    Gtk.CallbackAction.new(lambda w, a: delete_selected())))
widget.add_controller(controller)
```
