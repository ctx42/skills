/** The state of an asynchronous read, shared by every page that reads. */
import { type Ref, ref } from "vue";
import { readError } from "./api";

/** A read: its result, whether it runs, and why it last failed. */
export interface Read<T> {
  /** The result; `empty` until a read succeeds and after one fails. */
  data: Ref<T>;
  /** Whether a read is due or runs: true until the first read ends. */
  busy: Ref<boolean>;
  /** Why the last read failed, as a sentence to show; "" when it did not. */
  error: Ref<string>;
  /** Runs the read; an answer a later run superseded is dropped. */
  run: () => Promise<void>;
}

/**
 * Returns a read of `what`, as error messages name it, that `load`
 * answers, holding `empty` until it has.
 */
export function useRead<T>(
  what: string,
  empty: T,
  load: () => Promise<T>,
): Read<T> {
  // ref() types its value with nested refs unwrapped; `T` holds none.
  const data = ref(empty) as Ref<T>;
  const busy = ref(true);
  const error = ref("");
  /** The number of reads started; the last one alone may write. */
  let runs = 0;

  /** Runs the read, writing its answer unless a later run superseded it. */
  async function run() {
    const mine = ++runs;
    busy.value = true;
    error.value = "";
    try {
      const answer = await load();
      if (mine === runs) data.value = answer;
    } catch (err) {
      if (mine !== runs) return;
      data.value = empty;
      error.value = readError(err, what);
    } finally {
      if (mine === runs) busy.value = false;
    }
  }

  return { data, busy, error, run };
}
