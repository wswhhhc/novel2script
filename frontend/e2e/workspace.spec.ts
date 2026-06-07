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

test.describe("Novel2Script 核心流程", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Novel2Script 工作台" })).toBeVisible();
  });

  test("完整创作流程：输入 → 识别 → 生成 → 校验 → 保存 → 导出", async ({ page }) => {
    // ── 填写基本信息 ──
    await page.getByRole("textbox", { name: "小说标题" }).fill("雨夜咖啡馆");
    await page.getByRole("combobox", { name: "剧本类型" }).selectOption("悬疑");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);

    // 字数统计应更新
    await expect(page.getByText(/字输入/)).toBeVisible();

    // ── 识别章节 ──
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();
    await expect(page.getByText("C001").first()).toBeVisible();

    // 识别后生成按钮应可用
    await expect(page.getByRole("button", { name: /生成剧本/ })).toBeEnabled();

    // ── 生成剧本 ──
    // 先清空标题测试错误提示
    await page.getByRole("textbox", { name: "小说标题" }).fill("");
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/生成剧本前请填写小说标题/)).toBeVisible();

    // 重新填标题
    await page.getByRole("textbox", { name: "小说标题" }).fill("雨夜咖啡馆");

    // 生成剧本
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible();
    await expect(page.getByText("Schema 校验通过", { exact: true })).toBeVisible();

    // ── 手动校验 ──
    // 校验按钮在 YAML 编辑器工具栏中
    await page.getByRole("button", { name: /校验/ }).click();
    await expect(page.getByText(/校验通过|校验失败/).first()).toBeVisible();

    // ── 保存项目 ──
    await page.getByRole("button", { name: "保存" }).first().click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByRole("button", { name: "保存" }).last().click();
    await expect(page.getByText("项目已保存：雨夜咖啡馆")).toBeVisible();
    await expect(page.getByText("当前项目：雨夜咖啡馆 · 已保存")).toBeVisible();

    // ── 创建版本快照 ──
    page.on("dialog", (dialog) => {
      if (dialog.message().includes("版本名称")) dialog.accept("v1.0");
      else if (dialog.message().includes("版本说明")) dialog.accept("初始版本");
      else dialog.accept();
    });
    await page.getByTitle("保存版本快照").click();
    await expect(page.getByText(/已保存版本：v1.0/)).toBeVisible();
    await expect(page.getByText("v1.0")).toBeVisible();

    // ── 导出剧本 ──
    for (const format of ["YAML", "JSON", "Markdown"]) {
      const downloadPromise = page.waitForEvent("download", { timeout: 10000 });
      await page.getByRole("button", { name: format }).click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain(".");
    }
  });

  test("边界情况：空输入时按钮禁用", async ({ page }) => {
    await expect(page.getByRole("button", { name: /识别章节/ })).toBeDisabled();
    await expect(page.getByRole("button", { name: /生成剧本/ })).toBeDisabled();
  });
});
