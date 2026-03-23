from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    console_msgs = []
    page.on('console', lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

    page_errors = []
    page.on('pageerror', lambda err: page_errors.append(str(err)))

    # 监听网络请求
    failed_requests = []
    def on_response(response):
        if response.status >= 400:
            failed_requests.append({
                'url': response.url,
                'status': response.status,
                'body': response.text[:500] if response.status >= 500 else ''
            })

    page.on('response', on_response)

    try:
        print("=== 打开应用并调试 ===\n")

        page.goto('http://localhost:5174', timeout=30000)
        page.wait_for_load_state('networkidle', timeout=30000)
        print("✓ 应用已加载")

        page.wait_for_timeout(3000)

        # 打印失败的请求
        if failed_requests:
            print("\n=== 失败的请求 ===")
            for req in failed_requests:
                print(f"  {req['status']}: {req['url']}")
                if req['body']:
                    print(f"    响应内容: {req['body'][:200]}")

        # 打印控制台消息
        if console_msgs:
            print("\n=== 控制台消息 ===")
            for msg in console_msgs:
                print(f"  {msg}")

        # 打印错误
        if page_errors:
            print("\n=== 页面错误 ===")
            for err in page_errors:
                print(f"  ❌ {err}")

        page.screenshot(path='/tmp/debug_screenshot.png', full_page=True)
        print("\n✓ 截图已保存")

        input("\n按 Enter 键关闭...")

    except Exception as e:
        print(f'测试失败: {e}')
        import traceback
        traceback.print_exc()
        page.screenshot(path='/tmp/error_screenshot.png')

    finally:
        browser.close()
