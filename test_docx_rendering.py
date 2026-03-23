from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    console_logs = []
    page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

    try:
        print("=== 诊断 Word 预览行号问题 ===\n")

        # 打开应用
        page.goto('http://localhost:5174')
        page.wait_for_load_state('networkidle')
        print("✓ 应用已打开")

        # 检查是否有项目
        projects = page.evaluate("""() => {
            return JSON.parse(localStorage.getItem('bid_review_projects') || '[]');
        }""")

        if not projects:
            print("⚠ 没有项目，跳过测试")
        else:
            project = projects[0]
            print(f"✓ 项目: {project['name']}")

            # 检查 sliceMetadata
            metadata = project.get('sliceMetadata', [])
            if metadata:
                print(f"\n切片元数据 (共 {len(metadata)} 个):")
                for i, m in enumerate(metadata[:5]):
                    print(f"  [{i}] '{m['title']}': startLine={m['startLine']}, endLine={m['endLine']}")

                # 找到 "二、法定代表人身份证明" 的 startLine
                target_slice = None
                for m in metadata:
                    if '身份证明' in m.get('title', ''):
                        target_slice = m
                        break

                if target_slice:
                    print(f"\n目标切片: '{target_slice['title']}'")
                    print(f"  startLine = {target_slice['startLine']}")
                    print(f"  endLine = {target_slice['endLine']}")

            # 检查 Word 预览中的元素
            print("\n=== Word 预览中的元素 ===")
            elements_info = page.evaluate("""() => {
                const preview = document.querySelector('#word-preview');
                if (!preview) return { error: 'No #word-preview found' };

                const sections = preview.querySelectorAll('section');
                const elements = [];

                // 获取前30个有 data-line 的元素
                let count = 0;
                for (const section of sections) {
                    const els = section.querySelectorAll('[data-line]');
                    for (const el of els) {
                        if (count < 30) {
                            elements.push({
                                dataLine: el.getAttribute('data-line'),
                                tag: el.tagName,
                                text: el.textContent?.substring(0, 40).replace(/\\n/g, ' ')
                            });
                            count++;
                        }
                    }
                }

                // 特别检查 startLine=80 附近
                const targetEl = preview.querySelector('[data-line="80"]');
                return {
                    totalSections: sections.length,
                    totalElements: count,
                    first20: elements.slice(0, 20),
                    targetAt80: targetEl ? {
                        tag: targetEl.tagName,
                        text: targetEl.textContent?.substring(0, 50)
                    } : null
                };
            }""")

            if 'error' in elements_info:
                print(f"  错误: {elements_info['error']}")
            else:
                print(f"  Section 数量: {elements_info['totalSections']}")
                print(f"  有 data-line 的元素数: {elements_info['totalElements']}")

                if elements_info.get('first20'):
                    print("\n  前20个元素 (data-line, tag, text[:40]):")
                    for el in elements_info['first20']:
                        print(f"    {el['dataLine']}: <{el['tag']}> {el['text']}...")

                if elements_info.get('targetAt80'):
                    print(f"\n  data-line=80 的元素: <{elements_info['targetAt80']['tag']}> {elements_info['targetAt80']['text']}...")
                else:
                    print(f"\n  ⚠ 没有找到 data-line=80 的元素")

        # 打印控制台日志
        if console_logs:
            print('\n--- 相关控制台日志 ---')
            for log in console_logs:
                if 'sections' in log.lower() or 'line' in log.lower() or 'render' in log.lower():
                    print(log)

    except Exception as e:
        print(f'测试失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
