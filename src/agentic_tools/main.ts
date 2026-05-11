import { createExecutionOptions, type RunOptions } from "./node_cli/common.ts";
import { runAgentsPolicy } from "./agents_policy/main.ts";
import { runSkillsManagement } from "./skills_management/main.ts";

const ROOT_USAGE_LINES = [
  "Usage:",
  "  agentic-tools policy <sync|check|import-vscode> [options]",
  "  agentic-tools skills <list|link|sync|unlink> [options]",
  "",
  "Examples:",
  "  agentic-tools policy sync",
  "  agentic-tools policy check --config .agents/policy.json",
  "  agentic-tools skills sync",
  "  agentic-tools skills list --from ../agentic-tools",
];

const POLICY_USAGE_LINES = [
  "Usage:",
  "  agentic-tools policy sync [--config <path>]",
  "  agentic-tools policy check [--config <path>]",
  "  agentic-tools policy import-vscode [--config <path>]",
];

function renderUsage(lines: string[]): string {
  return `${lines.join("\n")}\n`;
}

function buildPolicyArgs(command: string, args: string[]): string[] {
  if (command === "check") {
    return ["--check", ...args];
  }

  if (command === "import-vscode") {
    return ["--import-vscode", ...args];
  }

  return args;
}

export async function runAgenticTools(
  argv: string[] = process.argv.slice(2),
  options: RunOptions = {},
): Promise<number> {
  const effectiveOptions = createExecutionOptions(options);

  if (argv.length === 0) {
    effectiveOptions.output(renderUsage(ROOT_USAGE_LINES));
    return 1;
  }

  const [scope, ...remaining] = argv;

  if (scope === "skills") {
    return runSkillsManagement(remaining, options);
  }

  if (scope === "policy") {
    if (remaining.length === 0) {
      effectiveOptions.output(renderUsage(POLICY_USAGE_LINES));
      return 1;
    }

    const [policyCommand, ...policyArgs] = remaining;
    if (
      policyCommand !== "sync" &&
      policyCommand !== "check" &&
      policyCommand !== "import-vscode"
    ) {
      effectiveOptions.output(renderUsage(POLICY_USAGE_LINES));
      return 1;
    }

    return runAgentsPolicy(buildPolicyArgs(policyCommand, policyArgs), options);
  }

  effectiveOptions.output(renderUsage(ROOT_USAGE_LINES));
  return 1;
}