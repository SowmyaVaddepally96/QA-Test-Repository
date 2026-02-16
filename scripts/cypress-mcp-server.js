#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const dotenv = require("dotenv");
const { z } = require("zod");
const {
  McpServer,
} = require("@modelcontextprotocol/sdk/server/mcp.js");
const {
  StdioServerTransport,
} = require("@modelcontextprotocol/sdk/server/stdio.js");

const args = process.argv.slice(2);
function readArg(flag) {
  const idx = args.indexOf(flag);
  if (idx === -1 || idx + 1 >= args.length) return null;
  return args[idx + 1];
}

const repoRoot =
  readArg("--repo") ||
  process.env.MCP_CYPRESS_REPO_ROOT ||
  process.cwd();

function resolveRepoPath(...segments) {
  const resolved = path.resolve(repoRoot, ...segments);
  if (!resolved.startsWith(path.resolve(repoRoot))) {
    throw new Error(`Path escapes repo: ${resolved}`);
  }
  return resolved;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function writeText(filePath, content) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content, "utf8");
}

function listFilesRecursive(rootDir, predicate) {
  if (!fs.existsSync(rootDir)) return [];
  const entries = fs.readdirSync(rootDir, { withFileTypes: true });
  const results = [];
  for (const entry of entries) {
    const fullPath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      results.push(...listFilesRecursive(fullPath, predicate));
    } else if (!predicate || predicate(fullPath)) {
      results.push(fullPath);
    }
  }
  return results;
}

function getCypressConfigPath(explicitPath) {
  if (explicitPath) return resolveRepoPath(explicitPath);
  const jsPath = resolveRepoPath("cypress.config.js");
  if (fs.existsSync(jsPath)) return jsPath;
  const tsPath = resolveRepoPath("cypress.config.ts");
  if (fs.existsSync(tsPath)) return tsPath;
  return jsPath;
}

function loadCypressConfig(configPath) {
  const resolved = getCypressConfigPath(configPath);
  if (!fs.existsSync(resolved)) {
    return { path: resolved, config: {} };
  }
  delete require.cache[require.resolve(resolved)];
  // eslint-disable-next-line global-require, import/no-dynamic-require
  const config = require(resolved);
  return { path: resolved, config: config || {} };
}

function toJs(value, indent = 2) {
  const pad = " ".repeat(indent);
  const padInner = " ".repeat(indent + 2);
  if (value === null) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (typeof value === "function") {
    return value.toString();
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return "[]";
    const inner = value.map((v) => `${padInner}${toJs(v, indent + 2)}`);
    return `[\n${inner.join(",\n")}\n${pad}]`;
  }
  if (typeof value === "object") {
    const keys = Object.keys(value);
    if (keys.length === 0) return "{}";
    const inner = keys.map((key) => {
      return `${padInner}${JSON.stringify(key)}: ${toJs(
        value[key],
        indent + 2,
      )}`;
    });
    return `{\n${inner.join(",\n")}\n${pad}}`;
  }
  return "undefined";
}

function saveCypressConfig(configPath, config) {
  const resolved = getCypressConfigPath(configPath);
  const content = `module.exports = ${toJs(config, 0)};\n`;
  writeText(resolved, content);
  return resolved;
}

function setDeepValue(target, pathStr, value) {
  const parts = pathStr.split(".").filter(Boolean);
  let current = target;
  for (let i = 0; i < parts.length - 1; i += 1) {
    const key = parts[i];
    if (!current[key] || typeof current[key] !== "object") {
      current[key] = {};
    }
    current = current[key];
  }
  current[parts[parts.length - 1]] = value;
}

function parseEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return {};
  return dotenv.parse(readText(filePath));
}

function writeEnvFile(filePath, envObj) {
  const lines = Object.keys(envObj)
    .sort()
    .map((key) => `${key}=${envObj[key]}`);
  writeText(filePath, `${lines.join("\n")}\n`);
}

function getEnvProfilePath(profileName) {
  if (!profileName) return resolveRepoPath(".env.cypress");
  return resolveRepoPath(`.env.cypress.${profileName}`);
}

function buildEnv(profileName, overrides) {
  const baseEnv = parseEnvFile(getEnvProfilePath(profileName));
  return { ...baseEnv, ...(overrides || {}) };
}

function resolveCypressBinary() {
  const localBin = resolveRepoPath("node_modules/.bin/cypress");
  if (fs.existsSync(localBin)) return localBin;
  return "npx";
}

function buildCypressArgs(options) {
  const argsList = [];
  if (options.mode === "open") {
    argsList.push("open");
  } else {
    argsList.push("run");
  }
  if (options.testingType === "component") {
    argsList.push("--component");
  }
  if (options.specs && options.specs.length) {
    argsList.push("--spec", options.specs.join(","));
  }
  if (options.browser) {
    argsList.push("--browser", options.browser);
  }
  if (options.headed) {
    argsList.push("--headed");
  }
  if (options.configFile) {
    argsList.push("--config-file", options.configFile);
  }
  if (options.config) {
    const configPairs = Object.entries(options.config)
      .map(([key, val]) => `${key}=${val}`)
      .join(",");
    if (configPairs) {
      argsList.push("--config", configPairs);
    }
  }
  if (options.env && Object.keys(options.env).length) {
    const envPairs = Object.entries(options.env)
      .map(([key, val]) => `${key}=${val}`)
      .join(",");
    argsList.push("--env", envPairs);
  }
  if (options.record) {
    argsList.push("--record");
  }
  if (options.parallel) {
    argsList.push("--parallel");
  }
  if (options.ciBuildId) {
    argsList.push("--ci-build-id", options.ciBuildId);
  }
  if (options.group) {
    argsList.push("--group", options.group);
  }
  if (options.tag) {
    argsList.push("--tag", options.tag);
  }
  if (options.reporter) {
    argsList.push("--reporter", options.reporter);
  }
  if (options.reporterOptions && Object.keys(options.reporterOptions).length) {
    const reporterPairs = Object.entries(options.reporterOptions)
      .map(([key, val]) => `${key}=${val}`)
      .join(",");
    argsList.push("--reporter-options", reporterPairs);
  }
  return argsList;
}

function summarizeCypressOutput(output) {
  const summary = {};
  const lines = output.split("\n");
  for (const line of lines) {
    const match = line.match(
      /(Tests|Passing|Failing|Pending|Skipped|Screenshots|Video):?\s+(\d+)/i,
    );
    if (match) {
      summary[match[1].toLowerCase()] = Number(match[2]);
    }
  }
  return summary;
}

function parseTestStructure(content) {
  const results = [];
  const regex =
    /\b(describe|context|it|test)\s*(\.(only|skip))?\s*\(\s*([`'"])(.*?)\4/gs;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const [, type, modifierGroup, modifier, , name] = match;
    const line =
      content.slice(0, match.index).split("\n").length;
    results.push({
      type,
      modifier: modifier || (modifierGroup ? modifierGroup.replace(".", "") : null),
      name,
      line,
    });
  }
  return results;
}

let lastRun = null;

const emptySchema = z.object({});
const schema = (shape) => z.object(shape);

function saveLastRun(result) {
  lastRun = result;
  const cacheDir = resolveRepoPath("cypress/.mcp");
  ensureDir(cacheDir);
  writeText(
    path.join(cacheDir, "last-run.json"),
    JSON.stringify(result, null, 2),
  );
  if (result.rawOutput) {
    writeText(path.join(cacheDir, "last-run.log"), result.rawOutput);
  }
}

function loadLastRun() {
  if (lastRun) return lastRun;
  const cachePath = resolveRepoPath("cypress/.mcp/last-run.json");
  if (fs.existsSync(cachePath)) {
    lastRun = JSON.parse(readText(cachePath));
  }
  return lastRun;
}

const server = new McpServer({
  name: "cypress-mcp-server",
  version: "1.0.0",
});

server.tool(
  "cypress_list_specs",
  schema({
    testingType: z.enum(["e2e", "component"]).optional(),
  }),
  async ({ testingType }) => {
    const folders = [];
    if (!testingType || testingType === "e2e") {
      folders.push(resolveRepoPath("cypress/e2e"));
      folders.push(resolveRepoPath("cypress/integration"));
    }
    if (!testingType || testingType === "component") {
      folders.push(resolveRepoPath("cypress/component"));
    }
    const specs = new Set();
    for (const folder of folders) {
      const files = listFilesRecursive(folder, (filePath) =>
        /\.cy\.(js|jsx|ts|tsx)$/.test(filePath),
      );
      for (const file of files) {
        specs.add(path.relative(repoRoot, file));
      }
    }
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ specs: Array.from(specs).sort() }, null, 2),
        },
      ],
    };
  },
);

server.tool(
  "cypress_read_test_file",
  schema({
    path: z.string(),
  }),
  async ({ path: filePath }) => {
    const resolved = resolveRepoPath(filePath);
    const content = readText(resolved);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, resolved), content },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_get_test_structure",
  schema({
    path: z.string(),
  }),
  async ({ path: filePath }) => {
    const resolved = resolveRepoPath(filePath);
    const content = readText(resolved);
    const structure = parseTestStructure(content);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, resolved), structure },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_read_config",
  schema({
    path: z.string().optional(),
  }),
  async ({ path: configPath }) => {
    const { path: resolved, config } = loadCypressConfig(configPath);
    const raw = fs.existsSync(resolved) ? readText(resolved) : "";
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              path: path.relative(repoRoot, resolved),
              config,
              raw,
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_update_config",
  schema({
    path: z.string().optional(),
    updates: z
      .array(
        z.object({
          keyPath: z.string(),
          value: z.any(),
        }),
      )
      .optional(),
    replaceWith: z.any().optional(),
  }),
  async ({ path: configPath, updates, replaceWith }) => {
    const { config } = loadCypressConfig(configPath);
    if (replaceWith) {
      saveCypressConfig(configPath, replaceWith);
    } else if (updates && updates.length) {
      for (const update of updates) {
        setDeepValue(config, update.keyPath, update.value);
      }
      saveCypressConfig(configPath, config);
    }
    const { path: resolved, config: updated } =
      loadCypressConfig(configPath);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, resolved), config: updated },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_read_env",
  schema({
    profile: z.string().optional(),
  }),
  async ({ profile }) => {
    const envPath = getEnvProfilePath(profile);
    const env = parseEnvFile(envPath);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, envPath), env },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_update_env",
  schema({
    profile: z.string().optional(),
    updates: z.record(z.string()).optional(),
    removeKeys: z.array(z.string()).optional(),
  }),
  async ({ profile, updates, removeKeys }) => {
    const envPath = getEnvProfilePath(profile);
    const env = parseEnvFile(envPath);
    if (updates) {
      Object.assign(env, updates);
    }
    if (removeKeys) {
      for (const key of removeKeys) {
        delete env[key];
      }
    }
    writeEnvFile(envPath, env);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, envPath), env },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_run_tests",
  schema({
    testingType: z.enum(["e2e", "component"]).default("e2e"),
    specs: z.array(z.string()).optional(),
    browser: z
      .enum(["chrome", "firefox", "edge", "electron"])
      .optional(),
    headed: z.boolean().optional(),
    configFile: z.string().optional(),
    config: z.record(z.any()).optional(),
    envProfile: z.string().optional(),
    env: z.record(z.any()).optional(),
    record: z.boolean().optional(),
    parallel: z.boolean().optional(),
    ciBuildId: z.string().optional(),
    group: z.string().optional(),
    tag: z.string().optional(),
    reporter: z.string().optional(),
    reporterOptions: z.record(z.any()).optional(),
  }),
  async (options) => {
    const cypressBinary = resolveCypressBinary();
    const useNpx = cypressBinary === "npx";
    const argsList = buildCypressArgs({
      ...options,
      env: buildEnv(options.envProfile, options.env),
    });
    const fullArgs = useNpx
      ? ["-y", "cypress", ...argsList]
      : argsList;
    const env = { ...process.env, ...buildEnv(options.envProfile, options.env) };
    const start = Date.now();
    const outputChunks = [];
    const errorChunks = [];

    const exitCode = await new Promise((resolve) => {
      const child = spawn(cypressBinary, fullArgs, {
        cwd: repoRoot,
        env,
      });
      child.stdout.on("data", (data) => {
        outputChunks.push(data.toString());
      });
      child.stderr.on("data", (data) => {
        errorChunks.push(data.toString());
      });
      child.on("close", (code) => {
        resolve(code ?? 0);
      });
    });

    const rawOutput = `${outputChunks.join("")}\n${errorChunks.join("")}`.trim();
    const summary = summarizeCypressOutput(rawOutput);
    const result = {
      exitCode,
      durationMs: Date.now() - start,
      summary,
      rawOutput,
      command: {
        binary: cypressBinary,
        args: fullArgs,
      },
    };
    saveLastRun(result);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  },
);

server.tool(
  "cypress_get_last_run_results",
  emptySchema,
  async () => {
    const result = loadLastRun();
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result || { message: "No runs recorded." }, null, 2),
        },
      ],
    };
  },
);

server.tool(
  "cypress_get_last_run_logs",
  emptySchema,
  async () => {
    const cachePath = resolveRepoPath("cypress/.mcp/last-run.log");
    const logs = fs.existsSync(cachePath) ? readText(cachePath) : "";
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, cachePath), logs },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_list_artifacts",
  emptySchema,
  async () => {
    const artifactDirs = [
      resolveRepoPath("cypress/screenshots"),
      resolveRepoPath("cypress/videos"),
      resolveRepoPath("cypress/results"),
      resolveRepoPath("cypress/reports"),
    ];
    const artifacts = [];
    for (const dir of artifactDirs) {
      const files = listFilesRecursive(dir);
      for (const file of files) {
        artifacts.push(path.relative(repoRoot, file));
      }
    }
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ artifacts: artifacts.sort() }, null, 2),
        },
      ],
    };
  },
);

server.tool(
  "cypress_read_artifact",
  schema({
    path: z.string(),
    encoding: z.enum(["base64", "utf8"]).default("base64"),
  }),
  async ({ path: artifactPath, encoding }) => {
    const resolved = resolveRepoPath(artifactPath);
    const buffer = fs.readFileSync(resolved);
    const content =
      encoding === "utf8" ? buffer.toString("utf8") : buffer.toString("base64");
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              path: path.relative(repoRoot, resolved),
              encoding,
              content,
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_list_network_logs",
  emptySchema,
  async () => {
    const dirs = [
      resolveRepoPath("cypress/har"),
      resolveRepoPath("cypress/logs"),
      resolveRepoPath("cypress/network"),
    ];
    const logs = new Set();
    for (const dir of dirs) {
      const files = listFilesRecursive(dir, (filePath) =>
        /\.(har|json|log)$/.test(filePath),
      );
      for (const file of files) {
        logs.add(path.relative(repoRoot, file));
      }
    }
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ logs: Array.from(logs).sort() }, null, 2),
        },
      ],
    };
  },
);

server.tool(
  "cypress_read_network_log",
  schema({
    path: z.string(),
  }),
  async ({ path: logPath }) => {
    const resolved = resolveRepoPath(logPath);
    const content = readText(resolved);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, resolved), content },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_create_test_file",
  schema({
    testingType: z.enum(["e2e", "component"]).default("e2e"),
    name: z.string(),
    description: z.string().optional(),
    content: z.string().optional(),
  }),
  async ({ testingType, name, description, content }) => {
    const folder =
      testingType === "component"
        ? resolveRepoPath("cypress/component")
        : resolveRepoPath("cypress/e2e");
    const safeName = name
      .toLowerCase()
      .replace(/[^a-z0-9-_]+/g, "-")
      .replace(/--+/g, "-")
      .replace(/^-|-$/g, "");
    const filePath = path.join(folder, `${safeName}.cy.js`);
    if (!content) {
      const title =
        description || `${testingType} spec for ${safeName}`;
      content = `describe(${JSON.stringify(title)}, () => {\n  it("runs", () => {\n    // TODO: add assertions\n  });\n});\n`;
    }
    writeText(filePath, content);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, filePath) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

function ensureSupportFiles() {
  const supportDir = resolveRepoPath("cypress/support");
  ensureDir(supportDir);
  const supportFile = path.join(supportDir, "e2e.js");
  if (!fs.existsSync(supportFile)) {
    writeText(supportFile, "");
  }
  const commandsFile = path.join(supportDir, "commands.js");
  if (!fs.existsSync(commandsFile)) {
    writeText(
      commandsFile,
      "Cypress.Commands.add(\"noop\", () => {});\n",
    );
  }
  const supportContent = readText(supportFile);
  if (!supportContent.includes('import "./commands";')) {
    writeText(supportFile, `import "./commands";\n${supportContent}`);
  }
  return { supportFile, commandsFile };
}

function ensureImportLine(filePath, importLine) {
  if (!fs.existsSync(filePath)) {
    writeText(filePath, `${importLine}\n`);
    return;
  }
  const content = readText(filePath);
  if (!content.includes(importLine)) {
    writeText(filePath, `${importLine}\n${content}`);
  }
}

function insertHooksIntoSpec(filePath, hooks) {
  const content = readText(filePath);
  const describeMatch = content.match(
    /\bdescribe\s*(\.(only|skip))?\s*\(/,
  );
  const hookLines = [];
  const addHook = (name, body) => {
    if (!body) return;
    hookLines.push(
      `  ${name}(() => {\n    ${body.trim().split("\n").join("\n    ")}\n  });\n`,
    );
  };
  addHook("before", hooks.before);
  addHook("beforeEach", hooks.beforeEach);
  addHook("after", hooks.after);
  addHook("afterEach", hooks.afterEach);
  if (!hookLines.length) return content;
  if (describeMatch) {
    const startIdx = describeMatch.index;
    const braceIdx = content.indexOf("{", startIdx);
    if (braceIdx !== -1) {
      const insertAt = braceIdx + 1;
      return (
        content.slice(0, insertAt) +
        "\n" +
        hookLines.join("") +
        content.slice(insertAt)
      );
    }
  }
  return `${hookLines.join("")}\n${content}`;
}

function ensureSupportEnabled(configPath) {
  const { config } = loadCypressConfig(configPath);
  if (!config.e2e) config.e2e = {};
  if (!config.e2e.supportFile || config.e2e.supportFile === false) {
    config.e2e.supportFile = "cypress/support/e2e.js";
  }
  saveCypressConfig(configPath, config);
}

server.tool(
  "cypress_add_custom_command",
  schema({
    name: z.string(),
    body: z.string(),
    configPath: z.string().optional(),
  }),
  async ({ name, body, configPath }) => {
    const { commandsFile } = ensureSupportFiles();
    ensureSupportEnabled(configPath);
    const commandLine = `Cypress.Commands.add(${JSON.stringify(
      name,
    )}, ${body});\n`;
    fs.appendFileSync(commandsFile, commandLine, "utf8");
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              path: path.relative(repoRoot, commandsFile),
              added: name,
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_insert_hooks",
  schema({
    path: z.string(),
    before: z.string().optional(),
    beforeEach: z.string().optional(),
    after: z.string().optional(),
    afterEach: z.string().optional(),
  }),
  async ({ path: specPath, before, beforeEach, after, afterEach }) => {
    const resolved = resolveRepoPath(specPath);
    const updated = insertHooksIntoSpec(resolved, {
      before,
      beforeEach,
      after,
      afterEach,
    });
    writeText(resolved, updated);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, resolved) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_create_storage_state",
  schema({
    name: z.string().default("storageState"),
    localStorage: z.record(z.any()).optional(),
    sessionStorage: z.record(z.any()).optional(),
    cookies: z
      .array(
        z.object({
          name: z.string(),
          value: z.string(),
          options: z.record(z.any()).optional(),
        }),
      )
      .optional(),
  }),
  async ({ name, localStorage, sessionStorage, cookies }) => {
    const fixtureDir = resolveRepoPath("cypress/fixtures");
    ensureDir(fixtureDir);
    const filePath = path.join(fixtureDir, `${name}.json`);
    const payload = {
      localStorage: localStorage || {},
      sessionStorage: sessionStorage || {},
      cookies: cookies || [],
    };
    writeText(filePath, `${JSON.stringify(payload, null, 2)}\n`);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, filePath) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_add_storage_helpers",
  emptySchema,
  async () => {
    const { supportFile } = ensureSupportFiles();
    ensureSupportEnabled();
    const storageHelperPath = resolveRepoPath("cypress/support/storage.js");
    const helperContent = `Cypress.Commands.add("loadStorageState", (fixtureName = "storageState") => {\n  cy.fixture(fixtureName).then((state) => {\n    if (state.localStorage) {\n      cy.window().then((win) => {\n        Object.entries(state.localStorage).forEach(([key, value]) => {\n          win.localStorage.setItem(key, value);\n        });\n      });\n    }\n    if (state.sessionStorage) {\n      cy.window().then((win) => {\n        Object.entries(state.sessionStorage).forEach(([key, value]) => {\n          win.sessionStorage.setItem(key, value);\n        });\n      });\n    }\n    if (Array.isArray(state.cookies)) {\n      state.cookies.forEach((cookie) => {\n        cy.setCookie(cookie.name, cookie.value, cookie.options || {});\n      });\n    }\n  });\n});\n\nCypress.Commands.add("clearStorageState", () => {\n  cy.clearCookies();\n  cy.window().then((win) => {\n    win.localStorage.clear();\n    win.sessionStorage.clear();\n  });\n});\n`;
    writeText(storageHelperPath, helperContent);
    ensureImportLine(supportFile, 'import "./storage";');
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              supportFile: path.relative(repoRoot, supportFile),
              helperPath: path.relative(repoRoot, storageHelperPath),
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_create_page_object",
  schema({
    name: z.string(),
    content: z.string().optional(),
  }),
  async ({ name, content }) => {
    const pagesDir = resolveRepoPath("cypress/pages");
    ensureDir(pagesDir);
    const safeName = name
      .replace(/[^a-zA-Z0-9-_]+/g, "-")
      .replace(/--+/g, "-")
      .replace(/^-|-$/g, "");
    const filePath = path.join(pagesDir, `${safeName}.js`);
    if (!content) {
      content = `export class ${safeName
        .replace(/-([a-z])/g, (_, c) => c.toUpperCase())
        .replace(/^[a-z]/, (c) => c.toUpperCase())}Page {\n  visit() {\n    // TODO: implement\n  }\n}\n`;
    }
    writeText(filePath, content);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, filePath) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_add_fixture",
  schema({
    name: z.string(),
    content: z.any(),
  }),
  async ({ name, content }) => {
    const fixtureDir = resolveRepoPath("cypress/fixtures");
    ensureDir(fixtureDir);
    const safeName = name.replace(/[^a-zA-Z0-9-_]+/g, "-");
    const filePath = path.join(fixtureDir, `${safeName}.json`);
    writeText(filePath, `${JSON.stringify(content, null, 2)}\n`);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, filePath) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_update_fixture",
  schema({
    name: z.string(),
    content: z.any(),
  }),
  async ({ name, content }) => {
    const fixtureDir = resolveRepoPath("cypress/fixtures");
    const safeName = name.replace(/[^a-zA-Z0-9-_]+/g, "-");
    const filePath = path.join(fixtureDir, `${safeName}.json`);
    writeText(filePath, `${JSON.stringify(content, null, 2)}\n`);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, filePath) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_set_retries",
  schema({
    runMode: z.number().optional(),
    openMode: z.number().optional(),
    configPath: z.string().optional(),
  }),
  async ({ runMode, openMode, configPath }) => {
    const { config } = loadCypressConfig(configPath);
    if (!config.e2e) config.e2e = {};
    if (runMode !== undefined || openMode !== undefined) {
      config.e2e.retries = {
        runMode: runMode ?? 0,
        openMode: openMode ?? 0,
      };
    }
    saveCypressConfig(configPath, config);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              path: path.relative(repoRoot, getCypressConfigPath(configPath)),
              retries: config.e2e.retries,
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_set_reporter",
  schema({
    reporter: z.string(),
    reporterOptions: z.record(z.any()).optional(),
    configPath: z.string().optional(),
  }),
  async ({ reporter, reporterOptions, configPath }) => {
    const { config } = loadCypressConfig(configPath);
    config.reporter = reporter;
    if (reporterOptions) {
      config.reporterOptions = reporterOptions;
    }
    saveCypressConfig(configPath, config);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              path: path.relative(repoRoot, getCypressConfigPath(configPath)),
              reporter,
              reporterOptions: reporterOptions || null,
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_add_plugin",
  schema({
    name: z.string(),
    content: z.string().optional(),
    configPath: z.string().optional(),
  }),
  async ({ name, content, configPath }) => {
    const pluginsDir = resolveRepoPath("cypress/plugins");
    ensureDir(pluginsDir);
    const safeName = name.replace(/[^a-zA-Z0-9-_]+/g, "-");
    const pluginPath = path.join(pluginsDir, `${safeName}.js`);
    if (!content) {
      content = `module.exports = (on, config) => {\n  // TODO: add plugin logic\n  return config;\n};\n`;
    }
    writeText(pluginPath, content);

    const { config } = loadCypressConfig(configPath);
    if (!config.e2e) config.e2e = {};
    const existing = config.e2e.setupNodeEvents;
    config.e2e.setupNodeEvents = (on, cfg) => {
      if (typeof existing === "function") {
        existing(on, cfg);
      }
      // eslint-disable-next-line global-require, import/no-dynamic-require
      require(`./cypress/plugins/${safeName}`)(on, cfg);
      return cfg;
    };
    saveCypressConfig(configPath, config);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              pluginPath: path.relative(repoRoot, pluginPath),
              configPath: path.relative(
                repoRoot,
                getCypressConfigPath(configPath),
              ),
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

server.tool(
  "cypress_generate_ci_github_actions",
  schema({
    workflowName: z.string().default("cypress.yml"),
    nodeVersion: z.string().default("20"),
    installCommand: z.string().default("npm ci"),
    runCommand: z.string().default("npx cypress run"),
  }),
  async ({ workflowName, nodeVersion, installCommand, runCommand }) => {
    const workflowDir = resolveRepoPath(".github/workflows");
    ensureDir(workflowDir);
    const workflowPath = path.join(workflowDir, workflowName);
    const content = `name: Cypress Tests\n\non:\n  push:\n    branches: [main]\n  pull_request:\n    branches: [main]\n\njobs:\n  cypress:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with:\n          node-version: ${nodeVersion}\n      - run: ${installCommand}\n      - run: ${runCommand}\n`;
    writeText(workflowPath, content);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { path: path.relative(repoRoot, workflowPath) },
            null,
            2,
          ),
        },
      ],
    };
  },
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Cypress MCP server error:", error);
  process.exit(1);
});
