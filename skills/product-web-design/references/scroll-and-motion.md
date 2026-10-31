# Scroll and motion

Motion can explain a change, preserve continuity, direct attention or add a moment of pleasure. Choose the treatment to suit its purpose: an object opening, a responsive control and a theatrical reveal have different needs. Keep the product and reading experience central. Give readers useful states when movement stops and a way to proceed.

## Contents

- [Choose a mechanism](#choose-a-mechanism)
- [Define the scene before implementing it](#define-the-scene-before-implementing-it)
- [Calculate scroll geometry](#calculate-scroll-geometry)
- [Coordinate copy and media](#coordinate-copy-and-media)
- [Separate media loading from presentation](#separate-media-loading-from-presentation)
- [Scrub video deliberately](#scrub-video-deliberately)
- [Recompose motion on small screens](#recompose-motion-on-small-screens)
- [Respect interruption and motion preferences](#respect-interruption-and-motion-preferences)
- [Choose timings for the job](#choose-timings-for-the-job)
- [Separate viewport effects from motion preferences](#separate-viewport-effects-from-motion-preferences)
- [Validate what readers experience](#validate-what-readers-experience)

## Choose a mechanism

| Mechanism | Useful purpose | Cost or limit |
| --- | --- | --- |
| Short opacity or position transition | Introduce a chapter or clarify a state change | Can delay reading if applied to every element |
| Matched crossfade | Compare the same subject under different conditions | Requires aligned assets and truthful comparison conditions |
| Ordinary video with playback controls | Show a process that has its own timing | Readers need to pause, replay, or skip it |
| Sticky composition with transform | Keep a subject visible while a few details change | Needs a defined scroll range and a fallback when content does not fit |
| Scroll-scrubbed video | Reveal a continuous physical transformation at the reader's pace | Asset loading, seeking, responsive timing, and failure behavior are substantial work |
| Interactive 3D | Let a viewpoint answer questions a fixed view cannot | Needs appropriate assets, input alternatives, and a useful fallback |

Use the existing project tools. A static sequence of good images can explain more clearly than a large animation system built around weak assets.

## Define the scene before implementing it

Write a short scene specification for a substantial scroll sequence:

- Purpose: what should this sequence help the reader notice, understand or feel?
- Beginning: what meaningful image and copy appear before movement?
- Change: what moves, what stays fixed, and which detail becomes apparent?
- End: what image and text remain long enough to read before the next chapter?
- Range: where does progression start and finish relative to the section and viewport?
- Fallback: which still or ordinary layout communicates the same important fact?

Write the specification to fit the scene. Do not invent several stages just to fill a template. If it makes the connection clearer, you can keep the copy still while the image changes.

## Calculate scroll geometry

Separate the section's document height from the subject's sticky viewport. The section height gives the sequence room to progress; the sticky viewport keeps the subject visible. Base the duration on what must be shown and read rather than assigning a tall spacer to every chapter.

For a simple scene, normalize the reader's position between a start and end boundary:

`progress = clamp((scrollPosition - start) / (end - start), 0, 1)`

If the start and end boundaries are equal or reversed, show a safe static result. Apply easing only when it improves the demonstration. A direct mapping can make a scrubbed sequence feel responsive to scrolling. Do not animate scroll position itself merely to enforce the planned pacing.

Include navigation height and safe-area offsets when calculating the visible region. Avoid pinning media and copy that together exceed the available viewport height. Recalculate when asset dimensions become known, text wraps differently, the viewport changes, or a disclosure changes relevant content height. Organize layout reads and writes to avoid repeatedly forcing layout.

Movement tied to scrolling runs on every frame, so keep it cheap. Prefer transform and opacity changes. Measure filters, large blurs and anything that triggers layout on a representative device before keeping them. Apply rendering hints only while a scene is active, and stop animation loops when nothing is moving. Use a performance specialist when frames drop.

Specify what happens when the user scrolls backward, jumps to an anchor, restores a previous scroll position, or skips the entire scene with a large scroll. Every entry point should produce a valid state. Do not assume the user saw the beginning.

A scene can fail to fit because the viewport is too short or too narrow. Enable enhanced layouts only when both the available width and height are suitable. Return to the authored base layout when either becomes unsuitable. Test orientation and breakpoint changes, and check that they do not leave stale transforms or scroll space.

## Coordinate copy and media

A reveal can introduce a headline and then the supporting media. The reader should be able to understand the section before the full composition finishes. Keep text readable for the part of the sequence where it is useful. Avoid repeatedly fading essential copy in and out as it crosses a narrow threshold.

Coordinate the explanation with the visible detail it describes. A caption should appear while its subject is visible and remain long enough to read. If the subject moves away, move or replace the caption deliberately. Keep availability and other important conditions visible without requiring the reader to stop at an exact scroll position.

Stagger closely related elements only when the sequence helps the reader understand their relationship. A long series of identical entrance effects makes every part compete for attention. Use a stable resting state between major sequences.

## Separate media loading from presentation

Track whether each asset has not been requested, is loading, is ready, or has failed. Keep a useful poster or still while loading. Reserve space so the page does not jump when the media appears.

Start fetching before an expensive scene reaches the viewport. Set a limit on how far ahead to preload, based on asset size and network cost. When the reader has asked to reduce data use, keep looping or decorative video at its poster and do not preload it; this preference is separate from reduced motion. Do not fetch every distant demonstration at initial page load. Release or pause distant media where that meaningfully reduces resource use, while preserving the reader's selected state.

Show the fallback after a timeout, unsupported format, rejected playback request, or failed 3D initialization. Clear stale loaders and avoid leaving the original tall scroll range around a failed asset. Do not restart downloads or replay the intro whenever the reader makes a small movement across a boundary.

Handle visibility changes. Returning from another tab should restore the appropriate selected or scroll-derived state, not unexpectedly start sound or replay an unrelated introduction.

## Scrub video deliberately

Scrubbing maps normalized progress to a time in the video. This differs from starting normal playback when an element enters view. Seek only once metadata and duration are available. Keep an informative frame visible before the first useful seek. Handle the media's actual seeking behavior; a requested time may not be ready immediately.

Choose an encoded asset and frame cadence suitable for seeking. Large opaque video and transparent compositing may require different formats. Use available platform support and avoid importing a complicated streaming architecture unless the content justifies it.

Consider which part of the clip belongs in the story. If its opening is irrelevant, progress can map to a subset of the video. The final frame should support the next paragraph or transition rather than ending on a half-finished movement.

Check slow scrolling, rapid scrolling, reversal, loading mid-scene, a jump to the scene's end, tab visibility changes, and failed media. Inspect actual frames and text, not only a progress value in a debugger.

## Recompose motion on small screens

Choose a narrower crop and a shorter or differently placed range when the subject changes scale. A mobile scene may begin sooner, stop before the same document boundary, use different assets, or become a simple sequence of stills.

Keep the feature legible. If shrinking a desktop composition makes interface text unreadable, show a closer view or separate its steps. Position explanatory copy so it can be read without covering the subject. Preserve ordinary scrolling on a short screen, even if that requires changing an impressive desktop effect.

Test intermediate widths as well as the endpoints. A breakpoint is a composition decision, and the awkward width is often between the named sizes.

## Respect interruption and motion preferences

Keep the user's choices separate from automatic progression. Selecting a gallery item or pressing Pause should stop automatic advancement until the user deliberately resumes it. Leaving the viewport is a system pause; it should not erase an explicit user pause.

When the reader drags a comparison handle, scrubs a viewer or swipes a gallery, the content should follow the pointer directly and return to a valid state if the gesture is cancelled. When a transition is interrupted or reversed, continue from what is currently on screen instead of jumping back to its starting point.

For reduced motion, show meaningful states rather than simply extending animation durations. Remove scrubbed travel, parallax, large scaling, and automatic progression where they add unnecessary movement. Show the key still, readable copy, and working controls. If a transition conveys a necessary state change, a brief fade or immediate switch can be enough.

List the motion used in navigation morphs, media, comparisons, reveals, counters, disclosures and hover states. A query that handles one type does not cover the others. A counter used for emphasis is not a measurement; do not make it look like a live instrument without actual data.

Apply the preference at initial load. If the implementation supports preference changes during the session, apply it then as well. Check that the static layout does not retain hidden text, empty sticky ranges, invisible controls, or transforms from the enhanced state. Provide explicit pause controls for time-based media independently of the operating-system preference.

## Choose timings for the job

Use the [craft system](craft-system.md) to choose initial timings, then tune distance, easing and duration together in the actual scene. Small feedback effects, large movements and the time needed to read text have different needs. A deliberate reveal may take longer than an ordinary state change; a direct selection should feel responsive. Keep caption reading time distinct from transition duration, and do not make a timed highlight disappear before its point can be understood.

A spring can help a surface resize or settle, while a regular easing curve can suit a short fade. Avoid applying one spring to all movement. Treat the motion as complete when the new state is clear and the next action is available. Decorative elements may still be moving.

## Separate viewport effects from motion preferences

Use a small matrix to compare wide and narrow layouts, each with normal and reduced motion. Confirm the browser's actual `prefers-reduced-motion` result. A static narrow hero may be the normal responsive design, so it cannot by itself prove that the motion preference works. Compare playback controls and selected content over time as well as screenshots.

Check initial load with the preference already set separately from a live preference change. A media query can change while classes set during initialization to enable enhancements remain unchanged. Verify what the page renders after the change. A preference flag alone does not prove success, and a class alone does not prove failure. A reload may be needed to inspect the initial-load path, but does not prove live adaptation.

Test voluntary playback separately from automatic start. Reduced motion can leave a Play action available while preventing progression the reader did not request. Verify that manual choices still update their caption and media, and that a usable still remains when motion is absent. Restore temporary browser and system settings after testing.

## Validate what readers experience

For the scenes actually implemented, inspect:

- A settled beginning and end, plus at least one meaningful intermediate state.
- Fast and reverse scrolling, direct anchors, and restored scroll position.
- Wide and narrow layouts, short viewport height, and enlarged text.
- Reduced motion and the relevant asset-failure path.
- Keyboard access to playback and any controls within the scene.

A screenshot captured halfway through an entrance does not establish final contrast. A reduced-motion branch found in source does not establish that its layout works. Record source findings and observed runtime results separately, and name any conditions that remain untested.
