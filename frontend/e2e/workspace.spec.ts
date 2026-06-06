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

test("识别章节、生成 Mock 剧本并保存项目", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Novel2Script 工作台" })).toBeVisible();

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
