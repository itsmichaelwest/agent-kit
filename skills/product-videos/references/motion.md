# Construct motion that communicates

## Set the cadence of understanding

Author the order and timing of the viewer's discoveries before assigning durations to implementation steps. A launch passage may establish its proposition quickly, then develop its shape and emphasis. A tutorial may need separate time for approach, selection, confirmation and consequence. Do not let a launch passage inherit tutorial pacing merely because each interface operation has its own animation function.

For each phrase, distinguish the point when its composition becomes recognizable from the point when its movement finishes. New content can become readable while its proportions, spacing and weight continue to develop. The next addition can interrupt that development, or a complete statement can hold still. Decide this at phrase level; making every object enter, settle and hold in sequence often obscures the larger rhythm.

When the direction calls for expressive reflow, compose the whole frame before and after each addition. Decide which existing subject yields space, changes rank, persists or disappears. Filling a reserved empty slot animates content without necessarily changing the composition. Choose the relationship the passage needs. Shared boundaries let an incoming word change the space available to existing words and keep their movements related.

Inspect the first readable frame, the next major compositional change and what develops between them. Shortening a slow passage is not enough if its meaning still arrives late. Remove redundant explanation or change the hierarchy when that is the cause. Do not turn one successful excerpt's timing into a universal frame count, or replace a static hold with imperceptible decorative drift.

## Separate the times inside an event

An event can contain action, recognition, settling, reading and camera movement on different schedules. Action is the travel or change that does the work. Recognition is the first point where the intended relationship becomes clear. Settling is any residual movement after arrival. Reading or comparison gives the viewer time to understand the result. A shot can continue through all of them.

These intervals can overlap. A new word may arrive while an existing word gains weight; an interface state can become readable while its presentation camera continues moving. Use a pause when understanding or anticipation needs it, and decide what holds the viewer's interest during that interval.

For a complex event, write a compact ledger with output frame rate, event boundaries, recognition, overlap, sound cue and reason. Keep times in seconds and output frames. At a new delivery rate, preserve intended time or deliberately redesign exposure; frame counts alone do not transfer cadence.

## Shape force and arrival

Specify the start and end geometry, anchor, path and travel distance before choosing an easing function. Decide where visible acceleration begins, where speed peaks, how the object brakes and whether a settle belongs to its character. Different properties can use different schedules. Position may arrive while weight, reflection or focus continues changing.

| Intended behavior | Construction choice | Check in the output |
| --- | --- | --- |
| Immediate emphasis | Cut, discrete replacement or rapid reframe | The new relationship is understandable; missing intermediate states are intentional. |
| Decisive arrival | Concentrated travel followed by designed braking | Acceleration and braking remain visible at delivery cadence; the tail earns its time. |
| Gathering force | Visible acceleration before the main travel | The acceleration is not hidden before the object enters the frame. |
| Mechanical explanation | Coherent path, pivot and endpoint views | Contacts, dimensions and orientations remain plausible. |
| Changing identity | Authored contour landmarks and intermediate shapes | Holes, corners, strokes and recognition change deliberately. |
| Steady observation | Linear or near-linear traversal where appropriate | Apparent screen speed suits the camera and perspective. |

A named ease implements a chosen movement. Decide whether the shot calls for linear travel, overshoot or a hard stop. Add bounce only when it serves that choice, and preserve deliberately discontinuous edits.

Evaluate the movement of the leading image as well as the fastest object. A strongly accelerated small peripheral element can leave the dominant composition inert. Track changes to the main subject's silhouette, scale, hierarchy, available space or meaning. An expressive reference may owe its force to those changes as much as its easing. Preserve that relationship when changing the treatment. Incidental motion cannot compensate for an inert central image, though a purposeful still image can suit the brief and sequence.

Inspect actual sampled motion. For position `x[n]`, record `x[n] - x[n-1]`; inspect the corresponding edges in rendered frames. An apparently eased move may spend almost all its travel before its first readable sample. A long series of tiny deltas can produce inert drift. When motion feels slow, distinguish weak initial travel, a long tail, empty waiting and a late next action; repair the specific delay.

For large scale changes, inspect proportional change as well as pixel travel. `log(s[n] / s[n-1])` describes the frame-to-frame scale ratio. Interpolating raw scale across coarse linear keys can create an increasingly abrupt contraction near the endpoint. For a perceptually paced scale move, evaluate `s(t) = exp(lerp(log(s0), log(s1), p(t)))`, where the authored progress `p(t)` controls acceleration and braking. Test whether this model suits the shot. Inspect the combined movement of visible edges, subject and camera, especially the final moving samples. Choose the focal anchor deliberately.

Blur can support continuity when it matches exposure, direction and speed. It cannot repair a wrong path, missing product state or poorly placed stop. Judge the clear pose and motion before adding finishing effects.

## Choreograph shared space

Use anchors that help the viewer follow change: a word, boundary, face, cursor target, product edge or stable region. Persistent elements need not replay entrances whenever another element appears.

Derive related geometry from a shared state. If a panel expands and text makes room, calculate both from the same edge. Reveal text as the space becomes available; measure actual extents and inspect moving intersections. Collisions can occur between clean endpoint poses. Keep intentional overlap and cropping when they preserve the required meaning.

When a container resizes ahead of its contents, anchor content to the current edge plus an authored margin instead of interpolating absolute endpoints on delayed curves. Inspect neighboring baselines together: saving a footer from clipping can push it into a headline. For responsive lettering, derive the available width from the current frame and solve the letter geometry within it; let intentional changes of weight or spacing retain their own timing.

Choose the timing relationship between elements. Simultaneous movement can make a system read as one, while a leader and response can establish cause. An interruption can create emphasis. Properties that move together can still have different timing; decide which one leads instead of slowing every secondary element.

## Give edits and camera moves a purpose

At each cut, state what changes in the viewer's understanding and where attention lands. A closer view can establish new detail; a larger word changes emphasis. A discontinuity can supply punctuation. Enlarging an existing control can repair legibility without improving the edit. Consider giving the action enough screen space from its first appearance, avoiding a barely exposed wide shot followed by a rescue cut.

Trace the important subject's screen position through the entire transition, combining its motion with the camera. Check for detours: returning to a wide view, moving the subject across the frame, then immediately reversing toward its next role. If the restored context has no new purpose, connect the action directly to the next composition. A well-braked camera move can still be an unnecessary move.

Check the time available to recognize the outgoing composition. Completing a reflow immediately before cutting away can waste its arrival; interrupting it can also be intentional when the next image completes the thought. Judge the relationship across the boundary; two shots that each work alone can still join badly.

## Build expressive type as lettering

Compose the actual phrase before animating it. Establish cap height or x-height, baseline, stroke character, counters, optical spacing, line breaks and important crops. Decide which typographic properties express the thought and which should remain stable.

When width, weight and spacing change, give them distinct controls. Changing a variable font's width axis can alter glyph design; changing weight can alter stems and counters; tracking changes relationships between letters. Scaling a fixed text rectangle changes these properties together and cannot substitute for independent lettering decisions. Deliberate distortion is still available when its visual character is intended.

For a variable-font construction:

1. Verify the actual font file, supported axes and output renderer. Do not assume a CSS request selected the intended face or that an unsupported axis changed the outlines.
2. Shape the whole word with native kerning and preserve glyph positions. Add authored tracking or per-glyph offsets deliberately, respecting shaped clusters and ligatures. A zero-valued kerning override can differ from leaving native kerning enabled.
3. Anchor to a shared baseline and cap height when those relationships should persist. Use actual ink bounds to inspect alignment, overshoot and clipping; fitting every glyph to its own box can erase the typeface's proportions.
4. Author width, weight, spacing and layout trajectories against the surrounding image. Weight can continue after position arrives; a neighbor can retreat while letters expand. Weight changes may also change width, so derive a shared boundary from the actual shaped extent when it must stay aligned. Inspect counters and negative space throughout.
5. Render important poses and consecutive motion frames. If exporting outlines, either generate each sampled font state or verify compatible contour topology before interpolation. Equal character counts do not establish compatible paths.

A font-outline exporter, variable text layer or authored vector rig can all work. Choose a method supported by the production environment that preserves the controls this passage needs. Do not hide the difficult construction behind an instruction to “morph the text” without defining landmarks, topology or how the output is produced.

The [original variable-type example](variable-type-example.md) explains the independent controls and includes an optional dependency-free TypeScript helper for sampled outlines. Its input requirements and shaping and interpolation limits are explicit.

For restrained type, expression can come from selective additions, substitutions, removals and hierarchy. Keep a stable word or baseline when it supports continuity. Check intermediate phrases: replacing a verb before its object can briefly reverse a promise. A whole-phrase cut may communicate better than a letter-by-letter transition.

Direct a fill's light, texture scale, contrast and movement relative to the letterforms. A material or illumination change may continue after the silhouette settles. Inspect counters, edges and legibility. A generic gradient does not by itself show surface craft.

## Preserve product truth during motion

For UI, derive visible results from the same action model. A duration should control its label and represented span; selected content should determine the visible output. Keep dates, quantities and states consistent across shots. Show cause when viewers need to understand the workflow; a pointer is optional, but an unexplained result can weaken the demonstration.

When the product produces sound, derive visible notes, playback indicators, mute states and audible events from the same product data. Distinguish recording or entry from playback: a replayed note can light without showing another input gesture. Keep editorial stings and interface feedback identifiable as separate cues so they do not misrepresent the demonstrated output.

Keep editorial frame times separate from product times and quantities. Retiming a reveal must not change a meeting's end hour, a purchase amount or a demonstrated duration. Scope timing edits to the event model, then recheck the product invariants and decoded frames; a valid render can still display corrupted data.

Distinguish product behavior from editorial presentation. Cropping or moving a whole screen in the film does not imply that the application performs that movement. If a diagram simplifies a system, preserve the relationships needed for the claim.

For physical subjects, preserve identity, scale, geometry, contact, material response and direction of movement. Give a mechanical explanation accurate pivots and connected parts. Identify unverified internals as missing evidence; do not invent their engineering. Recheck these details during fast motion, occlusion and cut boundaries as well as in the hero pose.
