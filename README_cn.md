# Code Archaeologist 🔥

> "每个遗留代码库都在讲述一个故事。有时候是悲剧，有时候是喜剧。通常两者兼有。"

一个强大的 CLI 工具，用于分析遗留代码库、评估技术债务，并生成带有 AI 智能洞察的美观 HTML 报告。

## 功能特点

- **多语言支持** - 自动检测 Python、JavaScript、TypeScript、Go、Java 等
- **代码健康分析** - 圈复杂度、死代码检测、安全扫描
- **依赖健康** - 漏洞检测、过时包识别
- **技术栈检测** - 框架识别、时代判定(传统 vs 现代)
- **技术债务热力图** - 按文件可视化问题密度
- **AI 驱动的报告** - LLM 生成的摘要、重构优先级、迁移路径

## 安装

```bash
# 克隆仓库
git clone https://github.com/code-archaeologist/code-archaeologist.git
cd code-archaeologist

# 使用 pip 安装
pip install -e .

# 安装完整功能
pip install -e ".[full]"
```

## 快速开始

```bash
# 分析项目
code-archaeologist ./my-legacy-project

# 显示详细输出
code-archaeologist ./my-legacy-project -v

# 跳过 LLM 分析（离线模式）
code-archaeologist ./my-legacy-project --no-llm

# 指定输出路径
code-archaeologist ./my-legacy-project -o ./reports/analysis.html
```

## 命令选项

```
code-archaeologist <project_path> [OPTIONS]

选项:
  -o, --output PATH      报告输出路径 (默认: ./archaeology-report.html)
  --llm-backend TEXT     LLM 后端: openai, ollama, groq, deepseek, azure
  --llm-api-key TEXT     LLM API 密钥
  --llm-model TEXT       模型名称 (默认: gpt-4)
  --no-llm              跳过 LLM 分析
  --exclude PATHS        要排除的目录（逗号分隔）
  --config PATH          配置文件路径
  -v, --verbose         详细输出
```

## 配置

创建 `config.json` 文件进行持久配置：

```json
{
  "exclude_patterns": [".git", "node_modules", "__pycache__"],
  "llm": {
    "backend": "openai",
    "model": "gpt-4",
    "api_key": "your-key-here"
  },
  "analysis": {
    "max_file_size_kb": 1000,
    "timeout_seconds": 300
  }
}
```

或使用环境变量：
- `LLM_BACKEND`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_BASE_URL`
- `OUTPUT_PATH`

## 支持的语言

| 语言 | 复杂度 | 死代码 | 安全 |
|------|--------|--------|------|
| Python   | ✅ radon   | ✅ vulture | ✅ bandit |
| JavaScript/TypeScript | ✅ ESLint | ⚠️ basic | ⚠️ npm audit |
| Go       | ⚠️ basic   | ❌        | ⚠️ govulncheck |
| 其他     | ⚠️ basic   | ❌        | ❌        |

## 依赖

核心依赖（自动安装）：
- `click` - CLI 框架
- `jinja2` - HTML 模板
- `pygments` - 语法高亮和语言检测
- `radon` - Python 复杂度分析
- `rich` - 终端输出美化

可选依赖（完整分析）：
- `vulture` - 死代码检测
- `bandit` - 安全扫描
- `safety` / `pip-audit` - 依赖漏洞检测
- `openai` - LLM 集成

## 输出示例

### 健康评分仪表盘
- 总体健康评分 (0-100)
- 语言分布图表
- 复杂度分布
- 问题分类

### 技术栈分析
- 检测到的框架 (Django, React 等)
- 时代判定 (传统/现代)
- 架构模式 (MVC, 微服务等)

### 技术债务热力图
- 按文件的问题密度
- 颜色编码的严重程度
- 点击查看详情

### AI 分析报告

```
## 技术债务摘要

这个项目就像一个 90 年代的废弃主题公园——过山车锈迹斑斑，
棉花糖机正在繁殖某种可疑的东西，但你仍然能在空气中闻到怀旧的气息。
代码复杂度已经突破了大气层，那些无人敢动的遗留模块就像定时炸弹...

[阅读完整的 AI 分析报告]
```

## 使用场景

- **入职培训** - 快速了解新代码库
- **尽职调查** - 收购前的技术健康评估
- **规划重构** - 优先排序重构工作
- **监控追踪** - 持续跟踪技术债务
- **团队沟通** - 与利益相关者分享健康报告

## 许可证

MIT

## 贡献

欢迎贡献！请先阅读贡献指南。