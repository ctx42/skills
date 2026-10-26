/**
 * Runs before every test file: each test unmounts what it mounted when it
 * ends, and starts with empty browser storage.
 */
import { enableAutoUnmount } from "@vue/test-utils";
import { afterEach, beforeEach } from "vitest";

enableAutoUnmount(afterEach);

beforeEach(() => localStorage.clear());
