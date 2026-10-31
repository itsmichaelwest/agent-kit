# Static and interactive slide decks

Keep the main promise, character and facts about the product consistent across formats. Compose the deck for its audience and setting. It may devote different amounts of attention to anticipation, explanation, demonstration and pauses than the website does. Use [Narrative strategy](narrative-strategy.md) for the argument and [Story development](story-development.md) for reveals and campaign context.

## Choose the delivery mode

| Mode | What the audience has | Design implication |
| --- | --- | --- |
| Speaker-led | A presenter supplying explanation and timing | Keep slides focused on the visible argument; put delivery cues and supporting detail in speaker notes |
| Self-paced static | Slides or a PDF without a presenter | Supply enough visible explanation, definitions, and qualifications to understand each claim independently |
| Self-paced interactive | A navigable presentation with optional detail or demonstrations | Provide a coherent default route, orientation, explicit controls, and a route back from branches |
| Combined | A live presentation plus a leave-behind | Preserve the shared argument but adapt explanatory detail; do not assume speaker notes survive export |

Use the brief to confirm or infer the intended audience, viewing context, output format, aspect ratio, and delivery mode. Ask only when a missing choice materially affects the result. Static slides may still contain links. Adding links does not make an otherwise incomplete argument suitable for self-paced viewing. Do not build a web application merely because the brief calls the deck interactive.

## Sequence the argument

For a substantial new deck, briefly map out each slide's purpose and how it leads to the next. A slide can introduce, explain, compare, build anticipation or let an idea settle. Give it a clear centre of attention. A comparison may need several related facts. Avoid fixed slide counts, arbitrary word limits, and mandatory problem-and-solution plots.

Write titles that advance the story. A section divider can name a topic when the audience needs orientation, but a small label above each slide title usually repeats it. The audience should be able to follow the main argument from the sequence of titles and images. Distinguish a supported conclusion from an evocative headline. Place qualifications that affect a claim beside it. Do not hide them in notes or an appendix.

Use an overview when it helps people understand the route. Move specialist detail into an appendix or a clearly labeled branch when it would interrupt the main argument. Keep buying or adoption constraints on the main route. End with a decision or next step appropriate to the presentation. A generic closing slogan does not provide that direction.

## Compose for the canvas

Apply the chosen [identity](identity.md) to the slide canvas, and plan scenes and imagery with [Visual direction](visual-direction.md). Use the presentation tools and format-specific guide appropriate to the requested output. Text fitting on the slides and a successful export are only part of finishing a deck.

Choose proportions to suit the viewing distance, delivery mode and content:

- Canvas: margins can give an object presence or help viewers see related parts as a group. Full bleed may better serve another moment. Keep the prominence of navigation, numbering and persistent identity elements proportionate to their use.
- Type: judge hierarchy and legibility at the actual viewing size. On a 1920×1080 canvas, a 120px statement is a possible starting point, not a target. Projection and close reading need different supporting text sizes and density. A minimum pixel size alone cannot establish readability.
- Composition: an isolated phrase, an expansive image, a matched pair, a diagram or a compact overview can each carry a moment. Make visual priorities clear so viewers can connect the parts. Do not require one object or fact per slide.
- Product imagery: preserve the product's identity while choosing crops and lighting for each scene. The deck may need a closer crop than the website. It can share the campaign's character without repeating all its images.
- Figures: make the number, units, qualifier and baseline readable, with their relationship clear. Displaying a number in large type can create emphasis; a table or chart may make comparison easier.
- Builds and transitions: choose continuity or a deliberate break. A cut can make a change of subject more pronounced, while a matched transition can preserve a relationship. Reveal a meaningful group together when separating its elements would obscure the point. Set the timing to suit the movement and give the audience an opportunity to read.

Make the main idea and its supporting information easy to distinguish. Keep both readable at the expected viewing distance. Use a compact overview or appendix to show the breadth of supporting features. Not every small feature needs a full dramatic scene.

Give each slide a clear focal point and keep alignment, type roles and margins stable across the deck. Vary the composition to suit the content: a result, an object detail, a workflow and a qualified comparison need different treatments. Do not decorate every slide with the same card grid.

Use product imagery to explain scale, construction, output, or use. Crop interface screenshots around the relevant action while retaining enough context to avoid implying a different workflow. Charts need legible units, baselines, labels, and source context. Do not shrink an entire webpage or dense dashboard until it fits.

Check text and diagram legibility at the expected viewing size. Projection needs a different density from a document read close up. If a slide is overloaded, split it or move optional detail instead of silently reducing type. Where the format supports them, preserve editable text and meaningful reading order. Add useful media alternatives, and do not communicate essential differences through color alone.

## Make builds and interaction serve understanding

A build can reveal a relationship, explain a transformation, focus attention or use timing expressively. Identify the useful states where it can pause, and keep labels, captions and visible product states synchronized. Use decorative movement selectively. Repeated entrances and compulsory waits can interrupt the argument.

For an interactive deck, specify the default sequence and each optional branch. Make previous/next controls easy to find, show the current location, and provide a clear return path. Keep a linear route that communicates the essential story without visiting every branch. Do not let a visitor return from a branch without the prerequisites for continuing or with an unexplained change of selection.

Use keyboard-accessible controls and visible focus in runtimes that support them. When the slide changes, move focus to the new slide's heading or otherwise announce the change, and show the new slide from its top. Keep navigation shortcuts from conflicting with text fields, media controls, or dialogs. Swipe and hover cannot be the only way to discover information. A comparison selector must update its labels and evidence together. A simulated product interaction must not imply a real transaction or live result.

Provide pause/replay for relevant media and a meaningful still or text explanation when it cannot play. In browser-based decks, inspect reduced-motion behavior, including slide transitions and animated charts. In other formats, verify the actual viewer's capabilities and supply a usable static version when motion is essential to the original treatment. Settings in the source do not prove how a viewer behaves.

## Preserve meaning in static output

Choose how to represent the presentation in static form. A build that adds content at each step can export its complete state. Mutually exclusive states may need separate slides or a labeled comparison. A final frame alone is insufficient when the point is a change over time. Preserve the sequence or explain the change in a diagram.

When a linear export is a requested deliverable, include essential branch content and media explanations. Carry sources and qualifications into that version. Links may supplement the PDF or printed deck, but the audience should not need them to understand its central claim. Do not assume animations, embedded video, scripts, notes, or navigation survive conversion.

## Inspect the delivered format

Render and review every slide for clipping, overlap, font substitution, contrast, and legibility. Read the deck in sequence without relying on its authoring context. Check that transitions do not imply an unsupported connection. For a speaker-led deck, inspect notes separately from the claims visible to the audience.

For interactive delivery, exercise the default route, branches, return paths, first and last slides, keyboard operation, and media fallback in the intended runtime. In a browser-based deck, also load it with scripts disabled or failing: the default route should remain readable in order. Check supported small-screen behavior. Use a readable reflow or a deliberately scaled presentation with usable controls; do not assume a desktop canvas is usable on a phone.

Open the actual requested export and inspect it independently of the source. Confirm that essential states, media explanations, sources, and qualifications survived. Report which runtime and exports were checked and any limitations. Do not claim a presentation file works in every viewer based on one preview.
