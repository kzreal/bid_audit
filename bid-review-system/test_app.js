// 简单的测试脚本来验证应用结构
const fs = require('fs');
const path = require('path');

console.log('检查 Vue 应用文件...\n');

// 1. 检查 main.js
const mainJsPath = path.join(__dirname, 'src/main.js');
if (fs.existsSync(mainJsPath)) {
  const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
  console.log('✓ main.js 存在');
  console.log('  - 导入 App.vue:', mainJsContent.includes('import App from \'./App.vue\''));
  console.log('  - 导入 Pinia:', mainJsContent.includes('import { createPinia } from \'pinia\''));
  console.log('  - 挂载到 #app:', mainJsContent.includes('app.mount(\'#app\')'));
} else {
  console.log('✗ main.js 不存在');
}

// 2. 检查 App.vue
const appVuePath = path.join(__dirname, 'src/App.vue');
if (fs.existsSync(appVuePath)) {
  const appVueContent = fs.readFileSync(appVuePath, 'utf8');
  console.log('\n✓ App.vue 存在');
  console.log('  - 导入 Layout 组件:', appVueContent.includes('import Layout from \'./components/Layout.vue\''));
  console.log('  - 使用 Layout 组件:', appVueContent.includes('<Layout />'));
} else {
  console.log('\n✗ App.vue 不存在');
}

// 3. 检查 Layout.vue
const layoutVuePath = path.join(__dirname, 'src/components/Layout.vue');
if (fs.existsSync(layoutVuePath)) {
  console.log('\n✓ Layout.vue 存在');
} else {
  console.log('\n✗ Layout.vue 不存在');
}

// 4. 检查 style.css
const styleCssPath = path.join(__dirname, 'src/style.css');
if (fs.existsSync(styleCssPath)) {
  const styleCssContent = fs.readFileSync(styleCssPath, 'utf8');
  console.log('\n✓ style.css 存在');
  console.log('  - Tailwind base:', styleCssContent.includes('@tailwind base'));
  console.log('  - Tailwind components:', styleCssContent.includes('@tailwind components'));
  console.log('  - Tailwind utilities:', styleCssContent.includes('@tailwind utilities'));
} else {
  console.log('\n✗ style.css 不存在');
}

// 5. 检查配置文件
console.log('\n配置文件检查:');
console.log('✓ tailwind.config.js:', fs.existsSync(path.join(__dirname, 'tailwind.config.js')));
console.log('✓ postcss.config.js:', fs.existsSync(path.join(__dirname, 'postcss.config.js')));
console.log('✓ vite.config.js:', fs.existsSync(path.join(__dirname, 'vite.config.js')));

// 6. 检查 index.html
const indexHtmlPath = path.join(__dirname, 'index.html');
if (fs.existsSync(indexHtmlPath)) {
  const indexHtmlContent = fs.readFileSync(indexHtmlPath, 'utf8');
  console.log('\n✓ index.html 存在');
  console.log('  - 包含 #app div:', indexHtmlContent.includes('<div id="app"></div>'));
  console.log('  - 引入 main.js:', indexHtmlContent.includes('/src/main.js'));
} else {
  console.log('\n✗ index.html 不存在');
}

console.log('\n应用文件结构检查完成！');
