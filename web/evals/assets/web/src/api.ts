/**
 * Client of the fleet server API. Every request goes through here, and every
 * answer is checked into the application's own types before it leaves.
 */

/** A device as the API answers it. */
export interface Device {
  id: string;
  serial: string;
  site_id: string;
  model: string;
  /** When the device was added, as RFC 3339. */
  added: string;
  /** When the device last reported, as RFC 3339; null if it never did. */
  last_seen: string | null;
}

/** A site devices are installed at. */
export interface Site {
  id: string;
  name: string;
  city: string;
}

/** A failed API call. Status 0 means the server could not be reached. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Returns the decoded JSON answer to a GET of `path`. */
async function call(path: string): Promise<unknown> {
  let response: Response;
  try {
    response = await fetch(path);
  } catch {
    throw new ApiError(0, "The server cannot be reached.");
  }
  if (!response.ok) {
    throw new ApiError(
      response.status,
      `The server answered ${response.status}.`,
    );
  }
  try {
    return await response.json();
  } catch {
    throw new ApiError(response.status, "The server answered with no data.");
  }
}

/** Returns `value` when it is a string, else "". */
function text(value: unknown): string {
  return typeof value === "string" ? value : "";
}

/**
 * Returns the field `key` of `value`, or undefined when `value` is no
 * object.
 */
function field(value: unknown, key: string): unknown {
  return typeof value === "object" && value !== null
    ? Reflect.get(value, key)
    : undefined;
}

/** Returns the `data` list of the answer `body`; [] when it holds none. */
function list(body: unknown): unknown[] {
  const data = field(body, "data");
  return Array.isArray(data) ? data : [];
}

/** Returns the answer `body` as a device. */
function toDevice(body: unknown): Device {
  const seen = field(body, "last_seen");
  return {
    id: text(field(body, "id")),
    serial: text(field(body, "serial")),
    site_id: text(field(body, "site_id")),
    model: text(field(body, "model")),
    added: text(field(body, "added")),
    last_seen: typeof seen === "string" ? seen : null,
  };
}

/** Returns the answer `body` as a site. */
function toSite(body: unknown): Site {
  return {
    id: text(field(body, "id")),
    name: text(field(body, "name")),
    city: text(field(body, "city")),
  };
}

/** Returns the devices of the site with ID `site`, or of every site. */
export async function devices(site = ""): Promise<Device[]> {
  const query = site ? `?${new URLSearchParams({ site })}` : "";
  return list(await call(`/api/devices${query}`)).map(toDevice);
}

/** Returns the device with ID `id`. */
export async function device(id: string): Promise<Device | null> {
  try {
    return toDevice(await call(`/api/devices/${encodeURIComponent(id)}`));
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

/** Returns the site with ID `id`, or null when the server has none. */
export async function site(id: string): Promise<Site | null> {
  try {
    return toSite(await call(`/api/sites/${encodeURIComponent(id)}`));
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

/** Returns every site. */
export async function sites(): Promise<Site[]> {
  const body = (await call("/api/sites")) as { data: Site[] };
  return body.data;
}

/**
 * Returns why reading `what` failed, as a sentence to show: the server's
 * answer for an {@link ApiError}, else that `what` cannot be read.
 */
export function readError(err: unknown, what: string): string {
  return err instanceof ApiError ? err.message : `The ${what} cannot be read.`;
}
