import { expect, test } from "@playwright/test";

const sampleNovel = `第一章 雨夜相逢
雨夜里，林晓推开午夜咖啡馆的门，发现旧友陈默正在角落里等她。
陈默递来一只旧怀表，说这和三年前失踪的剧本有关。

第二章 怀表线索
林晓检查怀表背面的刻字，确认它来自父亲曾经工作的剧团。
两人决定回到废弃剧场寻找线索。

第三章 剧场回声
废弃剧场里传来录音机的声音，旧剧本被藏在舞台地板下面。
林晓意识到父亲当年留下的秘密，正是新故事的开端。`;

async function enterWorkspace(page: import("@playwright/test").Page) {
  // 工作区弹窗会在首次访问时弹出
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible({ timeout: 5000 });

  // 填入工作区名称
  const input = page.getByPlaceholder("例如：my-project 或 张三");
  await input.waitFor({ state: "visible" });
  await input.fill("e2e-test");

  // 点击进入（确保按钮已启用）
  const submitBtn = page.getByRole("button", { name: "进入工作区" });
  await expect(submitBtn).toBeEnabled();
  await submitBtn.click();

  // 等待弹窗完全消失
  await page.waitForSelector(".modal-backdrop", { state: "detached", timeout: 5000 });
}

test.describe("Novel2Script", () => {
  test("核心创作流程：输入 → 识别 → 生成 → 保存", async ({ page }) => {
    await page.goto("/");
    await enterWorkspace(page);
    await expect(page.getByRole("heading", { name: "Novel2Script 工作台" })).toBeVisible();

    // 填写基本信息
    await page.getByRole("textbox", { name: "小说标题" }).fill("雨夜咖啡馆");
    await page.getByRole("combobox", { name: "剧本类型" }).selectOption("悬疑");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);

    // 识别章节
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible({ timeout: 10000 });

    // 生成剧本
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible({ timeout: 20000 });

    // 保存项目
    await page.getByRole("button", { name: "保存" }).first().click();
    await expect(page.getByRole("dialog")).toBeVisible({ timeout: 5000 });
    await page.getByRole("button", { name: "保存" }).last().click();
    await expect(page.getByText(/项目已保存/)).toBeVisible({ timeout: 10000 });
  });

  test("边界情况：空输入时按钮禁用", async ({ page }) => {
    await page.goto("/");
    await enterWorkspace(page);
    await expect(page.getByRole("heading", { name: "Novel2Script 工作台" })).toBeVisible();
    await expect(page.getByRole("button", { name: /识别章节/ })).toBeDisabled();
    await expect(page.getByRole("button", { name: /生成剧本/ })).toBeDisabled();
  });
});
