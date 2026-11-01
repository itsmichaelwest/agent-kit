# Construct variable letterforms

Use this original construction example when letter proportions, optical weight and spacing need to change independently. Its development film was rendered and technically inspected, then rejected by the user for slow pacing and awkward cuts. Use the code for its lettering controls, and do not treat the rejected film's direction as a template.

Use a variable text layer in the chosen renderer, or prepare font outlines with tools available in the production environment. The optional [TypeScript helper](../assets/variable-type.tsx) interpolates supplied outline samples and produces an SVG path. It has no operating-system, React or Remotion dependency, but it does not load fonts, shape text or generate its own samples. No font, reference footage, measured reference choreography or generated glyph data is included.

## Generate an original word

Use a font whose terms permit the intended output and verify its `wdth` and `wght` axes in the chosen renderer. Keep any optical-size axis fixed unless the treatment calls for it to change. Shape the complete word with native kerning before adding authored tracking. When the renderer can animate these controls and measure the resulting lettering directly, use that route without an outline-preparation step.

For sampled SVG outlines, prepare data matching `VariableTypeData` in the helper:

- Use one font face and a consistent coordinate scale. Supply sorted, distinct width and weight samples within the font's supported ranges, with at least two values per axis.
- Store each sample array in width-major order: `widthIndex * data.axes.wght.length + weightIndex`. Supply cap height, each glyph's coordinates, the shaped word's horizontal positions and its advance at every sample.
- Keep glyph contours and command order compatible across samples. The helper accepts `M`, `L`, `Q`, `C` and `Z` commands in font coordinates with a baseline origin and upward-positive Y; it converts them to SVG coordinates when placing the word.
- Use simple words with one glyph per character and horizontal placement. The helper indexes glyphs by character and cannot represent ligatures, contextual substitutions, cluster-dependent glyphs or vertical offsets. Reject fallback or missing outlines while preparing the data. Use the renderer's full shaping support for text outside those limits.

Compare interpolated cell midpoints with instances produced by the font renderer, including outlines, shaped positions, word advance and cap height. Add samples where the font changes rapidly along the intended trajectory. Control-point errors do not bound pixel or contour distance; inspect the rendered lettering too. A completed export can still contain samples too coarse for the shot.

## Animate independent controls

If using the helper, load the prepared data through your project's normal asset pipeline; it does not fetch a private location. With a grid that contains these values:

```tsx
import {wordAt, wordPath, type VariableTypeData} from './variable-type';

// data comes from your generated JSON. Each progress value is authored separately.
const focusPath = (
  data: VariableTypeData,
  widthProgress: number,
  weightProgress: number,
  spacingProgress: number,
) => wordPath(
  wordAt(data, 'FOCUS', 60 + 40 * widthProgress,
    400 + 400 * weightProgress, -12 + 12 * spacingProgress),
  {x: 960, baseline: 700, capHeight: 320, align: 'center'},
);
```

Render the returned string as an SVG `<path d={...}/>` with a chosen fill. Supply eased, frame-driven progress values from 0 to 1. Let width arrive, weight continue developing, and spacing compensate only when that sequence serves the shot. The baseline and cap height stay fixed here, while the native width and weight axes alter the letterforms. Tracking adds distance between already shaped glyphs and preserves native kerning. Choose timing and axis ranges for the shot and font; the example's numbers demonstrate how the controls work independently.

The helper computes tight quadratic and cubic Bézier bounds using derivative extrema and aligns to those curve bounds. The control-point hull would be larger. It rejects out-of-grid axis values instead of silently clamping them.

## Validate the passage

Compatible command sequences are necessary for this interpolation, but do not prove that bilinear samples reproduce every native instance. Axis mappings and intermediate masters can change rapidly within a cell. Refine sampling around the actual trajectory's troublesome regions, or bake native outlines at every output frame when exact native geometry matters.

Compare actual used widths, weights, spacing and cap heights against native instances. Inspect ink bounds, counters, shaped positions and consecutive-frame continuity at the final scale. A small average coordinate error can conceal a visible local error. Watch the rendered passage at normal speed before judging its motion, and keep the user's creative acceptance separate from mathematical and rendering checks.

## Build a shared composition from the lettering

Calculate the neighbor's boundary from the current word so their positions remain related. For example, a panel can follow the word's right ink edge:

```tsx
const word = wordAt(data, 'FOCUS', width, weight, tracking);
const scale = capHeight / word.capHeight;
const occupiedWidth = (word.bounds.maxX - word.bounds.minX) * scale;
const panelLeft = textLeft + occupiedWidth + gap;
const d = wordPath(word, {x: textLeft, baseline, capHeight, align: 'left'});
// Draw the panel at panelLeft, and the word with d. Both use this same frame state.
```

When the panel owns a fixed boundary, solve in the other direction: binary-search the width axis against `occupiedWidth`, holding the current weight, cap height and tracking fixed. Test the endpoints first. If the required span lies outside the font's width range, choose a different cap height, spacing or layout deliberately; avoid silently stretching the finished path. Recompute the word after the weight changes because weight can change its width too.

## Read the rendered development case

An original 14-second planning-film study used a day as a typographic composition. Each meeting occupied a fixed horizontal time band; its word stood vertically in that band. An existing free hour became a lit region, then the composition re-formed into a calendar. The hour eventually contracted into a letter of the product's wordmark. The calendar times stayed fixed throughout. This layout belongs to that study; choose a visual premise for the product at hand.

At 30 frames per second, the original construction used these relationships:

| Event | Authored behavior | What the construction establishes |
| --- | --- | --- |
| Meeting accumulation, frames 0–42 | Accelerating landings, independent native width fitting, weight 280→860, a short weight pulse at contact | The letters change proportions and density; parent scaling is not carrying the expression. |
| Focus lettering, frames 96–128 | The lit region already exists; width fitting and weight 1→780 develop on different curves | A visible result can gain character after it becomes recognizable. |
| Type to product, beginning at frame 130 | A spatial wave reduces vertical extent while each meeting keeps its horizontal time span | Shared geometry connects graphic metaphor to product evidence. |
| Product detail, frame 172 | A deliberate closer cut precedes the cursor and groups the control with its result | Closer framing helps legibility, but this cut follows a barely legible wide view and adds no new discovery. |
| Hour to wordmark, frames 314–356 | Width and height contract with an authored acceleration and brake; neighboring letters begin unfolding at frame 342 | Overlap gives the arrival a continuing purpose. |

The final contraction was checked in decoded frames: the highlighted shape changed from 210×545 pixels at frame 322, through 78×295 at 332 and 39×192 at 340, to 31×166 at both 355 and 356. Its replacement by the wordmark stem showed no observed position jump. These measurements describe this arrival; choosing a duration and judging creative quality require the surrounding sequence.

The user rejected the complete film's pace and cuts. Its technical checks did not predict creative success: a slow search preceded the proposition, the detail cut followed a barely exposed wide view, and the camera returned to context just before dismissing it. The agent had inspected rendered states, adjacent frames, geometry and technical audio measurements; those checks did not establish the complete motion or soundtrack experience. The helper was separately checked against shaped font data for positioning, curve bounds and independent controls. Use the [phrase and edit guidance](motion.md) to address these editorial decisions, and a different brief to test broader creative transfer.
