from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 收集控制台日志
    console_logs = []
    page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

    try:
        print("=== 测试 Word 预览行号跳转 ===\n")

        # 1. 打开应用
        page.goto('http://localhost:5174')
        page.wait_for_load_state('networkidle')
        print("✓ 应用已打开")

        # 2. 检查 localStorage 中的项目数据
        projects_data = page.evaluate("""() => {
            const projects = JSON.parse(localStorage.getItem('bid_review_projects') || '[]');
            return projects.map(p => ({
                name: p.name,
                id: p.id,
                sliceCount: p.slices?.length || 0,
                sliceMetadata: p.sliceMetadata?.map(s => ({
                    title: s.title,
                    startLine: s.startLine,
                    endLine: s.endLine
                })) || []
            }));
        }""")

        if not projects_data:
            print("⚠ 没有历史项目，请先创建一个项目")
            print("测试终止")
        else:
            print(f"✓ 找到 {len(projects_data)} 个项目")
            project = projects_data[0]
            print(f"  项目: {project['name']}")
            print(f"  切片数量: {project['sliceCount']}")

            if project['sliceMetadata']:
                print(f"  切片元数据:")
                for i, sm in enumerate(project['sliceMetadata'][:5]):  # 只显示前5个
                    print(f"    [{i}] {sm['title']}: startLine={sm['startLine']}, endLine={sm['endLine']}")

            # 3. 检查 store 中的数据
            store_data = page.evaluate("""() => {
                const store = window.__pinia?.state?.value?.app;
                if (!store) return null;
                return {
                    bidSlices: store.bidSlices?.length || 0,
                    sliceMetadata: store.sliceMetadata?.length || 0,
                    currentProjectId: store.currentProjectId
                };
            }""")

            print(f"\n✓ Store 数据:")
            print(f"  bidSlices: {store_data['bidSlices']}")
            print(f"  sliceMetadata: {store_data['sliceMetadata']}")

            # 4. 检查 Word 预览中的 data-line 属性
            line_numbers = page.evaluate("""() => {
                const elements = document.querySelectorAll('[data-line]');
                const lines = [];
                elements.forEach((el, idx) => {
                    if (idx < 100) {  // 只取前100个
                        lines.push({
                            line: parseInt(el.getAttribute('data-line')),
                            tag: el.tagName,
                            text: el.textContent?.substring(0, 50).replace(/\\n/g, ' ')
                        });
                    }
                });
                return lines;
            }""")

            print(f"\n✓ Word 预览中的 data-line 属性 (前20个):")
            for ln in line_numbers[:20]:
                print(f"  data-line={ln['line']}: <{ln['tag']}> {ln['text'][:40]}...")

            # 5. 检查切片详情的行号与 Word 预览的对应关系
            print(f"\n=== 切片详情行号 vs Word 预览 data-line ===")

            # 获取切片元数据中的 startLine
            slice_meta_startlines = [sm['startLine'] for sm in project['sliceMetadata'][:6]]

            # 获取 Word 预览中对应的元素
            for start_line in slice_meta_startlines:
                matching = [ln for ln in line_numbers if ln['line'] == start_line]
                if matching:
                    print(f"  startLine={start_line}: ✅ 找到 <{matching[0]['tag']}> \"{matching[0]['text'][:30]}...\"")
                else:
                    print(f"  startLine={start_line}: ❌ 未找到对应的 data-line 元素")

            # 6. 测试点击跳转功能
            print(f"\n=== 测试点击跳转 ===")

            # 模拟点击切片详情的第80行（如果存在）
            test_line = 80
            target = page.locator(f'[data-line="{test_line}"]')
            if target.count() > 0:
                # 获取元素位置
                box = target.first.bounding_box()
                print(f"  点击 data-line={test_line}")
                print(f"  元素位置: {box}")

                # 点击元素
                target.first.click()
                page.wait_for_timeout(500)

                # 检查是否有高亮效果
                highlighted = page.evaluate("""() => {
                    const el = document.querySelector('.highlight-line, [style*="background"]');
                    return el ? {
                        tag: el.tagName,
                        text: el.textContent?.substring(0, 30)
                    } : null;
                }""")

                if highlighted:
                    print(f"  高亮元素: <{highlighted['tag']}> \"{highlighted['text']}...\"")
                else:
                    print(f"  未检测到高亮")
            else:
                print(f"  data-line={test_line} 不存在")

        # 打印控制台日志（调试用）
        if console_logs:
            print('\n--- 控制台日志 ---')
            for log in console_logs[-20:]:  # 只打印最后20条
                print(log)

    except Exception as e:
        print(f'测试失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
