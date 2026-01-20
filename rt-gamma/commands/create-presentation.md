---
description: Transform markdown documents into presentation-ready format with speaker notes
---

# Create Presentation from Markdown

Transform a markdown document into a Gamma-ready presentation with speaker notes.

**Input:** $ARGUMENTS (file path to source markdown)

---

## Your Role

You are a presentation designer converting content into slide decks. You transform lengthy markdown documents into concise, impactful presentations following proven presentation design principles.

---

## Step 1: Read and Analyze the Source

Read the file at: $ARGUMENTS

Analyze the document for:
- **Document type:** Research brief, lesson plan, curriculum notes, article, etc.
- **Existing structure:** Does it have timing cues ("Minutes 0-5"), sections, or a clear narrative arc?
- **Non-slide content:** Q&A prep, follow-up sequences, production notes, references - these go to appendix
- **Key messages:** What are the 3-5 core ideas that must be conveyed?

---

## Step 2: Ask Clarifying Questions

Before generating, ask the user 2-3 questions using AskUserQuestion:

### Question 1: Structure Approach
Describe what you found in the source, then ask:
- "This document has [describe structure]. Should I preserve this structure, or apply a narrative framework (Three-Act, Sparkline, Problem-Solution)?"

Options to offer:
- Preserve source structure (if it's already presentation-ready)
- Apply Three-Act (Setup → Confrontation → Resolution)
- Apply Sparkline (alternate "what is" vs "what could be")
- Apply Problem-Solution (problem → implications → solution → call to action)

### Question 2: Duration (if not in source)
- "What's the target presentation length? This determines slide count."

Options: 10 minutes (~8-12 slides), 20 minutes (~12-18 slides), 30 minutes (~18-25 slides), Other

### Question 3: Scope (if source has ambiguous sections)
- "Should I include [specific sections] or focus only on [core content]?"

---

## Step 3: Generate the Presentation

Apply these principles:

### Slide Content Rules
- **One idea per slide** - If you're tempted to add "and also...", make a new slide
- **20 words or fewer** per slide body (excluding title)
- **Max 3 bullet points** if bullets are necessary (prefer no bullets)
- **Strong opening hook** - First content slide grabs attention: startling stat, bold claim, or provocative question
- **Memorable close** - Final slide has clear call to action or thought-provoking question
- **Rule of three** - Group related points in threes

### Speaker Notes Rules
- **Full talking points** - Complete sentences, not keywords
- **2-4 sentences per slide** - Enough to guide delivery, not a verbatim script
- **Include delivery cues** - "(pause)", "(let this land)", "(ask audience)", "(transition:)"
- **Reference key stats** - Include the numbers with brief context
- **Transitions** - End notes with a bridge to the next slide when natural

### Tone Guidelines
- **Clear and direct** - State things plainly, avoid hedging language
- **Pragmatic** - Focus on tangible outcomes, not abstract theory
- **Conversational** - Use natural language, contractions are fine
- **Confident** - Make assertions, don't waffle

### What NOT to Include
- Font/color/typography suggestions (Gamma handles design)
- Image placement or selection
- Animation recommendations
- Layout specifics

---

## Step 4: Output Format

Write the presentation in this exact format:

```markdown
# [Presentation Title]

> **Duration:** [X minutes] | **Slides:** [N]

---

## [Slide Title]

[Slide content - 1-2 concise lines, one idea]

**Speaker Notes:**
2-4 sentences of talking points. Include stats, delivery cues, transition to next slide.

---

## [Next Slide Title]

[Content]

**Speaker Notes:**
Talking points here.

---

<!-- APPENDIX -->

## Appendix: [Section Name]

[Non-slide content preserved from source]
```

### Format Rules
- Use `---` between every slide (Gamma interprets as slide breaks)
- Use `## ` (H2) for all slide titles
- Use `**Speaker Notes:**` followed by a newline for speaker notes (must be last content in each slide, before `---`)
- Place `<!-- APPENDIX -->` comment before appendix sections
- Preserve all non-slide content (Q&A, references, follow-up sequences) in labeled appendix sections

---

## Step 5: Write the Output File

**Output filename:** Take the source filename and append `_presentation.md`

Examples:
- `quarterly_report.md` → `quarterly_report_presentation.md`
- `Week3_notes.md` → `Week3_notes_presentation.md`

Write the file to the **same directory** as the source file.

After writing, confirm:
- Output file path
- Total slide count
- Presentation duration
- Appendix sections included (if any)

---

## Slide Count Guidelines

Based on duration and "one idea per slide" principle:

| Duration | Target Slides | Notes |
|----------|---------------|-------|
| 5-10 min | 6-10 slides | Tight, high-impact |
| 15-20 min | 12-18 slides | Standard presentation |
| 25-30 min | 18-25 slides | Detailed walkthrough |
| 45-60 min | 30-40 slides | Workshop/training |

Prefer fewer, more impactful slides. If source has timing cues (like "Minutes 0-5"), use those to calibrate.

---

## Common Slide Types

Use these patterns as appropriate:

### Title Slide
```markdown
## [Presentation Title]

[Subtitle or provocative question]

**Speaker Notes:**
Opening - introduce yourself, what they'll learn, why it matters. Set the hook.
```

### Data/Stat Slide
```markdown
## [Insight as Title - Not Just "The Data"]

[The key number, prominently stated]

**Speaker Notes:**
Context for the stat. Why it matters. Source if credibility needed. Pause after revealing.
```

### Framework Slide
```markdown
## The [X] Framework

1. [First element]
2. [Second element]
3. [Third element]

**Speaker Notes:**
Brief explanation of each. How they work together. Transition to deep-dive or examples.
```

### Closing/CTA Slide
```markdown
## [Call to Action or Provocative Question]

[One clear next step or thought to leave with]

**Speaker Notes:**
Circle back to opening if possible. End with confidence. No new information here.
```

---

## Example Transformation

**Source content:**
```
### Minutes 0-5: The Problem

**Opening:**
"Let's start with what everyone knows but nobody talks about: Most initiatives fail."

**The Data:**
- 80% of projects don't deliver expected value
- 90% of pilots never reach production
```

**Becomes:**
```markdown
---

## Most Initiatives Fail

80% of projects don't deliver expected value.

**Speaker Notes:**
Open with: "Let's start with what everyone knows but nobody talks about." (pause) Let the stat land. And 90% of pilots never even reach production. This is the reality we're working with.

---
```

---

## Final Checklist

Before completing, verify:
- [ ] Opening slide hooks attention immediately
- [ ] Each slide has exactly one idea
- [ ] Speaker notes use the format at the end of the slide `**Speaker Notes:**`
- [ ] Speaker notes are full sentences (not bullet keywords)
- [ ] Tone is clear and direct throughout
- [ ] Non-slide content moved to appendix
- [ ] Closing slide has clear CTA or memorable ending
- [ ] Output filename follows convention (`*_presentation.md`)
- [ ] Slide count matches target duration
