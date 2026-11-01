/** Sampled native outlines. No React, Remotion, font fetch or private assets required. */
export type VariableTypeData = {
  formatVersion: 1;
  coordinateSize: number;
  axes: {wdth: number[]; wght: number[]};
  metrics: {capHeight: number[]};
  glyphs: Record<string, {commands: string; points: number[][]}>;
  words: Record<string, {positions: number[][]; advance: number[]}>;
};
export type Bounds = {minX: number; maxX: number; minY: number; maxY: number};
export type Glyph = {commands: string; points: number[]; x: number; bounds: Bounds};
export type Word = {glyphs: Glyph[]; advance: number; capHeight: number; bounds: Bounds};
type Corners = {indices: number[]; weights: number[]};

const cell = (axis: number[], value: number): [number, number] => {
  if (!Number.isFinite(value) || axis.length < 2 || value < axis[0] || value > axis[axis.length - 1]) {
    throw new Error(`Axis value ${value} is outside the supplied sampling grid`);
  }
  const i = Math.min(axis.length - 2, axis.findIndex((v) => v >= value) - 1);
  const index = Math.max(0, i);
  return [index, (value - axis[index]) / (axis[index + 1] - axis[index])];
};
const corners = (data: VariableTypeData, width: number, weight: number): Corners => {
  const [i, u] = cell(data.axes.wdth, width), [j, v] = cell(data.axes.wght, weight);
  const n = data.axes.wght.length;
  return {indices: [i * n + j, i * n + j + 1, (i + 1) * n + j, (i + 1) * n + j + 1], weights: [(1-u)*(1-v), (1-u)*v, u*(1-v), u*v]};
};
const scalar = (values: number[], c: Corners): number => c.indices.reduce((sum, i, k) => sum + values[i] * c.weights[k], 0);
const vector = (rows: number[][], c: Corners): number[] => rows[c.indices[0]].map((_, k) => c.indices.reduce((sum, i, n) => sum + rows[i][k] * c.weights[n], 0));

/** Tight Bézier bounds, including derivative extrema; not the control-point hull. */
export const pathBounds = (commands: string, points: number[]): Bounds => {
  const box: Bounds = {minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity};
  let index = 0, x = 0, y = 0, startX = 0, startY = 0;
  const include = (px: number, py: number) => {
    box.minX = Math.min(box.minX, px); box.maxX = Math.max(box.maxX, px);
    box.minY = Math.min(box.minY, py); box.maxY = Math.max(box.maxY, py);
  };
  const next = (): [number, number] => {
    if (index + 1 >= points.length) throw new Error('Malformed outline coordinates');
    const result: [number, number] = [points[index], points[index + 1]]; index += 2; return result;
  };
  const roots = (a: number, b: number, c: number): number[] => {
    if (Math.abs(a) < 1e-12) return Math.abs(b) < 1e-12 ? [] : [-c/b];
    const discriminant = b*b - 4*a*c;
    return discriminant < 0 ? [] : [(-b + Math.sqrt(discriminant))/(2*a), (-b - Math.sqrt(discriminant))/(2*a)];
  };
  for (const command of commands) {
    if (command === 'M') { [x, y] = next(); startX = x; startY = y; include(x, y); }
    else if (command === 'L') { [x, y] = next(); include(x, y); }
    else if (command === 'Z') { x = startX; y = startY; }
    else if (command === 'Q') {
      const [ax, ay] = next(), [bx, by] = next();
      const ts = [(x-ax)/(x-2*ax+bx), (y-ay)/(y-2*ay+by)];
      for (const t of ts.filter((v) => v > 0 && v < 1)) {
        const u = 1-t; include(u*u*x + 2*u*t*ax + t*t*bx, u*u*y + 2*u*t*ay + t*t*by);
      }
      x = bx; y = by; include(x, y);
    } else if (command === 'C') {
      const [ax, ay] = next(), [bx, by] = next(), [cx, cy] = next();
      const ts = [...roots(-x+3*ax-3*bx+cx, 2*(x-2*ax+bx), ax-x), ...roots(-y+3*ay-3*by+cy, 2*(y-2*ay+by), ay-y)];
      for (const t of ts.filter((v) => v > 0 && v < 1)) {
        const u = 1-t; include(u*u*u*x + 3*u*u*t*ax + 3*u*t*t*bx + t*t*t*cx, u*u*u*y + 3*u*u*t*ay + 3*u*t*t*by + t*t*t*cy);
      }
      x = cx; y = cy; include(x, y);
    } else throw new Error(`Unsupported path command ${command}`);
  }
  if (index !== points.length || !Number.isFinite(box.minX)) throw new Error('Malformed or empty outline');
  return box;
};

/** Tracking is additional distance per gap in the generated coordinate system. */
export const wordAt = (data: VariableTypeData, text: string, width: number, weight: number, tracking = 0): Word => {
  if (data.formatVersion !== 1 || !data.words[text] || !Number.isFinite(tracking)) throw new Error('Unsupported data, ungenerated word or invalid tracking');
  const c = corners(data, width, weight), positions = vector(data.words[text].positions, c);
  const glyphs = [...text].map((character, i): Glyph => {
    const entry = data.glyphs[character];
    if (!entry) throw new Error(`Missing glyph ${character}`);
    const points = vector(entry.points, c);
    return {commands: entry.commands, points, x: positions[i] + i*tracking, bounds: pathBounds(entry.commands, points)};
  });
  return {
    glyphs, advance: scalar(data.words[text].advance, c) + (glyphs.length-1)*tracking,
    capHeight: scalar(data.metrics.capHeight, c),
    bounds: {
      minX: Math.min(...glyphs.map((g) => g.x + g.bounds.minX)), maxX: Math.max(...glyphs.map((g) => g.x + g.bounds.maxX)),
      minY: Math.min(...glyphs.map((g) => g.bounds.minY)), maxY: Math.max(...glyphs.map((g) => g.bounds.maxY)),
    },
  };
};

/** SVG path at a fixed baseline and cap height. Alignment uses actual curve bounds. */
export const wordPath = (word: Word, placement: {x: number; baseline: number; capHeight: number; align?: 'left' | 'center' | 'right'}): string => {
  if (![placement.x, placement.baseline, placement.capHeight, word.capHeight].every(Number.isFinite) || !(placement.capHeight > 0) || !(word.capHeight > 0)) throw new Error('Placement must be finite and cap heights must be positive');
  const scale = placement.capHeight / word.capHeight;
  const anchor = placement.align === 'center' ? (word.bounds.minX + word.bounds.maxX)/2 : placement.align === 'right' ? word.bounds.maxX : word.bounds.minX;
  const round = (n: number) => Math.round(n*1000)/1000;
  return word.glyphs.map((glyph) => {
    let index = 0, path = '';
    const point = () => {
      const x = placement.x + (glyph.points[index] + glyph.x - anchor)*scale;
      const y = placement.baseline - glyph.points[index+1]*scale;
      index += 2; return `${round(x)} ${round(y)}`;
    };
    for (const command of glyph.commands) {
      if (command === 'M' || command === 'L') path += `${command}${point()}`;
      else if (command === 'Q') path += `Q${point()} ${point()}`;
      else if (command === 'C') path += `C${point()} ${point()} ${point()}`;
      else if (command === 'Z') path += 'Z';
      else throw new Error(`Unsupported path command ${command}`);
    }
    return path;
  }).join('');
};
