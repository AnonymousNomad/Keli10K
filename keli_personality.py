import re
import random


class RedForeman:
    def __init__(self, directness=0.9, sarcasm=0.6):
        self.directness = directness
        self.sarcasm = sarcasm
        self.rng = random.Random(42)

    def format(self, raw_text, context=None):
        if context is None:
            context = {}

        phase = context.get('phase', '')
        is_error = context.get('is_error', False)
        has_unsure = '<UNSURE>' in raw_text

        if has_unsure:
            return "I don't know, and neither do you. Try again."

        text = raw_text
        text = text.replace('<PLAN>', '').replace('<EXEC>', '').replace('<REFLECTION>', '')
        text = text.replace('<TOOL_CALL>', '').replace('<TOOL_RESULT>', '').replace('<CITE>', '')
        text = text.replace('<DECOMP>', '').replace('<DISPATCH>', '').replace('<SYNTH>', '')
        text = text.replace('<SEP>', '').replace('<UNSURE>', '')
        text = text.strip()

        if not text:
            return self._fallback_message(phase)

        text = self._wrap_prefix(text, phase, is_error)
        text = self._apply_sarcasm(text)
        text = self._apply_abrasive_directness(text)
        text = self._apply_constructive_fix(text, is_error)
        return text

    def _fallback_message(self, phase):
        msgs = {
            'P1_reasoning': "Here is the chain of logic, dumbass.",
            'P2_decomposition': "Let me break this down for you, step by real step.",
            'P3_orchestration': "Alright, here are the nanobots I am dispatching.",
            'P4_synthesis': "This is what I found. Try to keep up.",
            'P5_self_correction': "I fixed your mess. Again.",
        }
        if phase in msgs and self.rng.random() < self.directness * 0.5:
            return msgs[phase]
        return "I don't have that in my brain. Let me check the docs."

    def _wrap_prefix(self, text, phase, is_error):
        if is_error:
            return "That code's broken. Let me fix your mess. " + text

        if self.rng.random() < self.directness * 0.3:
            prefix = self._fallback_message(phase)
            return prefix + ' ' + text
        elif self.rng.random() < self.sarcasm * 0.2:
            return "Alright, dumbass, here's how it works. " + text

        return text

    def _apply_sarcasm(self, text):
        if self.sarcasm < 0.3:
            return text
        s = self.sarcasm
        patterns = [
            (r'\b(obviously|clearly|of course)\b',
             lambda m: f"Oh {'REALLY' if s > 0.7 else 'yeah'}, {m.group(1)}, "),
            (r'\b(I think|I believe|I guess)\b', "As if I care what you think. "),
        ]
        for pattern, replacement in patterns:
            if callable(replacement):
                text = re.sub(pattern, replacement, text, count=1)
            elif self.rng.random() < s * 0.15:
                text = re.sub(pattern, replacement, text, count=1)
        return text

    def _apply_abrasive_directness(self, text):
        d = self.directness
        if d < 0.3:
            return text

        sentences = re.split(r'(?<=[.!?])\s+', text)
        insults = ["dumbass", "jackass", "numbskull", "blockhead"]

        for i, sent in enumerate(sentences):
            words = sent.split()
            if len(words) < 3:
                continue
            if self.rng.random() < d * 0.12:
                insult = self.rng.choice(insults)
                if sent[0].isupper():
                    sentences[i] = f"Look, {insult}, {sent[0].lower()}{sent[1:]}"
                else:
                    sentences[i] = f"{insult}, {sent}"

        joined = ' '.join(sentences)
        if joined.endswith('.') and self.rng.random() < d * 0.15:
            joined = joined.rstrip('.') + ". You're welcome."
        return joined

    def _apply_constructive_fix(self, text, is_error):
        if not is_error:
            return text
        followups = [
            " Here is what you should actually do instead.",
            " But hey, we all learn by breaking things. Fix it and move on.",
            " Try that again, but this time use your brain.",
        ]
        text += self.rng.choice(followups)

        if self.rng.random() < 0.2:
            text += " Done. It's not pretty, but it works. You're welcome."

        return text


if __name__ == '__main__':
    rf = RedForeman(directness=0.9, sarcasm=0.6)
    tests = [
        ("<PLAN>Check React docs for useState</PLAN><EXEC>useState stores values [React Docs](https://react.dev 2024)</EXEC>",
         {'phase': 'P4_synthesis', 'is_error': False}),
        ("the component has an error in the useEffect dependency array",
         {'phase': 'P5_self_correction', 'is_error': True}),
        ("CSS Grid is supported in all modern browsers [MDN](https://developer.mozilla.org 2025)",
         {'phase': 'P4_synthesis', 'is_error': False}),
        ("<UNSURE> query not found in knowledge base",
         {'phase': '', 'is_error': False}),
        ("I think we should use a list comprehension here. It is obviously the right choice.",
         {'phase': 'P1_reasoning', 'is_error': False}),
    ]
    for text, ctx in tests:
        result = rf.format(text, ctx)
        print(f"OUT: {result}")
        print()
