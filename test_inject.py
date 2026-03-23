from playwright.sync_api import sync_playwright

html_path = '/Users/kyle/Projects/投标文件审核/test_inject.html'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 使用 file:// URL
    page.goto(f'file://{html_path}')
    page.wait_for_load_state('domcontentloaded')

    # 检查结构
    result = page.evaluate("""() => {
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

        // 检查 h2 "身份证明" 在哪里
        const heading2 = preview.querySelector('h2');
        const heading1 = preview.querySelector('h1');

        return {
            totalElements: elements.length,
            elements: elements.slice(0, 10),
            firstH1: heading1 ? {
                text: heading1.textContent.substring(0, 30),
                dataLine: heading1.getAttribute('data-line')
            } : null,
            firstH2: heading2 ? {
                text: heading2.textContent.substring(0, 30),
                dataLine: heading2.getAttribute('data-line')
            } : null
        };
    }""")

    print('=== 测试结果 ===')
    print(f'总元素数: {result.get("totalElements", 0)}')
    print(f'\n前10个元素:')
    for el in result.get('elements', []):
        print(f"  data-line={el['dataLine']}: <{el['tag']}> {el['text']}...")
    print(f'\nh1 "投标函": data-line={result.get("firstH1", {}).get("dataLine")}')
    print(f'h2 "身份证明": data-line={result.get("firstH2", {}).get("dataLine")}')

    print('\n=== 问题分析 ===')
    h2_data_line = result.get('firstH2', {}).get('dataLine')
    if h2_data_line and h2_data_line != '80':
        print(f'❌ h2 "身份证明" 的 data-line={h2_data_line}，但应该是 80')
        print('   原因：docx-preview 渲染时没有保留原始注释标记，所以使用顺序编号')
        print('   这就是为什么点击"第80行"跳转到错误位置')
    elif h2_data_line == '80':
        print('✅ h2 "身份证明" 的 data-line=80，与预期一致')

    browser.close()
