<template>
  <div>
    <el-card>
      <template #header><strong>AI智能助手</strong></template>
      <div ref="listRef" style="height: 480px; overflow-y: auto; padding: 8px 4px; background-color: #fafafa; border-radius: 6px">
        <div
          v-for="(item, index) in messages"
          :key="index"
          :style="{ display: 'flex', justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: '12px' }"
        >
          <div
            :style="{
              maxWidth: '70%', padding: '10px 12px', borderRadius: '8px',
              backgroundColor: item.role === 'user' ? '#409eff' : '#fff',
              color: item.role === 'user' ? '#fff' : '#333', lineHeight: '1.6',
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.06)'
            }"
            v-html="parseMarkdown(item.content)"
          ></div>
        </div>
      </div>
      <div style="margin-top: 12px; display: flex; gap: 8px; align-items: flex-end">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="问问实验室怎么预约、开放时间..."
          @keydown.enter.exact.prevent="handleSend"
          @keydown.enter.shift.stop
        />
        <el-button type="primary" @click="handleSend" :loading="loading">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { chatApi } from '@/api/ai'
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const messages = ref([{
  role: 'assistant',
  content: '您好，我是实验室助手。你可以向我提问怎么预约、取消。具体实验室信息请到【实验室列表】页查看'
}])
const input = ref('')
const loading = ref(false)
const listRef = ref()

const scrollToBottom = () => {
  nextTick(() => {
    const elem = listRef.value
    if (elem) elem.scrollTop = elem.scrollHeight
  })
}
const handleSend = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  scrollToBottom()
  try {
    const history = messages.value.filter((item) => item.role === 'user' || item.role === 'assistant')
    const res = await chatApi({ messages: history })
    if (res.code === 200) { messages.value.push(res.data); scrollToBottom() }
  } finally { loading.value = false }
}
const parseMarkdown = (text) => {
  if (!text) return ''
  marked.setOptions({ breaks: true })
  return DOMPurify.sanitize(marked.parse(text))
}
</script>
