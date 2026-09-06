import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Captures the running shell for the critic loop and the story chapter. Opt-in:
//   SCREENS=1 pnpm exec playwright test e2e/screens.spec.ts
// Writes PNGs to story/assets/<SCREENS_DIR>/ (default slice-a).
const enabled = Boolean(process.env.SCREENS);
const outDir = resolve(__dirname, "../../../story/assets", process.env.SCREENS_DIR ?? "slice-a");
const specimen = resolve(__dirname, "fixtures/northwind-00417.png");

test.skip(!enabled, "screenshot capture is opt-in");

test.use({ viewport: { width: 1440, height: 900 } });

test("capture home, pricing, sign-in, inbox, transparency, models, production", async ({ page }) => {
  await page.goto("/");
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${outDir}/01-home.png`, fullPage: true });

  await page.goto("/pricing");
  await page.screenshot({ path: `${outDir}/02-pricing.png`, fullPage: true });

  await page.goto("/sign-in");
  await page.screenshot({ path: `${outDir}/03-sign-in.png` });
  await page.getByLabel("Work email").fill("clerk@ledgerlens.demo");
  await page.getByLabel("Password").fill("show-your-work-2026");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/inbox/);
  await page.screenshot({ path: `${outDir}/04-inbox-empty.png` });

  await page.setInputFiles('input[type="file"]', {
    name: "northwind-00417.png",
    mimeType: "image/png",
    buffer: readFileSync(specimen),
  });
  await expect(page.getByTestId("document-row").first()).toBeVisible();
  await page.screenshot({ path: `${outDir}/05-inbox.png` });

  await page.getByTestId("document-row").first().click();
  await expect(page.getByTestId("verdict")).toBeVisible();
  await page.waitForTimeout(1200);
  await page.screenshot({ path: `${outDir}/06-transparency.png`, fullPage: true });

  await page.goto("/models");
  await page.screenshot({ path: `${outDir}/07-models.png` });
  await page.goto("/production");
  await page.screenshot({ path: `${outDir}/08-production.png` });
});
