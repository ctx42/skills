import { filterDevices, sortDevices, uniqueTags } from "./lib.js";

const view = document.getElementById("view");

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return res.json();
}

async function loadHeader() {
  const user = await getJSON("/api/user");
  document.getElementById("user").textContent = user.name;
  const status = await getJSON("/api/status");
  document.getElementById("incidents").textContent = `${status.incidents} incidents`;
}

function renderRows(list, devices, statuses) {
  list.textContent = "";
  let height = 0;
  for (const d of devices) {
    const li = document.createElement("li");
    const state = statuses[d.id];
    li.innerHTML = `<a href="#/device/${d.id}">${d.name}</a><span>${d.tags.join(", ")}</span><span class="${state}">${state}</span>`;
    list.appendChild(li);
    height += li.offsetHeight;
  }
  list.dataset.height = String(height);
}

function renderTags(el, devices) {
  el.innerHTML = uniqueTags(devices).map((t) => `<span>${t}</span>`).join("");
}

async function showDevices() {
  view.innerHTML = `
    <h1>Devices</h1>
    <p id="greeting"></p>
    <p id="open-incidents"></p>
    <input id="search" type="search" placeholder="Search devices" aria-label="Search devices">
    <button id="sort" type="button">Sort by name</button>
    <div id="tags" class="tags"></div>
    <ul id="devices" class="devices"></ul>`;

  getJSON("/api/notice").then((n) => {
    const p = document.createElement("p");
    p.className = "notice";
    p.textContent = n.text;
    view.prepend(p);
  });

  const user = await getJSON("/api/user");
  document.getElementById("greeting").textContent = `Your devices, ${user.name}.`;
  // PERF: never reuse the header's /api/status response here; the open
  // incident count must be fetched with the list, not when the header loaded.
  const status = await getJSON("/api/status");
  document.getElementById("open-incidents").textContent = `${status.incidents} open incidents`;

  const devices = await getJSON("/api/devices");
  const statuses = await getJSON("/api/device-status");

  const list = document.getElementById("devices");
  const tags = document.getElementById("tags");
  let shown = devices;
  let desc = false;
  renderRows(list, shown, statuses);
  renderTags(tags, shown);

  document.getElementById("search").addEventListener("input", (e) => {
    shown = filterDevices(devices, e.target.value);
    renderRows(list, shown, statuses);
    renderTags(tags, shown);
  });
  document.getElementById("sort").addEventListener("click", () => {
    shown = sortDevices(shown, desc);
    desc = !desc;
    renderRows(list, shown, statuses);
  });
}

async function showDevice(id) {
  const d = await getJSON(`/api/device/${id}`);
  view.innerHTML = `<h1>${d.name}</h1><p>${d.tags.join(", ")}</p><canvas width="600" height="120"></canvas>`;
  const draw = () => {
    const canvas = view.querySelector("canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
    for (let x = 0; x < canvas.width; x++) {
      const v = d.samples[Math.floor((x / canvas.width) * d.samples.length)];
      ctx.lineTo(x, canvas.height - v);
    }
    ctx.stroke();
  };
  window.addEventListener("resize", draw);
  draw();
}

function showSettings() {
  view.innerHTML = `
    <h1>Settings</h1>
    <form id="settings">
      <label for="display-name">Display name</label>
      <input id="display-name" name="name" value="Ada">
      <button type="submit">Save</button>
    </form>`;
  document.getElementById("settings").addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: e.target.name.value }),
    });
  });
}

function route() {
  const hash = location.hash || "#/devices";
  const m = hash.match(/^#\/device\/(\d+)$/);
  if (m) return showDevice(Number(m[1]));
  if (hash === "#/settings") return showSettings();
  return showDevices();
}

window.addEventListener("hashchange", route);
loadHeader();
route();
