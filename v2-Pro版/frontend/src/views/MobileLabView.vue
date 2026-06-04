<template>
  <div class="lab-page">
    <div class="phone-mock">
      <div class="phone-screen">
        <div class="phone-status">12:30 &nbsp; 📶 &nbsp; 🔋</div>
        <div class="phone-apps">
          <div class="app-icon">📱<span>被测App</span></div>
          <div class="app-icon">🐛<span>崩溃!</span></div>
          <div class="app-icon">📊<span>设置</span></div>
        </div>
        <div class="phone-crash" v-if="deviceCrashed">💥 App 已崩溃</div>
      </div>
    </div>

    <div class="terminal">
      <div class="term-header"><span class="term-dot red"></span><span class="term-dot yellow"></span><span class="term-dot green"></span><span class="term-title">adb shell</span></div>
      <div class="term-body" ref="termBody">
        <div v-for="(line, i) in history" :key="i" class="term-line">
          <span class="term-prompt">$</span>
          <span v-if="line.cmd" class="term-cmd">{{ line.cmd }}</span>
          <pre v-if="line.out" class="term-out">{{ line.out }}</pre>
          <span v-if="line.err" class="term-err">{{ line.err }}</span>
        </div>
        <div class="term-input-line">
          <span class="term-prompt">$</span>
          <input v-model="cmd" @keyup.enter="execute" @keyup.up.prevent="prevCmd" @keyup.down.prevent="nextCmd" placeholder="adb devices" class="cmd-input" spellcheck="false" ref="cmdInput">
        </div>
      </div>
    </div>

    <div class="quick-bar">
      <span class="qc-label">快捷命令：</span>
      <button v-for="qc in quickCommands" :key="qc" class="qc-chip" @click="cmd=qc; execute()">{{ qc }}</button>
    </div>

    <details class="cheatsheet">
      <summary>📖 ADB 命令速查表</summary>
      <div class="cheat-grid">
        <div v-for="c in cheatsheet" :key="c.cmd" class="cheat-item"><code>{{ c.cmd }}</code><span>{{ c.desc }}</span></div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const cmd = ref('')
const history = ref([])
const cmdHistory = ref([])
const cmdIdx = ref(-1)
const deviceCrashed = ref(false)
const installedApp = ref(false)

const quickCommands = [
  'adb devices',
  'adb install app.apk',
  'adb logcat | grep ERROR',
  'adb shell screencap /sdcard/screen.png',
  'adb shell dumpsys meminfo',
  'adb pull /sdcard/screen.png .',
]

const cheatsheet = [
  { cmd: 'adb devices', desc: '列出连接的设备/模拟器' },
  { cmd: 'adb install app.apk', desc: '安装 APK' },
  { cmd: 'adb uninstall pkg', desc: '卸载应用' },
  { cmd: 'adb logcat', desc: '查看设备日志' },
  { cmd: 'adb logcat | grep ERROR', desc: '过滤错误日志' },
  { cmd: 'adb shell screencap /sdcard/x.png', desc: '截屏' },
  { cmd: 'adb shell input tap x y', desc: '模拟点击' },
  { cmd: 'adb shell input text "hello"', desc: '模拟输入文本' },
  { cmd: 'adb shell dumpsys meminfo', desc: '内存信息' },
  { cmd: 'adb shell dumpsys battery', desc: '电池状态' },
  { cmd: 'adb pull /sdcard/file .', desc: '从设备拉取文件' },
  { cmd: 'adb push file /sdcard/', desc: '推送文件到设备' },
  { cmd: 'adb shell pm list packages', desc: '列出已安装应用' },
  { cmd: 'adb reboot', desc: '重启设备' },
]

const simDB = {
  devices: ['emulator-5554\tdevice', ''],
  install: ['Performing Streamed Install\nSuccess', ''],
  logcat: `--------- beginning of crash
E/AndroidRuntime: FATAL EXCEPTION: main
E/AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method on null
E/AndroidRuntime: \tat com.app.LoginActivity.onCreate(LoginActivity.java:42)
E/AndroidRuntime: \tat android.app.Activity.performCreate(Activity.java:7136)
--------- beginning of system`,
  screencap: ['Screenshot saved to /sdcard/screen.png (1080×2400, 1.2MB)', ''],
  dumpsys: ['Total RAM: 8,192 MB\nUsed RAM: 3,456 MB (42%)\nFree RAM: 4,736 MB', ''],
  pull: ['/sdcard/screen.png: 1 file pulled, 0 skipped. 1.2 MB/s (1.2MB in 1.0s)', ''],
  push: ['file pushed to /sdcard/', ''],
  packages: ['package:com.app.qa.demo\npackage:com.android.chrome\npackage:com.google.gms', ''],
  reboot: ['Rebooting device...', ''],
  shell: ['shell@android:/ $ ', ''],
}

function sim(c) {
  if (c === 'adb devices') return simDB.devices[0]
  if (c.startsWith('adb install')) { installedApp.value = true; return simDB.install[0] }
  if (c.startsWith('adb logcat')) {
    if (deviceCrashed.value) return simDB.logcat
    return '--------- beginning of main\nI/ActivityManager: Displayed com.app.qa/.MainActivity: +420ms\nI/Choreographer: Skipped 34 frames!'
  }
  if (c.includes('screencap')) return simDB.screencap[0]
  if (c.includes('dumpsys meminfo')) return simDB.dumpsys[0]
  if (c.startsWith('adb pull')) return simDB.pull[0]
  if (c.startsWith('adb push')) return simDB.push[0]
  if (c.includes('pm list packages')) return simDB.packages[0]
  if (c === 'adb reboot') return simDB.reboot[0]
  if (c.startsWith('adb shell input tap')) {
    deviceCrashed.value = true
    return 'Tap sent: ' + c.split(' ').slice(3).join(' ')
  }
  if (c.startsWith('adb shell input text')) return 'Text input sent'
  if (c.startsWith('adb shell dumpsys battery')) return 'AC powered: false\nUSB powered: true\nlevel: 73\nhealth: 2'
  if (c.startsWith('adb uninstall')) return 'Success'
  return `Unknown command: ${c}`
}

function execute() {
  const c = cmd.value.trim()
  if (!c) return
  history.value.push({ cmd: c, out: '', err: '' })
  const out = sim(c)
  history.value[history.value.length - 1].out = out
  cmdHistory.value.push(c)
  cmdIdx.value = cmdHistory.value.length
  cmd.value = ''
  nextTick(() => { const el = document.querySelector('.term-body'); if (el) el.scrollTop = el.scrollHeight })
}

function prevCmd() {
  if (cmdIdx.value > 0) {
    cmdIdx.value--
    cmd.value = cmdHistory.value[cmdIdx.value]
  }
}

function nextCmd() {
  if (cmdIdx.value < cmdHistory.value.length - 1) {
    cmdIdx.value++
    cmd.value = cmdHistory.value[cmdIdx.value]
  } else {
    cmdIdx.value = cmdHistory.value.length
    cmd.value = ''
  }
}
</script>

<style scoped>
.lab-page { max-width: 800px; margin: 0 auto; }
.breadcrumb a { color: var(--primary); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }

.phone-mock { display: flex; justify-content: center; margin-bottom: var(--space-md); }
.phone-screen {
  width: 200px; height: 340px; border: 3px solid #333; border-radius: 24px;
  background: linear-gradient(180deg, #f0f4ff 0%, #e8ecf8 100%);
  padding: 12px; display: flex; flex-direction: column; gap: 8px; position: relative; overflow: hidden;
}
.phone-status { font-size: .6rem; color: #333; text-align: center; }
.phone-apps { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.app-icon {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  font-size: 1.6rem; padding: 6px; border-radius: 12px; cursor: pointer;
}
.app-icon span { font-size: .52rem; color: #555; }
.phone-crash {
  position: absolute; inset: 40px; background: rgba(0,0,0,.85); color: #ef4444;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .8rem;
  border-radius: 12px;
}

.terminal { background: #1a1a2e; border-radius: var(--radius-lg); overflow: hidden; border: 1px solid #2d2d4a; }
.term-header { padding: 8px 14px; background: #16162a; display: flex; align-items: center; gap: 6px; }
.term-dot { width: 10px; height: 10px; border-radius: 50%; }
.term-dot.red { background: #ff5f57; } .term-dot.yellow { background: #febc2e; } .term-dot.green { background: #28c840; }
.term-title { color: #a0a0b8; font-size: .72rem; margin-left: 10px; font-family: var(--font-mono); }
.term-body { padding: 12px 16px; max-height: 360px; overflow-y: auto; font-family: var(--font-mono); }
.term-line { margin-bottom: 2px; }
.term-prompt { color: #28c840; font-weight: 700; margin-right: 6px; }
.term-cmd { color: #e5e7eb; font-size: .82rem; }
.term-out { color: #a0a0b8; font-size: .78rem; line-height: 1.6; margin: 4px 0; white-space: pre-wrap; }
.term-err { color: #ef4444; font-size: .78rem; }
.term-input-line { display: flex; align-items: center; margin-top: 6px; }
.cmd-input { flex: 1; background: transparent; border: none; color: #e5e7eb; font-family: var(--font-mono); font-size: .82rem; outline: none; }

.quick-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; align-items: center; }
.qc-label { font-size: .78rem; color: var(--text-secondary); font-weight: 500; }
.qc-chip { padding: 5px 12px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--surface); cursor: pointer; font-size: .73rem; font-family: var(--font-mono); transition: all var(--fast); }
.qc-chip:hover { border-color: var(--primary); background: var(--primary-light); }

.cheatsheet { margin-top: var(--space-md); font-size: .82rem; }
.cheatsheet summary { cursor: pointer; color: var(--primary); font-weight: 500; margin-bottom: 10px; }
.cheat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 6px; }
.cheat-item { display: flex; gap: 8px; align-items: baseline; font-size: .78rem; }
.cheat-item code { background: var(--primary-light); padding: 2px 8px; border-radius: 4px; font-family: var(--font-mono); font-size: .74rem; color: var(--primary); white-space: nowrap; }
.cheat-item span { color: var(--text-secondary); }
</style>
