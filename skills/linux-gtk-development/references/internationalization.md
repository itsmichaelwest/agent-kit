# Internationalization

Use this reference for gettext setup, translated UI and metadata, translator context, plural forms, locale formatting, expansion, and right-to-left layouts.

## Project contract

Find the gettext domain, locale directory, source catalog, language list, build integration, and initialization point. The domain should remain stable across Rust code, templates, desktop metadata, AppStream metadata, and installed translation files.

Initialize locale and gettext before constructing translated UI. Keep generated configuration in the build system rather than hard-coding an installation prefix that differs between development, system packages, and Flatpak.

## Source strings

- Mark complete user-facing strings for translation.
- Use placeholders inside one translatable sentence. Do not concatenate translated fragments.
- Use plural APIs for count-dependent text. English singular and plural rules do not generalize.
- Add translator comments when a short label, placeholder, domain term, or ambiguous word lacks context.
- Give identical English words separate message context when their meanings differ.
- Keep internal errors, log fields, action names, schema keys, and protocol values out of translation.
- Avoid embedding markup in a message when separate styled spans can preserve translator control.

Use named placeholders where the Rust localization library supports them. Validate that translated input cannot alter a format or markup contract unexpectedly.

## Templates and Blueprint

Mark translatable properties in the project's template format. Add every template and Rust source file with user-facing text to the extraction catalog. Generated Blueprint XML should not cause duplicate extraction from both source and output.

Keep runtime-created labels and accessibility text under the same gettext domain.

## Desktop and AppStream metadata

Use the translation workflow supported by the project's build and metadata tooling. Keep application name, summary, keywords, descriptions, and release information synchronized without maintaining unrelated manual copies.

Validate the installed localized metadata as well as the source `.in` file.

## Formatting

Use locale-aware facilities for dates, times, numbers, units, and collation when the product calls for localized formatting.

- Do not assume month, day, and year order.
- Do not assume a 12-hour or 24-hour clock.
- Do not hand-insert decimal or thousands separators.
- Keep machine-readable timestamps and protocol values locale independent.
- Let translators reorder placeholders.
- Use Unicode-aware case and collation behavior for user-visible sorting and search, with product-specific rules documented.

## Layout review

Test a language with long strings and a right-to-left locale.

- Allow labels to wrap where truncation removes meaning.
- Avoid fixed widths based on English text.
- Keep icons with directional meaning mirrored through the toolkit's direction support.
- Check header bars, preference rows, buttons, menus, status pages, notifications, and dialogs for expansion.
- Verify focus and reading order in right-to-left layout.
- Keep paths, code, device identifiers, and other direction-sensitive content readable with appropriate isolation.

Pseudo-localization is useful for finding unmarked strings, unsafe concatenation, clipped controls, and direction assumptions before translators encounter them.

## Translation workflow

The repository's commands are authoritative. A typical workflow extracts a POT file, updates PO files, compiles MO files through the build, installs them under the gettext domain, and launches the app under a selected locale.

Check that:

- every source containing user text is extracted;
- obsolete strings do not hide a missing replacement;
- format placeholders match in each translation;
- plural entries compile;
- the installed package finds the locale directory;
- Flatpak includes the translations and locale extension behavior expected by its runtime.

## Primary references

- [GNU gettext manual](https://www.gnu.org/software/gettext/manual/gettext.html)
- [GLib internationalization](https://docs.gtk.org/glib/i18n.html)
- [GNOME writing style](https://developer.gnome.org/hig/guidelines/writing-style.html)
- [Unicode bidirectional algorithm](https://unicode.org/reports/tr9/)
