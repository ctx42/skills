/** Formatting of values for display. */

/** Where dates show: in UTC, or in the browser's own time zone. */
export type DateZone = "utc" | "local";

/** The date zones, labelled for a choice, in the order offered. */
export const dateZones: { label: string; value: DateZone }[] = [
  { label: "UTC", value: "utc" },
  { label: "My time zone", value: "local" },
];

/** Returns whether `value` is a date zone. */
export function isDateZone(value: unknown): value is DateZone {
  return dateZones.some((zone) => zone.value === value);
}

/**
 * formatDate returns the RFC 3339 time `value` as "YYYY-MM-DD HH:MM" in
 * `zone`, or "never" for null and "-" for a value that is not a time.
 */
export function formatDate(value: string | null, zone: DateZone): string {
  if (value === null) return "never";
  const time = new Date(value);
  if (Number.isNaN(time.getTime())) return "-";
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: zone === "utc" ? "UTC" : undefined,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(time);
  const part = (type: string) => parts.find((p) => p.type === type)?.value;
  return `${part("year")}-${part("month")}-${part("day")} ${part("hour")}:${part("minute")}`;
}
