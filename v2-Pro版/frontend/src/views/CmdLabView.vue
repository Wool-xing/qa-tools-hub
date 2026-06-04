<template>
  <div class="lab-page">
    <div class="file-bar">
      <span class="file-label">📁</span>
      <button v-for="f in files" :key="f.path" class="file-btn" :class="{ active: currentFile === f.path }"
        @click="currentFile = f.path; result = null">{{ f.label }}</button>
    </div>

    <div class="terminal">
      <div class="term-header">
        <span class="term-dot red"></span><span class="term-dot yellow"></span><span class="term-dot green"></span>
        <span class="term-title">qa@lab:{{ currentFile }}</span>
      </div>
      <div class="term-prompt">
        <span class="prompt-symbol">$</span>
        <input v-model="cmd" @keyup.enter="execute" placeholder="grep ERROR app.log" class="cmd-input" spellcheck="false">
        <button class="exec-btn" @click="execute" :disabled="!cmd.trim()">⏎</button>
      </div>
      <div v-if="result !== null" class="term-output">
        <pre v-if="result.ok" class="output-text">{{ result.output }}</pre>
        <div v-else class="output-err">❌ {{ result.error }}</div>
      </div>
    </div>

    <div class="quick-bar">
      <span class="qc-label">快捷命令：</span>
      <button v-for="qc in quickCommands" :key="qc" class="qc-chip" @click="cmd = qc; execute()">{{ qc }}</button>
    </div>

    <details class="cheatsheet">
      <summary>📖 命令速查表</summary>
      <div class="cheat-grid">
        <div v-for="c in cheatsheet" :key="c.cmd" class="cheat-item">
          <code>{{ c.cmd }}</code><span>{{ c.desc }}</span>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { labs } from '../api'

const cmd = ref('')
const result = ref(null)
const currentFile = ref('/var/log/app.log')

const files = [
  { path: '/var/log/app.log', label: '📋 app.log' },
  { path: '/var/log/nginx/access.log', label: '🌐 access.log' },
  { path: '/etc/hosts', label: '🔧 /etc/hosts' },
]

const quickCommands = [
  'grep ERROR app.log',
  'grep -c ERROR app.log',
  'tail -20 app.log',
  'grep " 5[0-9][0-9] " access.log',
  'cat hosts',
  'awk \'{print $1}\' access.log | sort | uniq -c | sort -rn',
]

const cheatsheet = [
  { cmd: 'grep PAT file', desc: '搜索匹配文本' },
  { cmd: 'grep -i PAT file', desc: '忽略大小写' },
  { cmd: 'grep -c PAT file', desc: '统计匹配行数' },
  { cmd: 'grep -v PAT file', desc: '反向匹配' },
  { cmd: 'tail -20 file', desc: '末尾20行' },
  { cmd: 'head -10 file', desc: '开头10行' },
  { cmd: 'cat file', desc: '显示全部内容' },
  { cmd: 'wc -l file', desc: '统计行数' },
  { cmd: 'sort file', desc: '排序' },
  { cmd: 'sort -r file', desc: '逆序排列' },
  { cmd: 'uniq -c', desc: '去重并统计' },
  { cmd: 'awk \'{print $1}\' file', desc: '提取第1列' },
]

async function execute() {
  if (!cmd.value.trim()) return
  try { result.value = await labs.cmd(cmd.value, 37) }
  catch (e) { result.value = { ok: false, error: e.message } }
}
</script>

<style scoped>
.lab-page { max-width: 800px; margin: 0 auto; }
.breadcrumb a { color: var(--primary); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }
.file-bar { display: flex; gap: 8px; align-items: center; margin-bottom: var(--space-md); }
.file-label { font-size: .85rem; }
.file-btn {
  padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .78rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.file-btn:hover { border-color: var(--primary); }
.file-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }

.terminal {
  background: #1a1a2e; border-radius: var(--radius-lg); overflow: hidden;
  border: 1px solid #2d2d4a;
}
.term-header { padding: 8px 14px; background: #16162a; display: flex; align-items: center; gap: 6px; }
.term-dot { width: 10px; height: 10px; border-radius: 50%; }
.term-dot.red { background: #ff5f57; } .term-dot.yellow { background: #febc2e; } .term-dot.green { background: #28c840; }
.term-title { color: #a0a0b8; font-size: .72rem; margin-left: 10px; font-family: var(--font-mono); }
.term-prompt { display: flex; align-items: center; padding: 8px 14px; background: #1e1e36; gap: 8px; }
.prompt-symbol { color: #28c840; font-weight: 700; font-family: var(--font-mono); font-size: .9rem; }
.cmd-input { flex: 1; background: transparent; border: none; color: #e5e7eb; font-family: var(--font-mono); font-size: .84rem; outline: none; }
.cmd-input::placeholder { color: #6b7280; }
.exec-btn { padding: 4px 12px; background: #28c840; color: #000; border: none; border-radius: 4px; cursor: pointer; font-weight: 700; font-size: .8rem; }
.exec-btn:disabled { opacity: .4; cursor: not-allowed; }
.term-output { padding: 12px 16px; border-top: 1px solid #2d2d4a; max-height: 400px; overflow-y: auto; }
.output-text { color: #e5e7eb; font-family: var(--font-mono); font-size: .8rem; line-height: 1.6; white-space: pre-wrap; margin: 0; }
.output-err { color: #ef4444; font-size: .82rem; }

.quick-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; align-items: center; }
.qc-label { font-size: .78rem; color: var(--text-secondary); font-weight: 500; }
.qc-chip {
  padding: 5px 12px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .73rem; font-family: var(--font-mono);
  transition: all var(--fast);
}
.qc-chip:hover { border-color: var(--primary); background: var(--primary-light); }

.cheatsheet { margin-top: var(--space-md); font-size: .82rem; }
.cheatsheet summary { cursor: pointer; color: var(--primary); font-weight: 500; margin-bottom: 10px; }
.cheat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 6px; }
.cheat-item { display: flex; gap: 8px; align-items: baseline; font-size: .78rem; }
.cheat-item code {
  background: var(--primary-light); padding: 2px 8px; border-radius: 4px;
  font-family: var(--font-mono); font-size: .74rem; color: var(--primary); white-space: nowrap;
}
.cheat-item span { color: var(--text-secondary); }
</style>
