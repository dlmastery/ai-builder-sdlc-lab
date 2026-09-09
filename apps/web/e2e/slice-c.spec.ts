import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Slice C proof (plan §2, step 7): correct → approve → the correction is visible; the review
// filter works; signals appear in Production after the observe job.

const specimen = resolve(__dirname, "fixtures/northwind-00417.png");

async function signUp(page: Page, suffix: string) {
  await page.goto("/sign-up");
  await page.getByLabel("Work email").fill(`lead+${suffix}@acme.io`);
  await page.getByLabel("Password").fill("a-long-enough-password");
  await page.getByLabel("Company").fill(`Acme ${suffix}`);
  await page.getByRole("button", { name: "Create workspace" }).click();
  await expect(page).toHaveURL(/\/inbox/);
}

async function upload(page: Page, name: string) {
  await page.setInputFiles('input[type="file"]', {
    name,
    mimeType: "image/png",
    buffer: readFileSync(specimen),
  });
  await expect(page.getByTestId("document-row").first()).toBeVisible();
}

test("correct a field, approve, and see the correction persist", async ({ page }) => {
  await signUp(page, `c${Date.now().toString(36)}`);
  await upload(page, "northwind-00417.png");
  await page.getByTestId("document-row").first().click();
  await expect(page.getByTestId("verdict")).toContainText(/needs review/i);

  // gate 5 (chapter 16): the default review screen is the calm document, and what needs a
  // person sits in a strip under the verdict with its edit right there — the correction is
  // made from the strip, above the page, never from the reference list below it
  await expect(page.getByTestId("needs-you")).toContainText(/total/i);
  await page.getByTestId("strip-correct-total").click();
  const input = page.getByLabel("Correct total");
  await input.fill("1,171.20");
  await input.press("Enter");
  await expect(page.getByTestId("readout-total")).toContainText("1,171.20");
  await expect(page.getByTestId("readout-total")).toContainText("1,177.20"); // struck-through old value

  await page.getByTestId("approve").click();
  await expect(page.getByTestId("verdict")).toContainText(/approved/i);
  await expect(page.getByTestId("verdict")).toContainText(/1 corrected/);

  await page.goto("/inbox?status=approved");
  await expect(page.getByTestId("document-row")).toHaveCount(1);
  await page.goto("/inbox?status=needs_review");
  await expect(page.getByTestId("document-row")).toHaveCount(0);
});

test("the evidence layers can be toggled and the pricing checkout completes in fake mode", async ({ page }) => {
  await signUp(page, `l${Date.now().toString(36)}`);
  await upload(page, "northwind-00417.png");
  await page.getByTestId("document-row").first().click();
  await expect(page.getByTestId("field-box").first()).toBeVisible();
  // the toggle by its id, not its label — the label is copy the design loop rewrites
  // ("where each value was found", round 12); the behaviour under test is the layer toggling
  await page.getByTestId("layer-fields").click();
  await expect(page.getByTestId("field-box")).toHaveCount(0);

  await page.goto("/pricing");
  await page.getByRole("link", { name: "Start on Team" }).click();
  await expect(page).toHaveURL(/\/billing\/start\?plan=team/);
  await page.getByTestId("checkout").click();
  await expect(page).toHaveURL(/\/production/);
  await expect(page.getByText(/Team · fake/)).toBeVisible();
});
