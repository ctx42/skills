import { expect, type Page, test } from "@playwright/test";

/** Returns the body rows of the device table: the rows holding cells. */
function rows(page: Page) {
  return page.getByRole("row").filter({ has: page.getByRole("cell") });
}

test("the devices list every device of the inventory", async ({ page }) => {
  // The start page is the device list, read from the fake inventory.
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Devices" })).toBeVisible();
  await expect(rows(page)).toHaveCount(6);
  await expect(rows(page).first()).toContainText("North Yard");
});

test("picking a site narrows the devices and names it in the address", async ({
  page,
}) => {
  await page.goto("/");
  await expect(rows(page)).toHaveCount(6);

  // Open the site picker and choose the second site.
  await page.getByRole("combobox", { name: "Site" }).click();
  await page.getByRole("option", { name: "Harbour" }).click();

  await expect(rows(page)).toHaveCount(2);
  await expect(page).toHaveURL("/?site=s2");
});

test("the search narrows to matching serial numbers", async ({ page }) => {
  await page.goto("/");

  // Type part of a serial number; the list and the address follow.
  await page.getByRole("textbox", { name: "Search" }).fill("0005");

  await expect(rows(page)).toHaveCount(1);
  await expect(rows(page)).toContainText("SN-0005");
  await expect(page).toHaveURL("/?q=0005");
});

test("sorting by last seen puts the longest silent device first", async ({
  page,
}) => {
  await page.goto("/");

  await page.getByRole("columnheader", { name: "Last seen" }).click();

  // The device that never reported sorts after every date.
  await expect(rows(page).first()).toContainText("SN-0003");
  await expect(rows(page).last()).toContainText("never");
});

test("a device opens from the list and links back to its site", async ({
  page,
}) => {
  await page.goto("/");

  await page.getByRole("link", { name: "SN-0003" }).click();

  await expect(page).toHaveURL("/devices/d3");
  await expect(page.getByRole("heading", { name: "SN-0003" })).toBeVisible();
  // The site's name leads back to the devices of that site.
  await page.getByRole("link", { name: "Harbour" }).click();
  await expect(page).toHaveURL("/?site=s2");
  await expect(rows(page)).toHaveCount(2);
});

test("an unknown device says so", async ({ page }) => {
  // The fake inventory holds no device d9.
  await page.goto("/devices/d9");

  await expect(page.getByText("No device has the ID d9.")).toBeVisible();
});

test("the sites link to their devices", async ({ page }) => {
  await page.goto("/");

  // Go to the sites through the main navigation, then pick one.
  await page
    .getByRole("navigation", { name: "Main" })
    .getByRole("link", { name: "Sites" })
    .click();
  await page.getByRole("link", { name: "Depot" }).click();

  await expect(page).toHaveURL("/?site=s3");
  await expect(rows(page)).toHaveCount(2);
});

test("an unknown path says no page lives there", async ({ page }) => {
  await page.goto("/no/such/page");

  await expect(page.getByText("No page lives at")).toBeVisible();
  // The page offers the way back to the start.
  await page.getByRole("link", { name: "Go to the devices" }).click();
  await expect(page).toHaveURL("/");
});
