import { expect, test } from "@playwright/test";

// Opt-in diagnostic: open the Next.js dev overlay's issue badge and print the issue text.
//   DEVISSUE=1 pnpm exec playwright test e2e/devissue.spec.ts
test.skip(!process.env.DEVISSUE, "diagnostic only");

test("read the dev overlay issue", async ({ page }) => {
  const consoleLines: string[] = [];
  page.on("console", (m) => consoleLines.push(`${m.type()}: ${m.text().slice(0, 300)}`));
  await page.goto("/sign-in");
  await page.getByLabel("Work email").fill("data@ledgerlens.demo");
  await page.getByLabel("Password").fill("show-your-work-2026");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/inbox/);
  await page.getByTestId("document-row").first().click();
  await expect(page.getByTestId("verdict")).toBeVisible();
  await page.waitForTimeout(2000);
  const portal = page.locator("nextjs-portal").first();
  const badge = portal.locator("button", { hasText: /Issue/ }).first();
  if (await badge.count()) {
    await badge.click();
    await page.waitForTimeout(1000);
    const text = await portal.evaluate((el) => {
      const root = el.shadowRoot;
      if (!root) return "";
      const dialog = root.querySelector("[role='dialog']") ?? root;
      return (dialog as HTMLElement).innerText ?? dialog.textContent ?? "";
    });
    console.log("DEV OVERLAY ISSUE:\n" + text.slice(0, 1500));
  } else {
    console.log("DEV OVERLAY: no issue badge");
  }
  console.log("CONSOLE (warnings/errors):\n" + consoleLines.filter((l) => /^(warning|error)/.test(l)).join("\n"));
});
