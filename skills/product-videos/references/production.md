# Choose a production method that supports revision

## Choose control from the shot

Identify what the shot must communicate, what must remain exact and one plausible late revision. Choose a method that exposes the controls needed to preserve identity and continuity through that revision. Inspect the resulting image for production quality.

| Shot requirement | Useful production control | Important inputs and limits |
| --- | --- | --- |
| Exact words, numbers, type or interface states | Authored motion graphics, a real UI capture, or a composite of both | Approved design, fonts and state sequence. A capture is a bounded take; an authored interface needs fidelity review. |
| Physical reveal, macro inspection or assembly | Filming or controlled 3D with separate object, camera, lighting and material controls | Verified geometry and surface references. An exterior model does not prove internal construction. |
| Human performance or use | Filmed takes with usable coverage and sound; exact screen replacements where needed | Contact, grip, action order and performance. Some changes require another take rather than an edit. |
| Impossible environment, material event or visual metaphor | Authored graphics, 3D/simulation or generated candidates, with exact product layers where needed | Defined meaning and endpoints. Inspect intermediate geometry, identity and continuity. |
| Coherent sequence and sound development | Editable assembly with shots, type and independent sound tracks | Original sources, cut points, cue versions and delivery requirements. A mixed file offers fewer controls than separated sources. |

Combine methods within a shot when each gives useful control over a different part of it.

## Discover usable capabilities

Inspect the available tools, local project and installed versions. Read the appropriate production guide when using a tool. Check which application features a connector exposes and whether the required project, scene connection and paid entitlement are available. An installed application may still lack any of these.

Use a focused trial when a capability is uncertain. Render or export a representative operation, inspect it and attempt the revision that matters. Record what worked and what remained fixed. Avoid a broad tool survey when the current shot already has a suitable, proven method.

Use [Tool selection](tool-selection.md) to find a missing control, a useful review capability or a way around a demonstrated limitation. Judge additional engines and effects by whether they help realize the direction.

## Preserve exact authored elements

For frame-driven graphics, derive animation from composition time so seeking and rendering produce the same state. Keep the product action model distinct from the editorial camera. Use named scenes, events and assets; make the properties likely to change accessible without building a general framework for one film.

For type, preserve font identity, shaping and actual bounds. For UI, use coherent sample data and the real relationship between action and result. A changed duration must update its label and represented span together. Capture the actual application when exact behavior is better demonstrated by a take; author components when their layout and timing need independent control and the representation can be verified.

For controlled 3D, retain a verified master asset and meaningful parts. Check the geometry, silhouette, spatial relationships and readability of the motion before costly finishing. Read [Controlled 3D product films](controlled-3d.md) for material, lighting, motion and render decisions at the scale the film will expose.

## Construct authored UI for the shot

Build the recognizable product context around the focal action. Preserve meaningful content, hierarchy and identity; simplify incidental detail without reducing the interface to anonymous boxes. Compose at the viewing size, with a deliberate crop and enough context to understand the result. Recompose for another aspect ratio when cropping would remove the cause or evidence.

When available, use `stageshow` for UI construction, measured interaction targets and rehearsal. Keep related elements continuous through a transformation: a container's changing bounds should govern its contents and neighbors, while lettering retains independent proportions and timing. Use a cursor when it makes the cause clearer, and derive its target from the current layout. A drawn click does not itself establish that the product state changed correctly.

Treat the kit's page-demo pacing, looping, entrance rules and example layouts as scoped choices. Author the shot's rhythm in the complete film: a decisive cut, immediate reveal or held result may serve it better than another animated entrance. Preserve the product's own visual identity. Reusable construction should support new compositions rather than reproduce an example's recognizable treatment.

Before committing a browser scene, verify how it reaches a requested time and exports media. The Stageshow version inspected on 2026-11-01 has a virtual clock for sequential stepping, but its `film.mjs` produces stills and contact sheets through wall-clock sampling, without finished video or audio export. Recheck the installed version. For film delivery, use a controlled sequential capture path or adapt the needed components to the film renderer; importing a stateful demo into Remotion does not make it frame-addressable.

## Keep one authoritative timeline

Make output time determine the picture and its related cues. A scene may calculate any frame directly, or reset to a known start and advance through fixed steps. Choose explicitly: forward stepping alone does not support arbitrary seeking, reverse review or parallel frame rendering. Do not let an independent browser timer, autoplay animation or unseeded simulation change the result.

For sequential capture, establish loaded fonts and assets, settled initial layout, viewport, visibility, time origin and random inputs before advancing. Save each intended frame after its updates complete. For an animation library, drive its supported timeline controls from output time; verify that callbacks and layout measurements reproduce the same state after a reset. Bake or cache simulation when it cannot be evaluated independently at each requested frame.

Check representative frames through both playback and the actual export route, including a repeated render or reset. Keep timing, source versions and approved parameter values with the edit so a live preview and an exported film use the same decisions. Reusable render mechanics can serve many films; scene order, copy, relationships and endings still belong to the individual brief.

## Plan filmed and generated media as shots

For footage, inspect the full take, usable in/out points, focus, exposure, continuity and sound. Choose coverage that supports the intended edit. A screen replacement needs appropriate perspective, occlusion and interaction timing; a clean insert alone does not establish believable contact.

For generated candidates, define the product details that cannot change and the elements open to interpretation. Inspect the entire shot, including fast motion and occlusion. Endpoints that match do not prove the path between them. Keep candidate versions and prompt/reference provenance in production notes. Do not promise independently editable objects, exact continuity or audio stems unless the actual output supplies them.

Use authorized assets and available generation capabilities. Keep source provenance and applicable usage conditions separate from public storytelling. A reference supplied for study is not automatically a release asset.

## Assemble and finish deliberately

Retain original media and editable project sources. Match frame cadence, dimensions, alpha treatment, color interpretation and audio timing across the handoff. Check which separate objects, masks, lighting controls and sound layers remain available; a high-resolution intermediate alone cannot supply them.

Check a representative round trip before committing a mixed pipeline. Include boundaries between transparent graphics, opaque cards and rendered footage: an image sequence can change pixel format partway through even when its dimensions stay constant. Normalize or explicitly handle those changes, and verify the exported tail. Look for color shifts, premultiplied-alpha fringes, softened type, duplicated frames, dropped frames, shifted trims and audio drift. Apply finishing at a point where it preserves the intended image and remains practical to revise.

Keep effects directed. Motion blur follows exposure and movement; texture has a scale and contrast; light changes describe a surface or emphasis. Check the clean construction before the final effect so finishing does not conceal a weak composition or broken boundary.

## Deliver what the user can review

Prepare playback in the requested form. If the user asks for a video file, produce the video rather than only an editor preview. Include the complete sequence and relevant sound, with a useful poster frame where supported. Preserve a version identifier so comments refer to the delivered edit.

Keep editable sources and required original assets organized for the next change. Identify temporary media, non-redistributable assets, unverified claims and remaining creative decisions in the handoff. Verify the exported file's picture, sound, duration and decode as well as editor playback.
