#!/usr/bin/env node

import { runAgenticTools } from "../src/agentic_tools/main.ts";

process.exitCode = await runAgenticTools(process.argv.slice(2));