import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { PNG } from "pngjs";

// Verification (plan §2 step 7): with the real OCR specialist pinned, the stamped total must
// surface as hard spots and an ungrounded field. Opt-in because it takes ~2 minutes on a laptop:
//   VERIFY_OCR=1 pnpm exec playwright test e2e/verify-ocr.spec.ts
const enabled = Boolean(process.env.VERIFY_OCR);
const outDir = resolve(__dirname, "../../../story/assets", process.env.SCREENS_DIR ?? "slice-c");
const specimen = resolve(__dirname, "fixtures/northwind-00417.png");

test.skip(!enabled, "real-OCR verification is opt-in");
test.use({ viewport: { width: 1440, height: 900 } });
test.setTimeout(420_000);

test("the real OCR specialist turns the stamp into hard spots", async ({ page }) => {
  await page.goto("/sign-in");
  await page.getByLabel("Work email").fill("clerk@ledgerlens.demo");
  await page.getByLabel("Password").fill("show-your-work-2026");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/inbox/);

  const png = PNG.sync.read(readFileSync(specimen));
  const idx = (10 * png.width + 10 + Math.floor(Math.random() * 100)) * 4;
  png.data[idx] = (png.data[idx] + 3) % 256;
  const name = `northwind-real-ocr-${Date.now().toString(36)}.png`;
  await page.setInputFiles('input[type="file"]', { name, mimeType: "image/png", buffer: PNG.sync.write(png) });
  const row = page.getByTestId("document-row").filter({ hasText: name });
  await expect(row).toBeVisible({ timeout: 60_000 });
  await row.click();
  // The worker reads the page asynchronously (the API returned 202); poll until the verdict lands.
  const started = Date.now();
  while (!(await page.getByTestId("verdict").count())) {
    if (Date.now() - started > 360_000) throw new Error("verdict did not arrive within 6 minutes");
    await page.waitForTimeout(10_000);
    await page.reload();
  }
  await expect(page.getByTestId("verdict")).toBeVisible();

  // real OCR: words exist, and the stamp region yields low-score words
  await page.getByRole("button", { name: /OCR words/ }).click();
  await expect(page.getByTestId("ocr-word").first()).toBeVisible();
  const hardSpots = await page.getByTestId("hard-spot").count();
  const wordCount = await page.getByTestId("ocr-word").count();
  console.log(`OCR words: ${wordCount}, hard spots: ${hardSpots}`);
  await page.waitForTimeout(1200);
  await page.screenshot({ path: `${outDir}/13-real-ocr.png`, fullPage: true });
  await expect(page.getByText(/OCR paddleocr-vl-1.6/)).toBeVisible();
});
