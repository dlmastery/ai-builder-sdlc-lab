import { expect, test } from "@playwright/test";

// Opt-in diagnostic: open the Next.js dev overlay's issue badge and print what it says.
//   DEVISSUE=1 pnpm exec playwright test e2e/devissue.spec.ts
test.skip(!process.env.DEVISSUE, "diagnostic only");

test("read the dev overlay issue", async ({ page }) => {
  await page.goto("/sign-in");
  await page.getByLabel("Work email").fill("data@ledgerlens.demo");
  await page.getByLabel("Password").fill("show-your-work-2026");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/inbox/);
  await page.getByTestId("document-row").first().click();
  await expect(page.getByTestId("verdict")).toBeVisible();
  const badge = page.locator("nextjs-portal").first();
  await page.waitForTimeout(1500);
  const shadowText = await badge.evaluate((el) => el.shadowRoot?.textContent ?? "");
  console.log("DEV OVERLAY TEXT:", shadowText.slice(0, 200));
  const issueButton = badge.locator("button", { hasText: /Issue/ }).first();
  if (await issueButton.count()) {
    await issueButton.click();
    await page.waitForTimeout(800);
    const text = await badge.evaluate((el) => el.shadowRoot?.textContent ?? "");
    console.log("DEV OVERLAY ISSUE:", text.slice(0, 1200));
  }
});
