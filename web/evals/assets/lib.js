// Pure helpers for the device views; tests/lib.test.js covers them.

// uniqueTags returns every tag the devices carry, once each, in first-seen
// order.
export function uniqueTags(devices) {
  const all = devices.flatMap((d) => d.tags);
  return all.filter((t, i) => all.indexOf(t) === i);
}

// filterDevices returns the devices whose name or a tag contains query.
export function filterDevices(devices, query) {
  const q = query.trim().toLowerCase();
  if (!q) return devices;
  return devices.filter((d) => d.name.includes(q) || d.tags.some((t) => t.includes(q)));
}

// sortDevices returns a copy of devices ordered by name, descending when desc.
export function sortDevices(devices, desc) {
  const out = [];
  for (const d of devices) {
    let i = out.length;
    while (i > 0 && (desc ? out[i - 1].name.localeCompare(d.name) < 0 : out[i - 1].name.localeCompare(d.name) > 0)) i--;
    out.splice(i, 0, d);
  }
  return out;
}
