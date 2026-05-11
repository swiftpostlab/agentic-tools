#!/usr/bin/env node

import { runSkillsManagement } from "../lib/skills-management.js";

process.exitCode = runSkillsManagement(process.argv.slice(2));