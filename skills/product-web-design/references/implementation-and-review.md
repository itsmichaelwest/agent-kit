# Implementation and review

## Implement the chosen design

Build from the approved scenes, actual content and chosen visual relationships. Use tokens for shared values where they help. In an existing project, use its components and brand system. Choose a framework or production tool only when the task calls for that decision; a design audit or copy task does not require a new build.

## Build the readable page first

Use semantic HTML to tell the story: a meaningful page heading, sections, ordered heading levels, paragraphs, links for navigation, and buttons for state changes. A heading's visual size does not have to determine its level. Give informative media useful alternatives and avoid duplicating decorative images in the reading order.

Use responsive image sources and explicit dimensions or aspect ratios. Make each image's declared sizes match the space it actually occupies at each layout, so the browser picks a suitable file. Load the opening's critical asset promptly and defer media that readers reach later. Inline looping clips are usually muted, play inline and wait to load until the reader approaches them. Provide a poster or still image when video cannot play. Plan how large media assets will load without assuming every visitor has a fast connection.

For component-specific states and checks, use [Interactive elements](interactive-elements.md). For scene planning and media lifecycle, use [Scroll and motion](scroll-and-motion.md).

Keep access to important content independent of enhancements. For a standalone page, meaningful HTML and ordinary links provide a useful base. In an existing application, follow its supported runtime contract and handle failures in loading or enhancement. This does not require introducing a new no-script architecture.

## Resolve the scene at real viewing sizes

Use the [craft system](craft-system.md) to align visible edges and baselines, establish type relationships and group content. Inspect actual image bounds and crops: transparent padding can make an object appear misaligned even when its box matches the grid. Keep numbered annotations attached to the detail they identify. Check word boundaries when responsive line breaks disappear, and keep secondary text readable on its rendered background.

Change the composition where the content needs a different arrangement. Inspect intermediate widths and short viewports as well as wide and narrow layouts. If an opening is sized to the viewport, bound it by its content: the headline, product and action should still fit on a short or landscape screen, and a tall screen should not leave an empty field. Prefer intrinsic sizing and normal flow where they fit. When a table or comparison needs to retain its two-dimensional relationship, provide a usable way to do so. Account for the actual height and safe areas of persistent navigation so it does not cover anchor destinations or focused controls. Give users ways to reach important content without relying on hover or precise dragging.

## Give motion a purpose

Motion can reveal a physical transformation, move between matched views, show a workflow, bring a chapter into focus, or add a restrained moment of tactile response or delight. Choose a technique and duration that suit the purpose.

Define the start, end and readable resting state of each scroll-linked scene. Preserve ordinary scrolling and let users move past the scene. They should not have to wait through a film to reach the next fact. Prevent large blank regions when loading, scripts or animation initialization fail.

Implement a reduced-motion presentation that preserves meaning while removing unnecessary movement. A useful still may be enough; a transformation may need a labeled pair or sequence. Slowing an animation or freezing its last frame is not always enough. Give autoplaying or looping media an accessible pause control. Inspect the fallback in use; a preference branch in the source alone does not prove it works.

## Give galleries and disclosures complete behavior

- Give galleries a discoverable next action, a visible selected state, and accessible names that identify the item or topic. Use tabs only when you implement their interaction and panel semantics.
- Keep content reachable with a keyboard and focus visible. Indicate unavailable previous/next actions consistently.
- Update the corresponding media and caption together when the selection changes. Do not use a progress decoration as the only label.
- Give disclosures an explicit expanded state and a controlled panel. Give dialogs a clear close action, handle focus appropriately, and return focus to the invoking control when they close.
- Keep essential qualifications outside optional disclosures.

## Inspect the experience, not only the source

Review the story, visual craft and operation separately. Read all the public copy alongside its imagery to check for repetition and unsupported implications. Then assess hierarchy, product scale, image/text relationships, pacing and precision against the brief. Finally, use the controls and check their states. Working controls do not establish that the imagery, composition or writing succeeds. Use `product-storytelling` for substantial editorial or narrative revision.

Capture representative views after transitions have finished: the opening, a chapter boundary, a detailed proof section, and the closing action. A screenshot taken during an opacity transition does not establish the final contrast or layout.

Check supported wide, intermediate and narrow layouts, and enlarge the text. Look for clipped headings, unreadable screen demonstrations, accidental horizontal page overflow, overlaps involving sticky navigation, and excessive empty space.

Use the implemented controls and confirm their visible results. Check reduced motion and delayed or unavailable media for the paths the page uses. Source inspection can show how a mechanism is intended to work; only runtime checks establish how it behaves in use. State any untested conditions in the handoff.

Do not claim this style improves conversion without measurement. Evaluate whether the hierarchy is clear, the proof is convincing, and the actions work. Measure business outcomes separately.
