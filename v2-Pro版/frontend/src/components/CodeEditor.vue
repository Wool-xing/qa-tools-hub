<template>
  <div ref="editorEl" class="code-editor"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { EditorView, keymap, lineNumbers, highlightActiveLine } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { python } from '@codemirror/lang-python'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '# 在这里写你的 Python 代码...' },
})

const emit = defineEmits(['update:modelValue'])

const editorEl = ref(null)
let view = null

onMounted(() => {
  const updateListener = EditorView.updateListener.of((update) => {
    if (update.docChanged) {
      emit('update:modelValue', update.state.doc.toString())
    }
  })

  view = new EditorView({
    doc: props.modelValue,
    extensions: [
      lineNumbers(),
      highlightActiveLine(),
      history(),
      python(),
      syntaxHighlighting(defaultHighlightStyle),
      keymap.of([...defaultKeymap, ...historyKeymap]),
      updateListener,
      EditorView.placeholder(props.placeholder),
      EditorView.theme({
        '&': { fontSize: '14px', fontFamily: 'var(--font-mono)' },
        '.cm-scroller': { maxHeight: '320px' },
        '.cm-content': { padding: '12px 0' },
        '.cm-gutters': { border: 'none', background: 'transparent', color: 'var(--text-muted)' },
        '.cm-activeLine': { background: 'var(--primary-light)' },
        '.cm-activeLineGutter': { color: 'var(--primary)' },
      }),
    ],
    parent: editorEl.value,
  })
})

watch(() => props.modelValue, (val) => {
  if (view && val !== view.state.doc.toString()) {
    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: val },
    })
  }
})

onBeforeUnmount(() => { view?.destroy() })
</script>

<style scoped>
.code-editor {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--surface);
}
</style>
