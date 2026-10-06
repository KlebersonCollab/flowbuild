#!/usr/bin/env node

/**
 * SDD Integrity & Canonical Governance Sensor
 * AI-SDD Framework | Fast empirical verification of project specifications and ADR invariants.
 *
 * Verifies:
 * 1. Required core specification files exist (.specs/project, .specs/codebase, root)
 * 2. ADR status consistency and valid lifecycle (Proposed, Accepted, Superseded, Deprecated)
 * 3. Tasks table schema adherence (MetaGPT 7-column SOP) in active features
 * 4. Memory graph (.agents/memory/memory_graph.jsonl) JSONL validity
 * 5. Corrupted escape sequences (e.g. raw tabs in spec files)
 */

const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '../..');

const REQUIRED_FILES = [
  'AGENTS.md',
  'DESIGN.md',
  '.specs/project/CONTEXT.md',
  '.specs/project/PROJECT.md',
  '.specs/project/ROADMAP.md',
  '.specs/project/STATE.md',
  '.specs/codebase/STACK.md',
  '.specs/codebase/ARCHITECTURE.md',
  '.specs/codebase/CONVENTIONS.md',
  '.specs/codebase/CONCERNS.md',
  '.specs/codebase/TECHNICAL-MAP.md'
];

const VALID_ADR_STATUSES = ['proposed', 'accepted', 'superseded', 'deprecated'];

function checkRequiredFiles() {
  const missing = [];
  for (const relPath of REQUIRED_FILES) {
    const fullPath = path.join(REPO_ROOT, relPath);
    if (!fs.existsSync(fullPath)) {
      missing.push(relPath);
    }
  }
  return missing;
}

function checkAdrs() {
  const adrsDir = path.join(REPO_ROOT, '.specs', 'project', 'ADRs');
  const issues = [];
  if (!fs.existsSync(adrsDir)) return issues;

  const files = fs.readdirSync(adrsDir).filter(f => f.endsWith('.md'));
  for (const file of files) {
    const fullPath = path.join(adrsDir, file);
    const content = fs.readFileSync(fullPath, 'utf8');

    const statusMatch = content.match(/^##\s+Status\s*\n+([^\n]+)/im);
    if (!statusMatch) {
      issues.push(`${file}: Missing '## Status' section`);
      continue;
    }

    const rawStatus = statusMatch[1].trim().toLowerCase();
    const isKnownStatus = VALID_ADR_STATUSES.some(s => rawStatus.startsWith(s));
    if (!isKnownStatus) {
      issues.push(`${file}: Invalid Status '${statusMatch[1].trim()}'. Allowed: Proposed, Accepted, Superseded, Deprecated`);
    }

    // Check if superseded ADR has link/reference to superseding ADR
    if (rawStatus.startsWith('superseded') && !rawStatus.includes('adr')) {
      issues.push(`${file}: Marked as 'Superseded' but does not reference target ADR (e.g., 'Superseded by ADR XXXX')`);
    }
  }

  return issues;
}

function checkTasksTables() {
  const featuresDir = path.join(REPO_ROOT, '.specs', 'features');
  const issues = [];
  if (!fs.existsSync(featuresDir)) return issues;

  const featureDirs = fs.readdirSync(featuresDir, { withFileTypes: true }).filter(d => d.isDirectory());
  for (const dir of featureDirs) {
    const tasksPath = path.join(featuresDir, dir.name, 'tasks.md');
    if (!fs.existsSync(tasksPath)) continue;

    const content = fs.readFileSync(tasksPath, 'utf8');
    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line.startsWith('|') || line.includes('Target Files') || line.includes('---')) continue;

      const columns = line.replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());
      if (columns.length < 5) {
        issues.push(`${dir.name}/tasks.md#L${i + 1}: Table row has only ${columns.length} columns (minimum 5 required, 7 standard)`);
        continue;
      }

      // Check task ID format
      const id = columns[1] || '';
      if (!/^TASK-\d+$/i.test(id)) {
        issues.push(`${dir.name}/tasks.md#L${i + 1}: Invalid task ID '${id}' (must follow TASK-XX format)`);
      }

      // Check status marker format
      const rawStatus = columns[0] || '';
      if (!/^\[\s*[xX\->.]?\s*\]$/.test(rawStatus)) {
        issues.push(`${dir.name}/tasks.md#L${i + 1}: Invalid status marker '${rawStatus}' (must be [ ], [-], or [x])`);
      }
    }
  }

  return issues;
}

function checkMemoryGraph() {
  const memoryFile = path.join(REPO_ROOT, '.agents', 'memory', 'memory_graph.jsonl');
  const issues = [];
  if (!fs.existsSync(memoryFile)) return issues;

  const content = fs.readFileSync(memoryFile, 'utf8');
  const lines = content.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    try {
      const record = JSON.parse(line);
      if (!record.type || !['entity', 'relation', 'observation'].includes(record.type)) {
        issues.push(`memory_graph.jsonl#L${i + 1}: Invalid record type '${record.type}'`);
      }
    } catch (err) {
      issues.push(`memory_graph.jsonl#L${i + 1}: Invalid JSON syntax (${err.message})`);
    }
  }

  return issues;
}

function checkCorruptedEscapes() {
  const specsDir = path.join(REPO_ROOT, '.specs');
  const issues = [];
  if (!fs.existsSync(specsDir)) return issues;

  function scanDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        scanDir(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        const content = fs.readFileSync(fullPath, 'utf8');
        // Check for raw tab followed by 'asks.md' (the common \tasks.md corruption)
        if (content.includes('\tasks.md') || content.includes('\tasks')) {
          const rel = path.relative(REPO_ROOT, fullPath).replace(/\\/g, '/');
          issues.push(`${rel}: Found corrupted unescaped tab escape sequence (	asks.md)`);
        }
      }
    }
  }

  scanDir(specsDir);
  return issues;
}

function runIntegrityAudit() {
  console.log('\n🛡️  [SDD INTEGRITY SENSOR] Iniciando auditoria canônica das especificações...');

  let hasErrors = false;

  // 1. Required Files
  const missingFiles = checkRequiredFiles();
  if (missingFiles.length > 0) {
    console.error('\n❌ Arquivos canônicos obrigatórios ausentes:');
    missingFiles.forEach(f => console.error(`   - ${f}`));
    hasErrors = true;
  } else {
    console.log('✅ [CANONICAL FILES] Todos os 11 arquivos estruturais presentes.');
  }

  // 2. ADR Consistency
  const adrIssues = checkAdrs();
  if (adrIssues.length > 0) {
    console.error('\n❌ Inconsistências de governança nas ADRs:');
    adrIssues.forEach(i => console.error(`   - ${i}`));
    hasErrors = true;
  } else {
    console.log('✅ [ADR GOVERNANCE] Ciclo de vida e status de todas as ADRs válidos.');
  }

  // 3. Tasks Table Schema
  const taskIssues = checkTasksTables();
  if (taskIssues.length > 0) {
    console.error('\n❌ Desvios no schema de tarefas (tasks.md):');
    taskIssues.forEach(i => console.error(`   - ${i}`));
    hasErrors = true;
  } else {
    console.log('✅ [SOP SCHEMA] Tabelas de tarefas em conformidade com MetaGPT SOP.');
  }

  // 4. Memory Graph
  const memoryIssues = checkMemoryGraph();
  if (memoryIssues.length > 0) {
    console.error('\n❌ Erros no grafo de memória persistente:');
    memoryIssues.forEach(i => console.error(`   - ${i}`));
    hasErrors = true;
  } else {
    console.log('✅ [MEMORY GRAPH] Grafo JSONL íntegro e sintaticamente válido.');
  }

  // 5. Corrupted Escape Sequences
  const escapeIssues = checkCorruptedEscapes();
  if (escapeIssues.length > 0) {
    console.error('\n❌ Sequências de escape corrompidas detectadas:');
    escapeIssues.forEach(i => console.error(`   - ${i}`));
    hasErrors = true;
  } else {
    console.log('✅ [ESCAPE INTEGRITY] Zero caracteres corrompidos em arquivos .specs.');
  }

  if (hasErrors) {
    console.error('\n🚫 [SDD INTEGRITY FAIL] Falha na validação de integridade. Corrija os desvios acima.\n');
    process.exit(1);
  }

  console.log('\n🎉 [SDD INTEGRITY OK] Ecossistema SDD 100% íntegro e aderente às regras canônicas.\n');
  process.exit(0);
}

if (require.main === module) {
  runIntegrityAudit();
}

module.exports = {
  checkRequiredFiles,
  checkAdrs,
  checkTasksTables,
  checkMemoryGraph,
  checkCorruptedEscapes,
  runIntegrityAudit
};
