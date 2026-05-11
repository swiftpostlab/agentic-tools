#!/usr/bin/env node

import { runAgentsPolicy } from "../lib/agents-policy.js";

process.exitCode = runAgentsPolicy(process.argv.slice(2));