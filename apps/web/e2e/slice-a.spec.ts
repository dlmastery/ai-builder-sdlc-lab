import { expect, test, type Page } from "@playwright/test";
import { PNG } from "pngjs";

// Slice A proof (plan §2, step 9): sign in, upload, see the stub's overlays; home and pricing
// render for an anonymous visitor; protected routes redirect.

function blankPng(width = 640, height = 900): Buffer {
  const png = new PNG({ width, height });
  png.data.fill(255);
  return PNG.sync.write(png);
}

async function signUp(page: Page, suffix: string) {
  await page.goto("/sign-up");
  await page.getByLabel("Work email").fill(`lead+${suffix}@acme.io`);
  await page.getByLabel("Password").fill("a-long-enough-password");
  await page.getByLabel("Company").fill(`Acme ${suffix}`);
  await page.getByRole("button", { name: "Create workspace" }).click();
  await expect(page).toHaveURL(/\/inbox/);
}

test("home page tells the story and offers sign-up", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(/shows its work/i);
  await expect(page.getByRole("link", { name: /pricing/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /start/i }).first()).toBeVisible();
});

test("pricing page lists three plans from the API", async ({ page }) => {
  await page.goto("/pricing");
  await expect(page.getByTestId("plan-card")).toHaveCount(3);
  await expect(page.getByRole("heading", { name: "Sovereign" })).toBeVisible();
});

test("anonymous visitor is redirected from the inbox to sign-in", async ({ page }) => {
  await page.goto("/inbox");
  await expect(page).toHaveURL(/\/sign-in/);
});

test("sign up, upload, and see the stub's transparency overlays", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text());
  });
  page.on("pageerror", (e) => consoleErrors.push(e.message));

  await signUp(page, Date.now().toString(36));

  await expect(page.getByTestId("inbox-empty")).toBeVisible();

  await page.setInputFiles('input[type="file"]', {
    name: "invoice.png",
    mimeType: "image/png",
    buffer: blankPng(),
  });

  await expect(page.getByTestId("document-row")).toHaveCount(1);
  await page.getByTestId("document-row").first().click();
  await expect(page).toHaveURL(/\/documents\//);

  // Evidence layers from the stub extractor, rendered from rows — not from the fixture.
  await expect(page.getByTestId("field-box")).not.toHaveCount(0);
  await expect(page.getByTestId("readout-total")).toContainText("1,177.20");
  await expect(page.getByTestId("ledger-row")).not.toHaveCount(0);
  await expect(page.getByTestId("verdict")).toContainText(/needs review/i);
  await expect(page.getByText(/stub/i).first()).toBeVisible();

  // Only required fields below threshold read as fault; other low-confidence fields are caution.
  await expect(page.locator('[data-testid="field-box"][data-tone="fault"]')).toHaveCount(1);
  await expect(page.locator('[data-testid="field-box"][data-tone="caution"]')).not.toHaveCount(0);

  expect(consoleErrors, consoleErrors.join("\n")).toEqual([]);
});

test("models and production views show the pinned stub", async ({ page }) => {
  await signUp(page, `m${Date.now().toString(36)}`);
  await page.goto("/models");
  await expect(page.getByTestId("model-row").filter({ hasText: "stub" }).first()).toBeVisible();
  await page.goto("/production");
  await expect(page.getByTestId("pinned-extractor")).toContainText("stub");
});
