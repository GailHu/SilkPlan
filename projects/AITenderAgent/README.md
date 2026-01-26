# AITenderAgent
标书智能体Demo
**Version: 0.1.0**

默认用户admin admin123

请把后端cors处地址端口改为前端实际端口（如5173）

deepseek apikey已配置，可以上传招标文件进行测试，解析时间可能较长（主要用于展示一下前端页面和交互流程）


## Frontend Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

## Backend Setup

### Set environment

```sh
pip install -r requirements.txt
```

### Run

```sh
python app.py
```

# AITenderAgent

Lv Mingxin 2025/04/09
