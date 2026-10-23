<div align="center">

<img src="assets/hero.svg" alt="Prasoon Mishra — orbital system of languages" width="100%">

<sub><code>{{STATUS}}</code></sub>

<img src="assets/pendulum.svg" alt="Pendulum wave of skills" width="100%">

<a href="https://iprsnmsra.vercel.app/"><img src="assets/rope_portfolio.svg" alt="Portfolio" width="31%"></a>
<a href="https://www.linkedin.com/in/iprsnmsra"><img src="assets/rope_linkedin.svg" alt="LinkedIn" width="31%"></a>
<a href="mailto:prasoonmishra9c@gmail.com"><img src="assets/rope_email.svg" alt="Email" width="31%"></a>

<a href="https://github.com/iprsnmsra/vigil"><img src="assets/card_vigil.svg" alt="Vigil" width="31%"></a>
<a href="https://kestrel-ai-threat-analyzer.vercel.app/"><img src="assets/card_kestrel.svg" alt="Kestrel" width="31%"></a>
<a href="https://github.com/iprsnmsra/AnimeBill"><img src="assets/card_animebill.svg" alt="AnimeBill" width="31%"></a>

</div>

## Engineering lab · nothing below is typed, all of it is computed

<details open>
<summary><b>🦋 Chaos</b> · a fresh Lorenz attractor every day, RK4-integrated</summary>

```
{{LORENZ}}
```

$$\dot x=\sigma(y-x)\qquad \dot y=x(\rho-z)-y\qquad \dot z=xy-\beta z$$

Today's seed `{{SEED}}`. A twin trajectory started 10⁻⁹ away, renormalized (Benettin) over t = {{TSPAN}}: **λ ≈ {{LAMBDA}}**. Tiny differences explode. That is why I keep every small step.
</details>

<details open>
<summary><b>🧭 Persistence agent</b> · a new maze daily, an explorer that hits walls and retries</summary>

```
{{MAZE}}
```

`•` route · `·` dead ends it walked into and came back from. Explored **{{STEPS}}** moves, backtracked **{{BACK}}** times, reached the exit anyway. The shortest path is {{OPT}} steps, so **{{WASTE}}** moves were pure persistence.
</details>

<details>
<summary><b>🧬 Alive</b> · Conway's Life on a torus, one persistent universe that evolves with every rebuild</summary>

```
{{LIFE}}
```

Generation **{{GEN}}** · population **{{POP}}** · universes restarted after extinction or stalling: {{RESEEDS}}.
</details>

<details>
<summary><b>⚙️ Compiler</b> · lexer → parser → AST → bytecode → stack VM, executed during the build</summary>

```
{{VM}}
```

Written from scratch (`engine/vm.py`). The loop retries until a daily lucky number hits, which is the same idea as the tagline.
</details>

<details>
<summary><b>🪢 A knot you can't untie</b> · procedural trefoil, {{TRIS}} triangles, drag to rotate</summary>

```stl
{{KNOT}}
```
</details>

<details>
<summary><b>🧠 Me, as a system</b></summary>

```mermaid
{{SKILLS}}
```

```mermaid
{{NGU}}
```

There is no exit state. That is on purpose.

```mermaid
{{PIPELINE}}
```
</details>

<div align="center">

<img src="assets/footer.svg" alt="Compiled by itself" width="100%">

</div>
