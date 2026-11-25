// Entry program for news-image-20261125 (Node 22, standard library only).
// The composed front page sits beside this file as entry.png; running the
// program copies those exact bytes to the grader's output folder. The copy
// is the whole job, so two runs always produce identical output.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
