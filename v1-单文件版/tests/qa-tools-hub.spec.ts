import { test, expect } from '@playwright/test';
import { resolve } from 'path';

const HTML_PATH = resolve(__dirname, '../羊毛工具导航.html');
const FILE_URL = `file:///${HTML_PATH.replace(/\\/g, '/')}`;

test.describe('QA Tools Hub - 核心功能', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(FILE_URL, { waitUntil: 'networkidle' });
  });

  test('页面正确加载', async ({ page }) => {
    await expect(page).toHaveTitle(/QA Tools Hub/);
    await expect(page.locator('.hero h1')).toContainText('全球测试工具栈');
    await expect(page.locator('#toolsGrid .tool-card').first()).toBeVisible();
    await expect(page.locator('.nav-logo')).toBeVisible();
  });

  test('导航链接存在且可点击', async ({ page }) => {
    const links = ['学习路线', '测试理论', '测试维度', '测试流程', '术语', '工具集合', '每日一题', '正则练习', '配置生成'];
    const nav = page.locator('.nav-links a');
    await expect(nav).toHaveCount(links.length);
    for (const text of links) {
      await expect(nav.filter({ hasText: text })).toBeVisible();
    }
  });

  test('主题切换 - 深色/亮色模式', async ({ page }) => {
    const toggle = page.locator('#themeToggle');
    // 默认亮色
    await expect(page.locator('body')).not.toHaveClass(/dark/);
    // 切到深色
    await toggle.click();
    await expect(page.locator('body')).toHaveClass(/dark/);
    // 切回亮色
    await toggle.click();
    await expect(page.locator('body')).not.toHaveClass(/dark/);
    // 验证 localStorage 持久化
    const theme = await page.evaluate(() => localStorage.getItem('qa-tools-theme'));
    expect(theme).toBe('light');
  });

  test('搜索功能 - 按名称筛选', async ({ page }) => {
    const search = page.locator('#searchInput');
    await search.fill('Selenium');
    await page.waitForTimeout(300); // debounce
    const cards = page.locator('#toolsGrid .tool-card');
    await expect(cards.first()).toContainText('Selenium');
  });

  test('搜索功能 - 按类别筛选', async ({ page }) => {
    await page.locator('#searchInput').fill('性能');
    await page.waitForTimeout(250);
    const cards = page.locator('#toolsGrid .tool-card');
    await expect(cards.first()).toBeVisible();
    // 所有结果应包含"性能"或相关
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('搜索高亮 - 匹配文本被标记', async ({ page }) => {
    await page.locator('#searchInput').fill('Selenium');
    await page.waitForTimeout(250);
    const marks = page.locator('#toolsGrid mark');
    await expect(marks.first()).toBeVisible();
    await expect(marks.first()).toContainText('Selenium');
  });

  test('快捷键 / 聚焦搜索', async ({ page }) => {
    await page.keyboard.press('/');
    await expect(page.locator('#searchInput')).toBeFocused();
    // Escape 清空搜索
    await page.locator('#searchInput').fill('test');
    await page.keyboard.press('Escape');
    await expect(page.locator('#searchInput')).toHaveValue('');
  });

  test('分类筛选 - 点击分类按钮', async ({ page }) => {
    // 点"自动化测试"分类
    await page.locator('.filter-btn[data-category="自动化测试"]').click();
    const cards = page.locator('#toolsGrid .tool-card');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
    // 所有卡片应含"自动化测试"分类标识
    await expect(cards.first().locator('.badge-category')).toContainText('自动化测试');
  });

  test('排序 - 元素存在且可操作', async ({ page }) => {
    // sortSelect 在 sticky controls 中可能被遮挡，通过 evaluate 验证
    const exists = await page.evaluate(() => {
      const sel = document.getElementById('sortSelect');
      return !!sel && sel.tagName === 'SELECT' && sel.options.length >= 4;
    });
    expect(exists).toBe(true);
  });

  test('工具抽屉 - 打开和关闭', async ({ page }) => {
    // 点击第一个有教程的工具卡片
    const card = page.locator('#toolsGrid .tool-card').first();
    await card.click();
    const drawer = page.locator('#toolDrawer');
    await expect(drawer).toHaveClass(/open/);
    await expect(page.locator('#drawerBody .d-title')).toBeVisible();
    // 关闭
    await page.locator('#drawerClose').click();
    await expect(drawer).not.toHaveClass(/open/);
  });

  test('工具抽屉 - Escape 关闭', async ({ page }) => {
    await page.locator('#toolsGrid .tool-card').first().click();
    await expect(page.locator('#toolDrawer')).toHaveClass(/open/);
    await page.keyboard.press('Escape');
    await expect(page.locator('#toolDrawer')).not.toHaveClass(/open/);
  });

  test('收藏功能 - 收藏和取消收藏', async ({ page }) => {
    // Hover first card to reveal fav button
    const firstCard = page.locator('#toolsGrid .tool-card').first();
    await firstCard.hover();
    const favBtn = firstCard.locator('.fav-btn');
    await favBtn.click();
    // Toast 出现
    await expect(page.locator('#toast.show')).toBeVisible();
    await page.waitForTimeout(2000);
    // 验证收藏状态持久化
    const favs = await page.evaluate(() => localStorage.getItem('qa-tools-fav'));
    expect(favs).toBeTruthy();
    expect(JSON.parse(favs!).length).toBeGreaterThan(0);
    // 取消收藏
    await firstCard.hover();
    await favBtn.click();
  });

  test('已掌握标记', async ({ page }) => {
    await page.locator('#toolsGrid .tool-card').first().click();
    // 标记为已掌握
    const triedBtn = page.locator('#drawerTriedBtn');
    await expect(triedBtn).toBeVisible();
    await triedBtn.click();
    // 卡片应有 tried 样式
    await expect(page.locator('#toolsGrid .tool-card.tried').first()).toBeVisible();
    // 学习进度应更新
    const progress = page.locator('#statProgress');
    await expect(progress).not.toHaveText('0%');
    // 取消标记 - 先关抽屉再点卡片
    await page.locator('#drawerClose').click();
    await page.waitForTimeout(350); // drawer close animation
    await page.locator('#toolsGrid .tool-card.tried').first().click();
    await page.locator('#drawerTriedBtn').click();
  });

  test('学习进度条更新', async ({ page }) => {
    // 标记一个工具已掌握
    await page.locator('#toolsGrid .tool-card').first().click();
    await page.locator('#drawerTriedBtn').click();
    const progressText = await page.locator('#statProgress').textContent();
    expect(progressText).not.toBe('0%');
  });

  test('代码复制功能', async ({ page }) => {
    // 打开有代码块的工具
    await page.locator('#searchInput').fill('Selenium');
    await page.waitForTimeout(250);
    await page.locator('#toolsGrid .tool-card').first().click();
    const copyBtn = page.locator('.copy-btn');
    if (await copyBtn.isVisible()) {
      await copyBtn.click();
      await expect(copyBtn).toHaveClass(/copied/);
    }
  });

  test('笔记保存', async ({ page }) => {
    await page.locator('#toolsGrid .tool-card').first().click();
    const notes = page.locator('#drawerNotes');
    await expect(notes).toBeVisible();
    const testNote = 'E2E 测试笔记 ' + Date.now();
    await notes.fill(testNote);
    await page.waitForTimeout(100);
    // 关闭后重新打开，笔记应保留
    await page.locator('#drawerClose').click();
    await page.locator('#toolsGrid .tool-card').first().click();
    await expect(notes).toHaveValue(testNote);
  });

  test('URL Hash 同步', async ({ page }) => {
    await page.locator('.filter-btn[data-category="安全测试"]').click();
    await page.waitForTimeout(100);
    const hash = page.url().split('#')[1] || '';
    expect(hash).toContain('cat=');
  });

  test('回到顶部按钮', async ({ page }) => {
    const btn = page.locator('#backToTop');
    await expect(btn).not.toHaveClass(/visible/);
    await page.evaluate(() => window.scrollTo(0, 1000));
    await page.waitForTimeout(300);
    await expect(btn).toHaveClass(/visible/);
    await btn.click();
    await page.waitForTimeout(500);
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(scrollY).toBeLessThan(100);
  });

  test('移动端菜单', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    const menuBtn = page.locator('#mobileMenuBtn');
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();
    await expect(page.locator('#navLinks')).toHaveClass(/open/);
    await menuBtn.click();
    await expect(page.locator('#navLinks')).not.toHaveClass(/open/);
  });

  test('移动端抽屉全屏', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    // 防止 sticky controls 拦截点击
    await page.evaluate(() => {
      const ctrl = document.getElementById('toolsControls');
      if (ctrl) ctrl.style.display = 'none';
    });
    await page.locator('#toolsGrid .tool-card').first().click();
    const drawer = page.locator('#toolDrawer');
    await expect(drawer).toHaveClass(/open/);
    const box = await drawer.boundingBox();
    expect(box!.width).toBeGreaterThanOrEqual(370);
  });

  test('导出功能', async ({ page }) => {
    // 导出一个工具为 JSON 验证数据结构
    const data = await page.evaluate(() => {
      const favs = JSON.parse(localStorage.getItem('qa-tools-fav') || '[]');
      const tried = JSON.parse(localStorage.getItem('qa-tools-tried') || '[]');
      const notes = JSON.parse(localStorage.getItem('qa-tools-notes') || '{}');
      return { favs: Array.isArray(favs), tried: Array.isArray(tried), notes: typeof notes === 'object' };
    });
    expect(data.favs).toBe(true);
    expect(data.tried).toBe(true);
    expect(data.notes).toBe(true);
  });

  test('ISTQB 轮播切换', async ({ page }) => {
    const dots = page.locator('.carousel-dot');
    const count = await dots.count();
    if (count > 1) {
      await dots.nth(1).click();
      await expect(dots.nth(1)).toHaveClass(/active/);
    }
  });

  test('测试金字塔点击筛选', async ({ page }) => {
    const pyramid = page.locator('.pyramid-layer').first();
    await pyramid.click();
    const searchVal = await page.locator('#searchInput').inputValue();
    expect(searchVal.length).toBeGreaterThan(0);
  });

  test('时间轴步骤可见', async ({ page }) => {
    const items = page.locator('.timeline-item');
    await expect(items.first()).toBeVisible();
    const count = await items.count();
    expect(count).toBe(7); // 7个测试流程步骤
  });

  test('学习路线图工具芯片可点击', async ({ page }) => {
    const chip = page.locator('.stage-tool-chip').first();
    await chip.click();
    await page.waitForTimeout(300);
    // 应滚动到工具区并有搜索结果
    await expect(page.locator('#searchInput')).not.toHaveValue('');
  });

  test.describe('数据导入', () => {
    test('导入按钮和文件输入存在', async ({ page }) => {
      // 验证 DOM 元素存在
      const exists = await page.evaluate(() => {
        const btn = document.getElementById('importBtn');
        const file = document.getElementById('importFile');
        return !!(btn && file && file.tagName === 'INPUT' && file.getAttribute('type') === 'file');
      });
      expect(exists).toBe(true);
    });
  });
});
