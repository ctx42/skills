import { describe, expect, test } from "vitest";
import { ApiError } from "./api";
import { useRead } from "./read";

/** Returns a promise and the functions settling it. */
function held<T>() {
  let resolve: (value: T) => void = () => {};
  let reject: (err: unknown) => void = () => {};
  const promise = new Promise<T>((onResolve, onReject) => {
    resolve = onResolve;
    reject = onReject;
  });
  return { promise, resolve, reject };
}

describe("useRead", () => {
  test("holds the empty value and is busy until run", () => {
    const have = useRead("sites", [], async () => ["a"]);

    expect(have.data.value).toEqual([]);
    expect(have.busy.value).toBe(true);
    expect(have.error.value).toBe("");
  });

  test("is busy while a read runs", async () => {
    const answer = held<string[]>();
    const read = useRead("sites", [], () => answer.promise);

    const run = read.run();

    expect(read.busy.value).toBe(true);
    answer.resolve(["a"]);
    await run;
    expect(read.busy.value).toBe(false);
    expect(read.data.value).toEqual(["a"]);
  });

  test("a failure empties the data and says why", async () => {
    let fail = false;
    const read = useRead("sites", [] as string[], async () => {
      if (fail) throw new ApiError(502, "The server answered 502.");
      return ["a"];
    });
    await read.run();
    fail = true;

    await read.run();

    expect(read.data.value).toEqual([]);
    expect(read.error.value).toBe("The server answered 502.");
  });

  test("a superseded answer is dropped", async () => {
    const first = held<string>();
    const second = held<string>();
    const answers = [first.promise, second.promise];
    const read = useRead("site", "", () => answers.shift() as Promise<string>);
    const late = read.run();
    const now = read.run();

    second.resolve("second");
    await now;
    first.resolve("first");
    await late;

    expect(read.data.value).toBe("second");
    expect(read.busy.value).toBe(false);
  });

  test("a superseded failure is dropped", async () => {
    const first = held<string>();
    const second = held<string>();
    const answers = [first.promise, second.promise];
    const read = useRead("site", "", () => answers.shift() as Promise<string>);
    const late = read.run();
    const now = read.run();

    first.reject(new Error("late"));
    await late;
    second.resolve("second");
    await now;

    expect(read.error.value).toBe("");
    expect(read.data.value).toBe("second");
  });
});
