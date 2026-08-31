# Technical writing

Use this reference for user-facing technical documentation: READMEs, guides,
tutorials, API concepts, troubleshooting material, and release documentation.
Apply the communication rules in `AGENTS.md` first. Preserve exact project
terms, public identifiers, UI text, templates, and required formats.

## Shape the document around the reader's task

- State the purpose, outcome, and necessary scope before supporting detail.
- Put prerequisites and conditions before the action that depends on them.
- Use task-based headings that start with a base-form verb and concept headings
  that use a clear noun phrase.
- Keep one page title and a semantic heading hierarchy. Do not skip levels.
- Provide essential context in place. Link only when the destination adds useful
  detail, and write link text that identifies that detail out of context. State
  when a link downloads a file or has another unexpected result.
- Remove previews that only announce what the next sentence or section says.

## Write procedures that can be followed

- Introduce a multi-step procedure only when the reader needs context beyond the
  heading. State the goal instead of repeating the heading.
- Use numbered steps for a sequence and one primary action per step. Use a bullet
  for a single-step procedure.
- Start steps with an imperative. Put explanations, expected output, and results
  directly after the action they qualify.
- Mark optional steps at the start. Separate alternative procedures by heading,
  and lead with the shortest accessible method that fits the audience.
- Keep commands, output, and placeholder explanations adjacent. Define each
  placeholder where the reader first uses it.
- End with a result the reader can observe or a check that confirms completion.

## Make technical content unambiguous

- Use inline code for text that the reader types verbatim and for identifiers
  such as commands, options, paths, filenames, types, methods, and values.
- Use fenced blocks for commands, code, and output that readers need to copy or
  distinguish from prose. Label the language when it is known.
- Follow the product's convention for UI controls. When none exists, use bold
  text for visible labels and preserve their exact capitalization.
- Define an acronym on first use unless the audience and project treat it as a
  standard term. Use one term for one concept.
- Use explicit dates, units, and version bounds when another locale or point in
  time could change the meaning.
- Use reserved example domains and fictional data. Never put real credentials,
  personal data, internal hosts, or sensitive URLs in examples.

## Keep the content accessible and global

- Use a natural, respectful tone without slang or filler such as "please note"
  or "let's." Keep the information more prominent than the writer's personality.
- Use literal language that translates cleanly. Avoid idioms, cultural
  references, humor that carries meaning, and unexplained regional terms.
- Put distinguishing information early in paragraphs, list items, headings, and
  links so readers can scan efficiently.
- Keep list items parallel. Use tables only for genuinely relational data, not
  to simulate layout.
- Give informative images concise alt text that states their purpose. Use empty
  alt text for decorative images, and provide the same essential information in
  text rather than relying on an image, color, direction, or position alone.
- Prefer text and semantic markup over screenshots of text, code, or terminal
  output. Ensure procedures have a keyboard-accessible path when one exists.

## Review before publication

Confirm that:

- the title, opening, and headings expose the document's purpose and route;
- every prerequisite, step, command, placeholder, and expected result is in the
  order the reader needs it;
- links, images, tables, and examples remain understandable without visual-only
  or private context;
- terminology and formatting match the project and the documented interface;
- claims reflect evidence and include the version or condition that bounds them.

## Source and maintenance

This reference adapts reusable guidance from the
[Google developer documentation style guide](https://developers.google.com/style),
especially its guidance on [voice and tone](https://developers.google.com/style/tone),
[global audiences](https://developers.google.com/style/translation),
[accessibility](https://developers.google.com/style/accessibility),
[procedures](https://developers.google.com/style/procedures),
[headings](https://developers.google.com/style/headings),
[links](https://developers.google.com/style/cross-references), and
[code in text](https://developers.google.com/style/code-in-text), with its
[example-data guidance](https://developers.google.com/style/examples). The Google
guide is licensed under CC BY 4.0; this file paraphrases and narrows it for the
kit instead of reproducing it. Sources were reviewed on 2026-08-31. Recheck the
upstream guide when this reference changes or when its requirements conflict
with current project practice.
