import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Captures the running product for the critic loop and the story chapters. Opt-in:
//   SCREENS=1 SCREENS_DIR=slice-c pnpm exec playwright test e2e/screens.spec.ts
// Writes PNGs to story/assets/<SCREENS_DIR>/ (default slice-a). Signs in as the demo data lead
// (an operator) so the observe job can be triggered for the Production screen.
const enabled = Boolean(process.env.SCREENS);
const outDir = resolve(__dirname, "../../../story/assets", process.env.SCREENS_DIR ?? "slice-a");
const specimen = resolve(__dirname, "fixtures/northwind-00417.png");

test.skip(!enabled, "screenshot capture is opt-in");

test.use({ viewport: { width: 1440, height: 900 } });

test("capture the product end to end", async ({ page, request }) => {
  await page.goto("/");
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${outDir}/01-home.png`, fullPage: true });

  await page.goto("/pricing");
  await page.screenshot({ path: `${outDir}/02-pricing.png`, fullPage: true });

  await page.goto("/sign-in");
  await page.screenshot({ path: `${outDir}/03-sign-in.png` });
  await page.getByLabel("Work email").fill("data@ledgerlens.demo");
  await page.getByLabel("Password").fill("show-your-work-2026");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/inbox/);
  await page.screenshot({ path: `${outDir}/04-inbox.png` });

  await page.setInputFiles('input[type="file"]', {
    name: `northwind-${Date.now().toString(36)}.png`,
    mimeType: "image/png",
    buffer: readFileSync(specimen),
  });
  await expect(page.getByTestId("document-row").first()).toBeVisible();
  await page.screenshot({ path: `${outDir}/05-inbox.png` });

  await page.getByTestId("document-row").first().click();
  await expect(page.getByTestId("verdict")).toBeVisible();
  await page.waitForTimeout(1200);
  await page.screenshot({ path: `${outDir}/06-transparency.png`, fullPage: true });

  // the loop: correct the stamped total, approve, then observe
  await page.getByTestId("correct-total").click();
  const input = page.getByLabel("Correct total");
  await input.fill("1,171.20");
  await page.screenshot({ path: `${outDir}/07-correcting.png` });
  await input.press("Enter");
  await expect(page.getByTestId("readout-total")).toContainText("1,171.20");
  await page.getByTestId("approve").click();
  await expect(page.getByTestId("verdict")).toContainText(/approved/i);
  await page.screenshot({ path: `${outDir}/08-approved.png`, fullPage: true });

  const csrf = (await (await request.get("/api/auth/me")).json()).csrf_token as string;
  const observe = await request.post("/api/jobs", {
    headers: { "X-CSRF-Token": csrf },
    data: { kind: "observe", payload: { min_reviews: 1, floor: 0.99 } },
  });
  expect(observe.ok()).toBeTruthy();

  await page.goto("/vendors");
  await page.screenshot({ path: `${outDir}/09-vendors.png` });
  await page.goto("/models");
  await page.screenshot({ path: `${outDir}/10-models.png`, fullPage: true });
  const firstModel = page.getByTestId("model-row").filter({ hasText: "lora" }).first();
  if (await firstModel.count()) {
    await firstModel.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: `${outDir}/11-model-detail.png`, fullPage: true });
  }
  await page.goto("/production");
  await page.screenshot({ path: `${outDir}/12-production.png`, fullPage: true });
});
