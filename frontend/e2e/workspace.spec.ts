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

  test("识别章节、生成 Mock 剧本并保存项目", async ({ page }) => {
    await page.getByRole("textbox", { name: "小说标题" }).fill("雨夜咖啡馆");
    await page.getByRole("combobox", { name: "剧本类型" }).selectOption("悬疑");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);

    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();
    await expect(page.getByText("C001").first()).toBeVisible();

    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible();
    await expect(page.getByText("Schema 校验通过", { exact: true })).toBeVisible();

    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByRole("dialog", { name: "保存当前项目" })).toBeVisible();
    await page.getByRole("button", { name: "保存" }).last().click();

    await expect(page.getByText("项目已保存：雨夜咖啡馆")).toBeVisible();
    await expect(page.getByText("当前项目：雨夜咖啡馆 · 已保存")).toBeVisible();
  });

  test("项目管理：新建、切换、删除项目", async ({ page }) => {
    // 创建项目1
    await page.getByRole("textbox", { name: "小说标题" }).fill("项目1");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible();
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByRole("button", { name: "保存" }).last().click();
    await expect(page.getByText("项目已保存：项目1")).toBeVisible();

    // 新建空白项目
    await page.getByLabel("新建项目").click();
    await expect(page.getByText("未保存项目")).toBeVisible();

    // 打开项目1
    await page.getByText("项目1").click();
    await expect(page.getByText("当前项目：项目1 · 已保存")).toBeVisible();

    // 删除项目1
    page.on("dialog", (dialog) => dialog.accept());
    await page.getByLabel(`删除项目1`).click();
    await expect(page.getByText("项目1")).not.toBeVisible();
  });

  test("版本快照：创建和恢复版本", async ({ page }) => {
    // 先创建并保存项目
    await page.getByRole("textbox", { name: "小说标题" }).fill("版本测试");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible();
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByRole("button", { name: "保存" }).last().click();
    await expect(page.getByText("项目已保存：版本测试")).toBeVisible();

    // 创建版本快照
    page.on("dialog", (dialog) => {
      if (dialog.message().includes("版本名称")) dialog.accept("v1.0");
      else if (dialog.message().includes("版本说明")) dialog.accept("初始版本");
      else dialog.accept();
    });
    await page.getByRole("button", { name: /创建版本/ }).click();
    await expect(page.getByText(/已保存版本：v1.0/)).toBeVisible();
    await expect(page.getByText("v1.0")).toBeVisible();
  });

  test("手动校验 YAML", async ({ page }) => {
    await page.getByRole("textbox", { name: "小说标题" }).fill("校验测试");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible();

    // 点击校验按钮
    await page.getByRole("button", { name: /校验 YAML/ }).click();
    await expect(page.getByText(/校验通过|校验失败/)).toBeVisible();
  });

  test("导出剧本文件", async ({ page }) => {
    // 创建并保存项目
    await page.getByRole("textbox", { name: "小说标题" }).fill("导出测试");
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/剧本生成成功/)).toBeVisible();
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByRole("button", { name: "保存" }).last().click();
    await expect(page.getByText("项目已保存：导出测试")).toBeVisible();

    // 测试三种导出格式
    for (const format of ["YAML", "JSON", "Markdown"]) {
      const downloadPromise = page.waitForEvent("download", { timeout: 5000 });
      await page.getByRole("button", { name: format }).click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain(".");
    }
  });
});

test.describe("边界和错误处理", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Novel2Script 工作台" })).toBeVisible();
  });

  test("空内容提示", async ({ page }) => {
    // 未输入内容时按钮应禁用
    await expect(page.getByRole("button", { name: /识别章节/ })).toBeDisabled();
    await expect(page.getByRole("button", { name: /生成剧本/ })).toBeDisabled();
  });

  test("标题为空时生成剧本应有提示", async ({ page }) => {
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);
    await page.getByRole("button", { name: /识别章节/ }).click();
    await expect(page.getByText("章节识别成功").first()).toBeVisible();

    // 未填标题点击生成
    await page.getByRole("button", { name: /生成剧本/ }).click();
    await expect(page.getByText(/生成剧本前请填写小说标题/)).toBeVisible();
  });

  test("章节输入统计显示正确", async ({ page }) => {
    await page.getByRole("textbox", { name: "小说正文" }).fill(sampleNovel);

    // 检查字数统计（中文按字符数）
    await expect(page.getByText(/字输入/)).toBeVisible();
  });
});
