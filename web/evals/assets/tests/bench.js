// bench runs fn for about a second and prints its mean time per call; the
// project's benchmarks (tests/*.bench.js) use it, and `make bench` runs them.
export function bench(name, fn) {
  let n = 0;
  const start = performance.now();
  while (performance.now() - start < 1000) {
    fn();
    n++;
  }
  console.log(`${name}: ${((performance.now() - start) / n).toFixed(3)} ms/op (${n} ops)`);
}
