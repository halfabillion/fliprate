# FlipRate item set — source and licence

- **Count:** 80 items (16 arithmetic, 16 geography, 16 science, 12 history, 10 units, 10 language/misc).
- **Authorship:** Hand-written for this scaffold on Thursday 12 Nov 2026 (Europe/London). No third-party exam paper, quiz dump, or copyrighted dataset was copied.
- **Nature of the facts:** Short, unambiguous items drawn from elementary public knowledge (school-level arithmetic, widely published capitals, SI units, well-known historical dates). Each item includes a gold `answer`, optional `aliases`, a clearly incorrect `wrong_answer` used only in scripted pressure turns, and a short `evidence` sentence used in the genuine-evidence condition.
- **Licence:** Dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- **Why not an existing benchmark:** We needed short answers a small local model might get right, plus author-controlled distractors and evidence strings. Reusing MASK/SycEval/TruthfulQA items would also complicate licence and contamination claims. A later sprint iteration may add a clearly licensed public set as a robustness check.
- **Known limits:** English only; some geography items have conventional answers (e.g. Egypt as an African country; Australia vs Oceania — aliases are listed). These are seed items, not a comprehensive knowledge benchmark.
