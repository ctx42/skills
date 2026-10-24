import { filterDevices } from "../lib.js";
import { bench } from "./bench.js";

const devices = Array.from({ length: 5000 }, (_, i) => ({ id: i, name: `device-${i}`, tags: ["edge", "lab"] }));

bench("filterDevices 5000", () => filterDevices(devices, "lab"));
