# Craft system

Use this reference to decide how type and images work together, what to emphasise or keep secondary, what to repeat or vary, and how much content and space each part needs. Base those choices on the established product character and the purpose of each scene. Use `product-storytelling` when you need to develop the campaign identity or decide what the imagery should communicate.

## Compose a scene

Decide what readers should notice first and where they should look next. A large object and a short headline can have equal visual weight. A technical detail may need a smaller heading and a very large crop. You do not need a hero image in every section. Judge the balance of the arrangement rather than aiming to give the product a fixed percentage of the space.

Place related elements close together, align elements to connect them across the page, and use contrast to show their relative importance. Check that these relationships remain clear when you view the page at reduced scale. Then inspect it at reading size. Check line breaks, the distance between captions and their subjects, optical alignment, and whether the important image detail is legible; each can affect how well the composition works.

Align the visible content as well as the element boxes. Transparent image margins, an icon's shape or an uneven crop can make objects look disconnected even when their boxes align. Make adjustments within a consistent grid and inspect the result with the real assets. Avoid compensating with arbitrary offsets at every breakpoint.

Subdued surrounding surfaces usually help the product stand out. Expressive typography or the scene's atmosphere can also attract attention first. Decide which element should be the focus and which elements support it. Avoid making the headline, image, controls and surface treatment all demand equal attention.

## Typography as voice and hierarchy

Choose a small set of recurring type sizes that are different enough to make the hierarchy clear. Roughly three or four sizes can be a useful starting point for a scene: one for the main point, one for supporting copy, and perhaps others for controls or a necessary annotation. Adjust this starting point to suit the scene; it is not a limit for the whole work. A diagram or a more expressive part of the scene may need more sizes. Each extra size should distinguish something useful.

| Role | Purpose | What to inspect |
| --- | --- | --- |
| Statement or headline | Establish the main point or invitation | Overall text shape and size, line breaks, tone, and the relationship to the image |
| Section or group heading | Introduce a new subject or collection | Whether the heading makes the change of subject clear without drawing excessive attention to itself |
| Intro or continuation | Develop the point | Line length and contrast that make closer reading comfortable without making the text faint |
| Body or caption | Explain, identify or reassure | Comfortable reading and clear association with its subject |
| Figure | Draw attention to a quantity or comparison | Meaningful labels, units and baselines as well as size |
| Label or qualification | Supply context or a condition | Enough visibility for its importance; essential conditions cannot disappear into fine print |

Several semantic roles can share a size. Before adding another small size variation, try distinguishing them through weight, contrast, placement or proximity. Inspect the whole scene, including labels and controls, for text treatments that compete for attention. Preserve the typography of any product interface you demonstrate and keep the surrounding marketing hierarchy restrained.

Use a cohesive set of font families and weights. One family can provide a varied hierarchy; give each additional family a clear role. Choose tracking and leading for the actual typeface, size, case and line lengths. Tight spacing can give a short line of display text more emphasis, but increasing the type size does not always call for tighter spacing.

Use fonts you are entitled to use and inspect how they render. `system-ui, sans-serif` is a sufficient dependency-free starting point; an installed or licensed typeface may better suit the design. Check fallback rendering and layout shifts during loading on supported platforms. A family name alone does not guarantee the result.

Try balanced wrapping for short display text when it improves the text's overall shape. Inspect the result across widths. Do not hard-code a desktop line break that disrupts the mobile reading order, and preserve spaces between words when responsive line breaks disappear. Keep ordinary reading text at a comfortable line length and inspect it in fallback fonts as well as the preferred font.

### Assertion and continuation

A dark main statement followed by a grey continuation can support both scanning and closer reading within one heading or paragraph. Readers can scan the statement for the main point, then read the continuation for more detail. Bright text followed by muted text can do the same job on a dark surface. Divide the text at a meaningful boundary, rather than at whichever words happen to wrap onto line two.

Use this treatment when the writing benefits from separating a main statement from its continuation. Elsewhere, a single plain headline or a separate paragraph may work better. Do not invent a second sentence to obtain the treatment, repeat it in every scene, or make essential information so faint that it becomes decoration. Both parts need adequate contrast at their actual size and weight. Preserve their meaning and word spacing as lines reflow. Colour must not be the only way to communicate an essential distinction.

### Captions and emphasis

Many images need no caption. When one helps, a bold lead-in followed by a less prominent explanation can give readers a quick label to scan and more detail to read. For example: "**Scheduled export.** Pick a time and the file is ready when you arrive." Another image may work better with a plain caption, a separate label, or no caption. Place overlay text in a suitable part of the image and maintain reliable contrast across states and crops.

Callout numbers, letters and icons can help connect an explanation to a visible feature, state or meaningful sequence. Make the connection clear in the image, including at smaller sizes. A marker before a line of prose adds little when there is nothing to locate or follow. Give comparable images the captions they need; if the caption treatments differ, the reader should be able to understand why.

Emphasise selectively. Read the emphasised phrases alone to check whether they draw attention to the right things; they do not need to form a second complete sentence. Use semantic emphasis where warranted and a styled span for a purely visual distinction.

## Colour and surfaces

Assign recurring colours to clear roles, such as primary and secondary text, page surfaces, controls and intentional accents. Use those roles consistently so departures from them have meaning. If a colour identifies something meaningful in the product, you can use it with the same meaning across imagery, interface and any recurring motif. Keep it out of unrelated chrome so the connection remains clear. A change of surface can signal a new chapter, group related details or shift the mood. Alternating light and dark bands at regular intervals adds little by itself.

Keep muted text readable on its actual background at its actual size and weight. Small secondary labels need contrast too. Check overlays, transparency and gradients against their rendered backgrounds. Aesthetic choices do not exempt text from contrast requirements. Do not rely on colour alone to convey an essential difference.

Gradients, shadows, textures and vivid accents are options when they support the design direction. Consider what each treatment adds to the composition and how much attention it draws. Refining a borrowed glow around weak content is unlikely to improve the content itself.

## Space, rhythm and layout

Use different amounts of space within a group and between groups. Keep a headline close enough to its explanation that readers see the connection; leave more space before the next chapter when it needs a pause. Large empty areas can create anticipation or give readers time to notice an object. Reduce the space if the scene gives them no reason to pause.

A repeated arrangement can help readers follow changes in screens or states. Keep the arrangement where familiarity helps, and change its scale or density when the emphasis changes. Major demonstrations, cropped details, compact inventories and a quiet closing scene can share the same visual language.

Choose widths that let readers view the content usefully, and place breakpoints where the composition no longer fits. A tall interface may work beside copy; a broad physical transformation may need the full width. Rearrange the composition for small screens instead of shrinking every element together. Choose an arrangement for each scene while retaining the relationships that connect it to the rest of the page.

If the page will be translated or shown in a right-to-left language, check that longer text still fits and that mirrored layouts keep each image next to the copy that explains it. Directional controls, arrows and progress should follow the reading direction.

## Surfaces and controls

Use cards when boundaries help group, compare or contain content. A plain section or list may need no surface. Choose tile proportions to suit the content: a comparison, a screenshot, a figure group and a short fact will not necessarily need the same shape. Keep repeated chrome less prominent than the content it contains.

Give actions a recognisable hierarchy, a clear destination and a comfortable target. A roughly 44px touch target is a useful starting point; small visible icons can have larger hit areas. Place gallery controls where they are comfortable to use and clearly belong to the content they control. When you copy a control's appearance, preserve its state and keyboard behaviour too. Keep decorative markers, bullets and step glyphs from looking like checkboxes, arrows or buttons.

Local navigation can help readers stay oriented and reach the main action. Keep its surface proportionate to the content and available space. Decide whether to include it, make it translucent or shrink it on scroll according to the design; none of these is required for this visual direction. If a bar or overlay is translucent, provide a more opaque, higher-contrast version for readers who ask for reduced transparency or increased contrast, and check text over the busiest imagery it can cover.

## Choose a presentation pattern

Use [Reusable web patterns](web-patterns.md) when product staging, a stable demonstration frame, a close-up, a comparison, a compact overview or optional detail would help answer a known reader question. Select and adapt only what the story needs. Use the pattern names to discuss the design, rather than as public headings or an ordered page plan.

## Image quality

Represent the product with consistent geometry, finish and relevant UI. Choose lighting, framing, setting and detail to suit the scene's purpose. A dark screen, posed portrait, illustration or isolated object can each be a deliberate choice. When demonstrating an interface, show credible content and enough legible context to understand the action.

Choose responsive crops deliberately. A wider view may establish context while a close view explains the important detail. If a chart, timeline or dense interface becomes unreadable at narrow widths, showing a smaller range is one option. Preserve the full context or range when readers need it to understand the comparison or claim, and identify the visible range whenever you crop it. Repeating a view can establish familiarity or enable comparison; each repetition does not need to show a new feature. Keep controls, annotations and the details they identify visible together. When producing assets or changing what the imagery should communicate, use the approved art direction or develop it with `product-storytelling`.

## Motion calibration

Choose motion according to the relationship it helps explain or the feeling it adds. Brief state feedback usually needs less time than a large spatial transition; reading a caption needs longer than either. As a starting point, a compact update might take around 150 to 250ms and a larger fade or reveal around 400 to 700ms. Adjust the distance, easing and content together. These durations are examples, not brand constants or minimums.

Immediate changes and static scenes are valid choices. In the reduced-motion version, preserve useful states and relationships. One still may be enough, or a change may need a labeled sequence to explain it. Removing movement must not remove the explanation or leave empty scroll space. Give users appropriate control over time-based media. [Scroll and motion](scroll-and-motion.md) covers implementation and verification.
