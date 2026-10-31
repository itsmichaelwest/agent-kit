# Product web patterns

Use this reference to choose how a product-marketing page presents evidence. Start with the reader's unanswered question and the material available to answer it. Combine, repeat or omit patterns to suit the story. Their order here does not prescribe a page sequence. Reusing a useful frame can make changes in product content easier to understand.

These patterns cover composition. Use the [craft system](craft-system.md) for visual relationships, [interactive elements](interactive-elements.md) for control and state contracts, and [scroll and motion](scroll-and-motion.md) for movement, timing, media and fallback implementation.

## What is this? Product stages and device framing

A product stage places an object or interface in enough context to show its form, scale and use. A portrait screen may fit beside its explanation; a broad physical object may need uninterrupted horizontal space. A device bezel helps when platform, handling or input matters. Once readers have that context, a direct crop of the interface can be clearer.

Choose surroundings that relate to the subject. The surface may echo a product material or the atmosphere of its interface. Use lighting and viewpoint to clarify the product's form.

On narrow screens, reconsider the image crop and copy order together. Preserve the part that identifies the product and the detail that supports the promised benefit. Show a useful product view in the static opening, before any reveal or playback begins.

## What happens during use? Stable frames and changing states

Keep the device, viewpoint, scale or surrounding workspace steady while changing a meaningful product state. Familiar surroundings help readers focus on the action and its consequence. You can use this approach across consecutive chapters or within a selected demonstration.

Use actual supported states or approved concept behavior. Each screen should show the relevant task or result; a new label over unchanged imagery adds little. Give each example the explanation it needs. Different tasks can share a frame without being presented as a before/after comparison.

On narrow screens, keep the result readable and its selector nearby. A static sequence or manually selected states can preserve the same explanation without automatic playback. See [product viewers](interactive-elements.md#product-viewers-finishes-and-detail-panes) for coordinated selections.

## Where should I look? Selective crops and linked annotation

Crop around the feature being discussed. Lower controls, an upper status area and a material joint may each require different framing. Keep enough surrounding context for readers to locate the detail. Return to a wider view when they can no longer see how the detail fits into the whole.

Connect an explanation to its visible subject by placing them close together, naming a selection or, when needed, using a marker or leader line. Each annotation should locate or explain something. Add a caption when the image needs identification or explanation; a self-explanatory image may stand alone.

On narrow screens, move crowded annotations beneath the image or separate the views. Keep it clear which annotation belongs to which detail. A static view must preserve these connections for essential labels without requiring hover or an exact scroll position.

## What difference does this choice make? Matched comparisons

Keep the subject, crop, scale and relevant conditions steady while changing the named variable. Matching the position of corresponding details lets readers inspect the consequence without having to reconstruct two unrelated scenes. A comparison may concern an output, setting or intervention; name the distinction in its controls.

Keep the baseline and any condition that changes the claim's meaning near the result. A clear visual difference can explain an effect. Claims about measured performance still need their own evidence.

On narrow screens, a shared frame with a selector often preserves more detail than tiny images placed side by side. If readers need to compare views simultaneously, stack aligned views with clear labels. In the reduced-motion version, retain both choices and their meaning through direct selection or a labeled static pair. See the [matched-comparison contract](interactive-elements.md#matched-comparisons).

## How does it work? Connected evidence at different scales

Use this pattern when an important mechanism is hidden inside the object or behind its output, or when one view combines several inputs. Start with a recognizable product view, show the relevant structure, then show what that structure enables. Repeat a feature or shape so readers can follow the change of scale. Include only views that help them understand more. For a combined view, introduce the layers in one stable frame and finish with the combination the product actually shows.

A cutaway, diagram or short transformation can explain a mechanism. Numerical bounds and measured results provide a different kind of evidence and need their own stated conditions. Optional technical detail can extend the explanation without taking up the whole main scene.

On narrow or short screens, replace a spacious animated composition with readable stills or separately arranged details. The static version must show the causal relationship; an arbitrary frozen frame may not explain it. Use the [scene specification](scroll-and-motion.md#define-the-scene-before-implementing-it) when motion helps connect the views.

## What else can it do? Compact supporting breadth

Give the central promises enough room to show product evidence. Once the role of supporting capabilities is clear, present them in a denser group: cropped screenshots for visible details, icon-and-text rows for recognizable integrations, or a manual rail for independent examples. The amount of space each feature receives can show its importance while all features share the same visual language.

Use boundaries that reflect how the items relate. A shared panel can identify a family; open rows can keep a simple inventory visually light. If an item gives readers the main reason to choose the product, give its demonstration enough room outside the inventory.

On narrow screens, choose the arrangement separately for each group. Some cropped details remain useful in a compact grid, while longer explanations need rows. A rail needs a readable example and a visible indication that more content follows. Static content is usually sufficient. See [caption rails](interactive-elements.md#caption-rails) when browsing helps.

## Which benefits matter to me? Optional guided highlights

Highlights can provide an overview when several distinct benefits compete for a reader's interest. Give each topic its own useful demonstration. Keep the visual, explanation and selected topic together so readers can understand the current point and choose another.

A guided sequence helps when readers benefit from seeing the examples in succession. Otherwise, manual browsing may fit better. Keep the main argument understandable for readers who skip the gallery.

On narrow screens, keep the current example readable even if every topic cannot fit at once. When the topic names do not fit, let the strip scroll horizontally with a visible cue that more topics follow; avoid shortening or squeezing the names until they are hard to read. Static and reduced-motion presentations should retain topic choice and informative stills. Use the [timed-highlights contract](interactive-elements.md#timed-highlights) for playback, pause and reentry behavior.

## Where am I, and what detail can I reach? Orientation and depth

Local navigation helps readers move among substantial subjects or return to a decision. Keep the product identity, useful destinations and main action recognizable as the surrounding scenes change. Choose a compact bar or expanded exploration panel according to the page's actual complexity.

Place optional detail near the question that prompts it: a feature tour for inspection, a comparison for choice, a technical view for methodology, or a disclosure for an adoption question. Keep the main explanation complete on a first reading, with essential qualifications beside the claim.

On narrow screens, simplify the persistent navigation surface and use a readable vertical layout for deeper content. Keep ordinary links working and detail reachable without animated transitions. See [local navigation](interactive-elements.md#local-navigation-and-an-expanded-exploration-panel), [technical detail](interactive-elements.md#detailed-benchmarks-and-modals) and [disclosures](interactive-elements.md#faq-disclosures).

## What should I choose or do next? Optional decision support

Use this pattern when readers are ready to choose or need practical support before acting. Group established options and requirements with the next action the product actually offers. Place it where the question needs an answer, whether that is a closing scene or a decision point elsewhere on the page.

Keep the product's visual identity while shifting attention toward comparison and action. A quieter treatment or different density may make the change of task clearer. Present only supported availability, choices and destinations.

When readers choose among a few variants, an aligned set of specifications works well: the same attributes in matched rows, so each difference sits beside its counterpart. A short positioning line can distinguish each variant, and links can lead to fuller detail.

On narrow screens, keep each option's conditions and action together; do not separate all descriptions from all controls. If an aligned comparison no longer fits, let readers pick the variants to compare while keeping the same attribute order. Preserve these relationships in a static layout so readers can see the requirements and reach the action without motion.
