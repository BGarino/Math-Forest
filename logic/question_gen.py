"""
Math question generator for 4 age groups.
5-7  : single-digit addition only (1-9 + 1-9)
8-10 : +, -, x up to 100
11-13: +, -, x, /, powers, sqrt
14+  : algebra, fractions, percent, geometry, sequences
"""
import random


class QuestionGenerator:
    def __init__(self, age_group: str):
        self.age_group = age_group

    def generate(self, level: int = 1) -> dict:
        if self.age_group == '5-7':
            return self._gen_5_7(level)
        elif self.age_group == '8-10':
            return self._gen_8_10(level)
        elif self.age_group == '11-13':
            return self._gen_11_13(level)
        else:
            return self._gen_14plus(level)

    # ── Age 5-7: ONLY single-digit addition ──────────────────────────────
    def _gen_5_7(self, level):
        # Always single digit numbers (1-9), only addition
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        answer = a + b
        question = f"{a} + {b} = ?"
        # Wrong answers close to correct, but stay positive and reasonable
        wrongs = set()
        while len(wrongs) < 3:
            delta = random.randint(1, 3)
            candidate = answer + random.choice([-delta, delta])
            if candidate != answer and candidate > 0:
                wrongs.add(candidate)
        choices = [answer] + list(wrongs)
        random.shuffle(choices)
        return {
            'question': question,
            'answer': answer,
            'choices': [str(c) for c in choices],
            'type': 'addition'
        }

    # ── Age 8-10 ──────────────────────────────────────────────────────────
    def _gen_8_10(self, level):
        max_num = min(10 + level * 3, 100)
        op = random.choice(['+', '-', '*'])
        if op == '*':
            a = random.randint(2, min(10, max_num))
            b = random.randint(2, min(10, max_num))
        else:
            a = random.randint(1, max_num)
            b = random.randint(1, max_num)
        if op == '-':
            a, b = max(a, b), min(a, b)
        answer = a + b if op == '+' else (a - b if op == '-' else a * b)
        sym = 'x' if op == '*' else op
        question = f"{a} {sym} {b} = ?"
        return self._build(question, answer, max_val=max(answer * 2, 20))

    # ── Age 11-13 ─────────────────────────────────────────────────────────
    def _gen_11_13(self, level):
        max_num = min(20 + level * 5, 500)
        op = random.choice(['+', '-', '*', '/', 'pow', 'sqrt'])
        if op in ('+', '-'):
            a = random.randint(10, max_num)
            b = random.randint(10, max_num)
            if op == '-':
                a, b = max(a, b), min(a, b)
            answer = a + b if op == '+' else a - b
            question = f"{a} {op} {b} = ?"
        elif op == '*':
            a = random.randint(2, 20)
            b = random.randint(2, 20)
            answer = a * b
            question = f"{a} x {b} = ?"
        elif op == '/':
            b = random.randint(2, 12)
            answer = random.randint(2, 20)
            a = b * answer
            question = f"{a} / {b} = ?"
        elif op == 'pow':
            a = random.randint(2, 10)
            b = random.randint(2, 3)
            answer = a ** b
            question = f"{a}^{b} = ?"
        else:
            answer = random.randint(2, 15)
            a = answer ** 2
            question = f"sqrt({a}) = ?"
        return self._build(question, answer, max_val=max(answer * 3, 30))

    # ── Age 14+ ───────────────────────────────────────────────────────────
    def _gen_14plus(self, level):
        qtype = random.choice(['algebra', 'percent', 'geometry', 'sequence'])
        if qtype == 'algebra':
            return self._algebra(level)
        elif qtype == 'percent':
            return self._percent(level)
        elif qtype == 'geometry':
            return self._geometry(level)
        else:
            return self._sequence(level)

    def _algebra(self, level):
        x = random.randint(1, 10 + level)
        a = random.randint(1, 10)
        b = random.randint(1, 20)
        result = a * x + b
        question = f"{a}x + {b} = {result},  x = ?"
        return self._build(question, x, max_val=30)

    def _percent(self, level):
        pct = random.choice([10, 20, 25, 50])
        base = random.randint(20, 200)
        answer = int(base * pct / 100)
        question = f"{pct}% of {base} = ?"
        return self._build(question, answer, max_val=base)

    def _geometry(self, level):
        w = random.randint(3, 20)
        h = random.randint(3, 20)
        answer = w * h
        question = f"Area: {w} x {h} = ?"
        return self._build(question, answer, max_val=answer * 2 + 10)

    def _sequence(self, level):
        start = random.randint(1, 10)
        step = random.randint(2, 5 + level)
        seq = [start + i * step for i in range(4)]
        answer = seq[-1] + step
        shown = ', '.join(map(str, seq)) + ', ?'
        question = f"{shown}"
        return self._build(question, answer, max_val=answer * 2)

    # ── Helper ────────────────────────────────────────────────────────────
    def _build(self, question: str, answer, max_val: int = 100) -> dict:
        if isinstance(answer, float) and answer == int(answer):
            answer = int(answer)
        wrongs = set()
        attempts = 0
        while len(wrongs) < 3 and attempts < 50:
            attempts += 1
            delta = random.randint(1, max(3, max_val // 5))
            candidate = int(answer) + random.choice([-delta, delta])
            if candidate != int(answer) and candidate >= 0:
                wrongs.add(candidate)
        choices = [answer] + list(wrongs)[:3]
        random.shuffle(choices)
        return {
            'question': question,
            'answer': answer,
            'choices': [str(c) for c in choices],
            'type': 'mcq'
        }
