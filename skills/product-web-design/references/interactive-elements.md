# Interactive elements

Choose an interaction that answers the reader's question. Use only the sections relevant to the page you are building or reviewing. The details below describe how each component should behave; you do not need to include every component.

## Contents

- [Choose the right form](#choose-the-right-form)
- [Local navigation and an expanded exploration panel](#local-navigation-and-an-expanded-exploration-panel)
- [Timed highlights](#timed-highlights)
- [Caption rails](#caption-rails)
- [Product viewers, finishes, and detail panes](#product-viewers-finishes-and-detail-panes)
- [Matched comparisons](#matched-comparisons)
- [Baseline selectors](#baseline-selectors)
- [Detailed benchmarks and modals](#detailed-benchmarks-and-modals)
- [FAQ disclosures](#faq-disclosures)
- [Visual treatment](#visual-treatment)

## Choose the right form

| Reader's question | Useful form | Information it must carry |
| --- | --- | --- |
| What are the main reasons to care? | Highlights gallery | A few distinct benefits, each with its own demonstration |
| What else can it do? | Caption rail | Independent examples that can be browsed at the reader's pace |
| What is this part, finish, or control? | Product viewer | A selected detail, its location or appearance, and an explanation |
| What changes when I choose this setting? | Matched comparison | Consistent framing with one clearly identified variable |
| What would I gain from my current version? | Baseline selector | The chosen reference, relevant results, and conditions |
| How was that measured? | Detailed chart or modal | Configuration, workload, units, source, and methodology |
| Where am I, and what can I do next? | Local navigation | Current product, meaningful section destinations, primary action |
| Does this work in my situation? | FAQ or disclosure | A complete answer to a real adoption question |

An image with controls is useful only when the selected state answers a question. Avoid adding a gallery to make a sparse page look busy.

An illustrative interaction should help the reader understand the product. Give it a clear invitation, controls and a visible result. Keep explanations of generated sample data, browser permissions and prototype storage or upload behaviour in the handoff. Do not present them as product benefits, captions or FAQ material. A separate simulation label is not part of the default composition.

If readers could mistake a particular action or result for a real transaction or measurement, correct how you present it or add the smallest necessary clarification at that point. When showing an existing product, reproduce its actual behaviour. When illustrating a concept, follow the approved design. Do not imply that switching illustrative states restores, exports, purchases or saves the reader's actual data.

Use native controls where they fit. Press feedback can begin immediately, but activation must retain normal release and cancellation behaviour. Keep the visible state, accessible state and actual state in agreement. When a custom control is necessary, preserve keyboard, touch and pointer paths. An optional effect should not delay an action or become its only feedback.

If the page collects input, for example to register interest, give each field a visible label. Report a problem beside its field once the reader has left the field or submitted, say how to fix it, and keep what they typed. After submission, say what happened and what comes next. Offer only actions that actually exist.

## Local navigation and an expanded exploration panel

Keep a small local bar readable over the page, with the product identity, a few useful destinations, and a clear next action. On a long page, you may reveal it after the opening has established the product. If a section menu would crowd the bar, offer an explicit **Explore** action with a fuller accessible name.

An expanded exploration panel can use the same surface. Define its behavior in each state:

| State | Behavior |
| --- | --- |
| Before reveal | Reading starts with the hero; hidden controls are not focusable |
| Collapsed | Identity and action remain available without obscuring content |
| Opening | Measure the target content; prevent conflicting transitions; move focus deliberately |
| Expanded | Expose section choices; constrain scrolling to the panel if it covers the page; keep Close reachable |
| Closing | Restore page scrolling and the collapsed state; return focus to the invoking control |

If the panel behaves as a modal, use appropriate dialog semantics, contain keyboard focus, and support Escape. If it remains a nonmodal disclosure, do not trap focus.

When the reader chooses a destination, close the panel and navigate to that section. Leave its heading visible below sticky bars. If the reader closes the panel without choosing a destination, preserve their reading position.

Use descriptive section names. A list of repeated **Discover more** links gives little orientation. Keep the primary action consistent between collapsed and expanded layouts. Ensure hidden duplicate controls do not appear twice in the reading order.

At narrow widths, allow the expanded content to scroll and account for safe areas. At large text sizes, prefer a simpler layout that lets labels wrap instead of compressing them. With reduced motion, switch directly between useful states. If scripting fails, retain ordinary links.

Check the reveal boundary in both scroll directions; keyboard entry before reveal; open, Escape, and focus return; a section link; long translated labels; and a short viewport.

## Timed highlights

Use timed highlights when a guided sequence helps readers follow a small set of short demonstrations. Keep the selected topic, its media, any explanatory text, and its progress indicator together as one state. A separate playback control must remain available.

Define playback explicitly:

- Entering the section may begin playback if motion is permitted and the user has not paused.
- Leaving the section pauses playback without erasing an explicit user pause.
- Opening a film, dialog or other overlay above the gallery is also a system pause.
- Selecting a topic manually stops automatic advancement so the reader can inspect it.
- If media fails, leave an informative still and any necessary explanation available. Do not leave the sequence stuck on a loader.
- Choose what happens on completion. A **Replay** state is often clearer than automatically looping a long sequence.
- When the user reenters the section, respect their previous choice. Track a system pause separately from a user pause.

Use topic labels; anonymous dots alone do not identify the topics. Dots or a filling capsule can show progress visually, while accessible names identify each topic and the selected state. Use tab semantics only if the control and panels follow the corresponding keyboard behavior. Avoid announcing continuously changing progress as live text.

If a caption is useful, keep it short enough to understand during its display. Let the image demonstrate the point; add an explanation only where it contributes meaning. Do not make a required qualification disappear with a slide transition. **Play**, **Pause**, and **Replay** should describe the available action, with the gallery identified in the accessible name.

Large cards can show part of the next card at the edge. Use horizontal overflow and snapping where they fit the implementation; do not intercept vertical scrolling. A card centered on desktop can align to the leading edge on a phone. Keep progress and playback controls clear of text, imagery, safe areas, and the persistent page action.

Check automatic start, manual selection, pause, leave and reenter, finish and replay, reduced motion, loading failure, keyboard operation, and a reader who scrolls past before media loads. Confirm the chosen media and caption agree after rapid changes.

## Caption rails

A caption rail lets readers manually browse examples of equal importance. Do not give it autoplay just because the opening uses a timed gallery.

Keep each visual and any useful explanation together in a stable layout. A short phrase or one sentence may be enough. Add more explanation only when it supplies meaning the image and nearby copy do not already convey. Let a self-explanatory example stand alone. Use consistent text treatments without forcing every item to have the same caption structure or word count.

Show continuation through a partial next item, clear previous/next controls, or both. Disable unavailable directions at the boundaries. Keep native touch and trackpad scrolling. Paddle activation should advance a predictable item or group and keep the selected content within the viewport. Keyboard navigation must not unexpectedly move focus back to the start of the page. If items move as they enter, leave room inside the scroll container so the movement is not clipped at its edges.

On smaller screens, keep the demonstration readable rather than squeezing several tiny cards into view. Allow the last card to settle cleanly at the trailing gutter. If an example is essential to understanding the main promise, give it a chapter instead of hiding it deep in the rail.

Check the first and last positions, pointer and keyboard controls, direct scrolling, captions with different lengths, and focus visibility. Check that the rail does not accidentally make the whole document overflow horizontally.

## Product viewers, finishes, and detail panes

Keep looking around the object, choosing a variant, and learning about a feature distinct. These tasks may share a viewer, but each control should make its purpose clear.

Begin with a useful landing image. A 2D tour can be enough: selecting a named detail shows the corresponding crop, still, or short video. Use 3D only when changing viewpoint reveals something useful and suitable assets exist. Reserve stable space while loading. If the enhancement fails, keep a meaningful still and the feature descriptions.

A detail control should identify what it opens. When it opens, show the description and relevant media, update expanded state, and move focus if the layout change warrants it. When it closes, restore the original control and a sensible viewpoint. Previous/next controls should move through the same ordered set of details. Hidden panels must not remain keyboard destinations.

Color and material choices need names, selected states, and a visible current label. A swatch alone cannot communicate its finish to everyone. Use native radio behavior where appropriate; keep arrow-key movement, focus, and the selected media coherent. A custom group should match native behavior: arrow keys wrap at either end and follow the writing direction. If changing the variant also changes specifications or availability, update those facts together. Do not imply that a cosmetic preview changes the configuration being purchased unless it actually does.

A mobile viewer may work better as a linear tour with the controls and text beneath the image. Keep detail text reachable without covering the entire subject. Provide an alternative to precision dragging. If an angle slider exists, give it a meaningful label and value; an unexplained percentage is not enough.

Check every variant and detail, close/return, repeated selection while loading, keyboard traversal, zoomed text, lost 3D support, and the small-screen arrangement. Confirm the fallback communicates the same important facts, even if it cannot reproduce the effect.

## Matched comparisons

Use matched imagery to show what changes with one choice: a setting, material, output mode, or before/after result. Hold framing and other conditions steady so the reader can interpret the change. Label the actual variable in the selector. If the scene does not make the significance or conditions clear, add an explanation. A caption need not repeat the visible difference.

A crossfade keeps corresponding parts in the same position; a swipe comparison may help readers inspect a boundary. Avoid a wipe or zoom that exaggerates the difference. Maintain the same crop, scale, and comparison conditions unless a difference is intentional and disclosed.

Update selected state and media together. Keep outgoing content available only for the transition, then remove it from interaction and reading order. Preserve the user's selection after resizing when possible. A direct link to a particular example should initialize both the control and panel consistently.

Check all choices, rapid switching, keyboard selection, a narrow crop, reduced motion, and the conditions behind the comparison. A visually striking result is not evidence that the test was fair.

## Baseline selectors

A baseline selector answers a personal question such as what changes from a reader's current model or plan. Prefer a native select when the choices are a straightforward list.

Every option maps to a complete comparison: baseline label, result values, units, explanatory copy, and applicable conditions. Update the whole group at the same time. If a figure changes while its baseline label still shows the previous selection, the result is misleading.

Use short labels that readers recognize. Introduce the selector with a literal question or instruction, then present the selected comparison nearby. Explain “up to” results, percentages, and durations against their real reference. Do not populate unsupported combinations with extrapolated numbers.

A brief fade can soften a change of facts. If the content height differs, preserve the reader's position and avoid moving the selector away from the pointer. Keep the old valid content visible while new data loads. Distinguish unavailable data from a zero result, and avoid unnecessary animation of the numbers themselves.

Check every supported mapping, the default selection, unavailable combinations, rapid changes, content-height changes, and reduced motion. Verify values against their data source separately from checking the UI.

## Detailed benchmarks and modals

A compact claim can open a more detailed explanation when readers need to inspect evidence. Keep any condition that changes the claim's meaning beside the claim itself. The modal can hold methodology and fuller results.

Within a benchmark view, keep selectors for different comparison dimensions separate. For example, a workload tab answers which task was measured, while a configuration selector answers which machine or plan was tested. State the active combination above the result. If a choice makes another option invalid, choose and announce a valid combination or explain that no result is available.

Charts need units, a baseline, readable labels, and the relevant test conditions. Retain those when switching tabs. Supply a text or table equivalent for essential values. Do not make the most favorable result the only discoverable one, and do not infer measurements for an untested configuration.

A modal needs a meaningful heading, close control, Escape handling, appropriate focus containment, and focus return. Handle content taller than the viewport and lock background scrolling only while needed. Nested tab panels inside one modal are usually simpler than opening a second modal. Place relevant footnotes inside the modal or provide a way to navigate to them. A footnote marker must let the reader reach its explanation.

Check opening from the real trigger, Tab and Shift+Tab, Escape, focus return, scroll position, every supported selector combination, long content, and a failed chart asset. With scripts unavailable, important evidence should remain reachable.

## FAQ disclosures

Include an FAQ only when there are useful product questions left to answer. Write a question a prospective user would actually ask, and answer it from established product facts. Questions about how the website prototype was made, what its simulation cannot do or what the author has not been told do not belong here.

Answer directly before adding conditions or explanation. Keep useful detail even when it takes several paragraphs. Slogans cannot replace those answers.

Use native disclosure elements where they fit, or a button associated with its answer panel that exposes expanded state. Keep the whole question clickable, with an icon as a secondary cue. A link to an answer inside a closed disclosure should open it before moving scroll or focus there. Choose whether several answers may remain open. Multiple-open behavior is useful when readers compare requirements across questions.

If **Expand all** exists, define what it does when some answers are already open: show **Collapse all** only when every answer is open; otherwise offer **Expand all**. Bulk changes should finish in a coherent state even if a panel is already moving. An individual panel should allow interruption or safely complete its transition without losing the reader's action.

A height transition can clarify where the answer appeared, but should not leave partially clipped text. Disable unnecessary movement for reduced motion. Allow the title and answer to wrap naturally, and give the icon its own space. Keep the answer content accessible if scripting fails.

Check one answer, multiple answers, mixed state, bulk open/close, repeated activation, keyboard focus, long answers, and text enlargement. Verify that qualifications essential to the main story also appear where the reader needs them, rather than only in the FAQ.

## Visual treatment

This reference defines behaviour and states. Use the [craft system](craft-system.md) to decide how elements look together, and adapt structure, placement and timing to the content. Use shared values from the established identity where they create consistency. Where the task benefits from a composition specific to the scene, make that choice deliberately; such an exception does not break the system. For scroll scenes, read [Scroll and motion](scroll-and-motion.md).
