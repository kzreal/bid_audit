const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // 创建临时 HTML 来模拟 docx-preview 的输出
  const html = fs.readFileSync('/Users/kyle/Projects/投标文件审核/test_inject.html', 'utf8');

  // 直接使用本地文件
  await page.setContent(html);
  await page.waitForLoadState('domcontentloaded');

  // 检查结构
  const result = await page.evaluate(() => {
    const preview = document.querySelector('#word-preview');
    if (!preview) return { error: 'No preview' };

    const sections = preview.querySelectorAll('section');
    const elements = [];

    let lineNumber = 1;
    sections.forEach((section, sectionIndex) => {
      section.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, img, figure').forEach((el) => {
        const text = el.textContent?.trim() || '';
        if (!text && el.tagName !== 'IMG' && el.tagName !== 'FIGURE') return;

        // 当前逻辑：直接用递增的 lineNumber
        el.setAttribute('data-line', lineNumber);
        elements.push({
          dataLine: lineNumber,
          tag: el.tagName,
          text: text.substring(0, 40)
        });
        lineNumber++;
      });
    });

    // 检查 # 80 和 # 2 在哪里
    const heading2 = preview.querySelector('h2');
    const heading1 = preview.querySelector('h1');

    return {
      totalElements: elements.length,
      elements: elements,
      firstH1: heading1 ? {
        text: heading1.textContent.substring(0, 30),
        dataLine: heading1.getAttribute('data-line')
      } : null,
      firstH2: heading2 ? {
        text: heading2.textContent.substring(0, 30),
        dataLine: heading2.getAttribute('data-line')
      } : null
    };
  });

  console.log('Result:', JSON.stringify(result, null, 2));

  await browser.close();
})();
