"""
Math question generator for 4 age groups.
Each group has increasing difficulty.
"""
import random


class QuestionGenerator:
    def __init__(self, age_group: str):
        """
        age_group: '5-7', '8-10', '11-13', '14+'
        """
        self.age_group = age_group

    def generate(self, level: int = 1) -> dict:
        """Returns a dict: {question, answer, choices, type}"""
        if self.age_group == '5-7':
            return self._gen_5_7(level)
        elif self.age_group == '8-10':
            return self._gen_8_10(level)
        elif self.age_group == '11-13':
            return self._gen_11_13(level)
        else:
            return self._gen_14plus(level)

    # ── Age 5-7 ──────────────────────────────────────────────────────────
    def _gen_5_7(self, level):
        max_num = min(5 + level * 2, 20)
        op = random.choice(['+', '-'])
        a = random.randint(1, max_num)
        b = random.randint(1, max_num)
        if op == '-':
            a, b = max(a, b), min(a, b)
        answer = a + b if op == '+' else a - b
        question = f"{a} {op} {b} = ?"
        return self._build(question, answer, max_val=max_num * 2)

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
        if op == '+':
            answer = a + b
        elif op == '-':
            answer = a - b
        else:
            answer = a * b
        sym = '×' if op == '*' else op
        question = f"{a} {sym} {b} = ?"
        return self._build(question, answer, max_val=max_num * 2)

    # ── Age 11-13 ─────────────────────────────────────────────────────────
    def _gen_11_13(self, level):
        max_num = min(20 + level * 5, 500)
        op = random.choice(['+', '-', '*', '/', 'pow', 'sqrt'])
        if op in ('+', '-'):
            a = random.randint(10, max_num)
            b = random.randint(10, max_num)
            if op == '-': a, b = max(a, b), min(a, b)
            answer = a + b if op == '+' else a - b
            question = f"{a} {op} {b} = ?"
        elif op == '*':
            a = random.randint(2, 20)
            b = random.randint(2, 20)
            answer = a * b
            question = f"{a} × {b} = ?"
        elif op == '/':
            b = random.randint(2, 12)
            answer = random.randint(2, 20)
            a = b * answer
            question = f"{a} ÷ {b} = ?"
        elif op == 'pow':
            a = random.randint(2, 10)
            b = random.randint(2, 3)
            answer = a ** b
            question = f"{a}^{b} = ?"
        else:  # sqrt
            answer = random.randint(2, 15)
            a = answer ** 2
            question = f"√{a} = ?"
        return self._build(question, answer, max_val=max(answer * 3, 30))

    # ── Age 14+ ───────────────────────────────────────────────────────────
    def _gen_14plus(self, level):
        qtype = random.choice(['algebra', 'fraction', 'percent', 'geometry', 'sequence'])
        if qtype == 'algebra':
            return self._algebra(level)
        elif qtype == 'fraction':
            return self._fraction(level)
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
        question = f"{a}x + {b} = {result}, x = ?"
        return self._build(question, x, max_val=30)

    def _fraction(self, level):
        d1 = random.randint(2, 8)
        d2 = random.randint(2, 8)
        n1 = random.randint(1, d1)
        n2 = random.randint(1, d2)
        from math import gcd
        common = d1 * d2 // gcd(d1, d2)
        num = n1 * (common // d1) + n2 * (common // d2)
        g = gcd(num, common)
        num //= g; common //= g
        question = f"{n1}/{d1} + {n2}/{d2} = ? (simplified)"
        answer_str = f"{num}/{common}" if common != 1 else str(num)
        return {'question': question, 'answer': answer_str,
                'choices': [answer_str, f"{num+1}/{common}", f"{num-1}/{common}", f"{num}/{common+1}"],
                'type': 'fraction'}

    def _percent(self, level):
        pct = random.choice([10, 15, 20, 25, 30, 50, 75])
        base = random.randint(20, 200)
        answer = int(base * pct / 100)
        question = f"{pct}% of {base} = ?"
        return self._build(question, answer, max_val=base)

    def _geometry(self, level):
        shape = random.choice(['rectangle_area', 'triangle_area', 'circle_area'])
        if shape == 'rectangle_area':
            w = random.randint(3, 20)
            h = random.randint(3, 20)
            answer = w * h
            question = f"Area of rectangle {w}×{h} = ?"
        elif shape == 'triangle_area':
            b = random.randint(4, 20)
            h = random.randint(4, 20)
            answer = b * h // 2
            question = f"Area of triangle base={b} height={h} = ?"
        else:
            import math
            r = random.randint(2, 10)
            answer = round(math.pi * r * r, 1)
            question = f"Area of circle r={r} ≈ ? (π≈3.14)"
            answer = round(3.14 * r * r, 1)
        return self._build(question, answer, max_val=int(answer) * 3 + 10)

    def _sequence(self, level):
        start = random.randint(1, 10)
        step = random.randint(2, 5 + level)
        length = 4
        seq = [start + i * step for i in range(length)]
        answer = seq[-1] + step
        shown = ', '.join(map(str, seq)) + ', ?'
        question = f"{shown}"
        return self._build(question, answer, max_val=answer * 2)

    # ── Helper ────────────────────────────────────────────────────────────
    def _build(self, question: str, answer, max_val: int = 100) -> dict:
        answer = int(answer) if isinstance(answer, float) and answer == int(answer) else answer
        wrongs = set()
        while len(wrongs) < 3:
            delta = random.randint(1, max(3, max_val // 5))
            candidate = int(answer) + random.choice([-delta, delta])
            if candidate != answer and candidate >= 0:
                wrongs.add(candidate)
        choices = [answer] + list(wrongs)[:3]
        random.shuffle(choices)
        return {'question': question, 'answer': answer,
                'choices': [str(c) for c in choices], 'type': 'mcq'}
