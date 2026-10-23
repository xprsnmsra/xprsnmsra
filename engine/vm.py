"""A complete toy compiler: lexer -> parser -> AST -> bytecode -> stack VM, executed at build time."""
import re, hashlib
TOK = re.compile(r"\s*(?:(\d+)|([A-Za-z_]\w*)|(==|[-+*%<={}()]))")
KW = {"while", "if", "print"}

def lex(src):
    out, i = [], 0
    while i < len(src.rstrip()):
        m = TOK.match(src, i)
        n, idt, op = m.groups(); i = m.end()
        out.append(("NUM", int(n)) if n else (("KW" if idt in KW else "ID"), idt) if idt else ("OP", op))
    return out

class P:
    def __init__(s, t): s.t, s.i = t, 0
    def pk(s): return s.t[s.i] if s.i < len(s.t) else (None, None)
    def eat(s, v=None):
        k = s.t[s.i]; s.i += 1; return k
    def prog(s):
        out = []
        while s.i < len(s.t) and s.pk()[1] != "}": out.append(s.stmt())
        return out
    def blk(s): s.eat(); b = s.prog(); s.eat(); return b
    def stmt(s):
        k, v = s.pk()
        if v == "while": s.eat(); c = s.expr(); return ("while", c, s.blk())
        if v == "if": s.eat(); c = s.expr(); return ("if", c, s.blk())
        if v == "print": s.eat(); return ("print", s.expr())
        s.eat(); s.eat(); return ("set", v, s.expr())
    def expr(s):
        l = s.add()
        if s.pk()[1] in ("==", "<"): op = s.eat()[1]; l = ("bin", op, l, s.add())
        return l
    def add(s):
        l = s.mul()
        while s.pk()[1] in ("+", "-"): op = s.eat()[1]; l = ("bin", op, l, s.mul())
        return l
    def mul(s):
        l = s.atom()
        while s.pk()[1] in ("*", "%"): op = s.eat()[1]; l = ("bin", op, l, s.atom())
        return l
    def atom(s):
        k, v = s.eat()
        if k == "NUM": return ("num", v)
        if k == "ID": return ("var", v)
        e = s.expr(); s.eat(); return e

def sx(n):
    if n[0] == "num": return str(n[1])
    if n[0] == "var": return n[1]
    if n[0] == "bin": return f"({n[1]} {sx(n[2])} {sx(n[3])})"
    if n[0] == "set": return f"(set {n[1]} {sx(n[2])})"
    if n[0] == "print": return f"(print {sx(n[1])})"
    return f"({n[0]} {sx(n[1])} {' '.join(sx(x) for x in n[2])})"

def comp(prog):
    c = []
    def e(n):
        if n[0] == "num": c.append(["PUSH", n[1]])
        elif n[0] == "var": c.append(["LOAD", n[1]])
        else: e(n[2]); e(n[3]); c.append([{"+": "ADD", "-": "SUB", "*": "MUL", "%": "MOD", "==": "EQ", "<": "LT"}[n[1]], None])
    def s(n):
        if n[0] == "set": e(n[2]); c.append(["STORE", n[1]])
        elif n[0] == "print": e(n[1]); c.append(["PRINT", None])
        elif n[0] == "if":
            e(n[1]); j = len(c); c.append(["JZ", None])
            for x in n[2]: s(x)
            c[j][1] = len(c)
        else:
            top = len(c); e(n[1]); j = len(c); c.append(["JZ", None])
            for x in n[2]: s(x)
            c.append(["JMP", top]); c[j][1] = len(c)
    for n in prog: s(n)
    c.append(["HALT", None]); return c

def execute(code):
    st, var, pc, tr, out, n = [], {}, 0, [], [], 0
    while code[pc][0] != "HALT" and n < 200000:
        op, a = code[pc]; n += 1
        if len(tr) < 14: tr.append((pc, op, a, list(st)))
        pc += 1
        if op == "PUSH": st.append(a)
        elif op == "LOAD": st.append(var[a])
        elif op == "STORE": var[a] = st.pop()
        elif op == "PRINT": out.append(st.pop())
        elif op == "JMP": pc = a
        elif op == "JZ":
            if not st.pop(): pc = a
        else:
            b, x = st.pop(), st.pop()
            st.append({"ADD": lambda: x + b, "SUB": lambda: x - b, "MUL": lambda: x * b, "MOD": lambda: x % b,
                       "EQ": lambda: int(x == b), "LT": lambda: int(x < b)}[op]())
    return tr, out, n

def run(seed):
    k = 3 + hashlib.sha256(seed.encode()).digest()[0] % 7
    src = f"tries = 0\ndone = 0\nwhile done == 0 {{\n  tries = tries + 1\n  if tries % {k} == 0 {{ done = 1 }}\n}}\nprint tries"
    toks = lex(src); ast = P(toks).prog(); code = comp(ast); tr, out, n = execute(code)
    L = ["── source " + "─" * 50, src, "── ast " + "─" * 52] + [sx(a) for a in ast]
    L += ["── bytecode " + "─" * 48] + [f"{i:02d}  {o:<6}{'' if a is None else a}" for i, (o, a) in enumerate(code)]
    L += ["── vm trace (first 14 of %d steps) " % n + "─" * 24] + [f"pc={p:02d}  {o:<6}{'' if a is None else a!s:<6} stack={s}" for p, o, a, s in tr]
    L += ["── result " + "─" * 50, f"{len(toks)} tokens · {len(code)} instructions · {n} cycles · output: {out[0]}"]
    return "\n".join(L)
