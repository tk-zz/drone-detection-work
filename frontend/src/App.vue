<template>
  <div class="page">
    <section v-if="!authToken" class="login-page">
      <div class="login-panel">
        <div class="login-copy">
          <h1>无人机航拍场景异常检测与可视分析系统</h1>
          <p>登录后进入航拍图像检测、异常分析和巡检建议工作台。</p>
        </div>

        <form class="login-card" @submit.prevent="login">
          <h2>系统登录</h2>
          <label>
            用户名
            <input v-model="loginForm.username" autocomplete="username" placeholder="请输入用户名" />
          </label>
          <label>
            密码
            <input v-model="loginForm.password" autocomplete="current-password" placeholder="请输入密码" type="password" />
          </label>
          <button :disabled="loginLoading" type="submit">
            {{ loginLoading ? '登录中...' : '登录' }}
          </button>
          <p v-if="loginError" class="error">{{ loginError }}</p>
          <p class="login-hint">默认账号：admin / admin123</p>
        </form>
      </div>
    </section>

    <template v-else>
    <header class="header">
      <div class="user-bar">
        <span>当前用户：{{ currentUser?.username }}</span>
        <button type="button" @click="logout">退出登录</button>
      </div>
      <h1>无人机航拍场景异常检测与可视分析系统</h1>
      <nav class="main-nav" aria-label="系统主导航">
        <button
          v-for="item in mainPages"
          :key="item.key"
          :class="{ active: activePage === item.key }"
          type="button"
          @click="switchMainPage(item.key)"
        >
          {{ item.label }}
        </button>
      </nav>
    </header>

    <main class="container">
      <section v-if="activePage === 'home'" class="home-page">
        <div class="welcome-band">
          <div class="welcome-copy">
            <span>UAV Inspection Analysis</span>
            <h2>欢迎使用无人机航拍异常检测工作台</h2>
            <p>
              系统面向航拍图像巡检场景，提供目标识别、场景理解、异常分析、统计图表和巡检建议生成能力。
            </p>
            <button type="button" @click="switchMainPage('upload')">开始上传图片</button>
          </div>
          <div class="console-preview" aria-label="系统能力预览">
            <div class="console-header">
              <strong>Inspection Console</strong>
              <span>ONLINE</span>
            </div>
            <div class="console-main">
              <div>
                <small>综合风险</small>
                <strong>中风险</strong>
              </div>
              <div>
                <small>检测目标</small>
                <strong>26</strong>
              </div>
              <div>
                <small>异常模块</small>
                <strong>4</strong>
              </div>
            </div>
            <div class="console-list">
              <p><span></span>车辆越界异常分析</p>
              <p><span></span>道路交通密度评估</p>
              <p><span></span>水域周边风险提示</p>
            </div>
          </div>
        </div>

        <section class="workflow-card">
          <div class="section-heading">
            <h2>系统流程</h2>
            <p>从航拍图像输入到异常判断，形成完整的巡检分析闭环。</p>
          </div>
          <div class="workflow-steps">
            <article>
              <span>01</span>
              <h3>上传航拍图像</h3>
              <p>选择无人机航拍图片，系统读取原图并生成预览。</p>
            </article>
            <article>
              <span>02</span>
              <h3>智能目标识别</h3>
              <p>调用自训练 YOLO 模型识别车辆、道路、水域等目标。</p>
            </article>
            <article>
              <span>03</span>
              <h3>异常模块分析</h3>
              <p>分析车辆越界、交通密度、水域风险和检测可信度。</p>
            </article>
            <article>
              <span>04</span>
              <h3>生成巡检建议</h3>
              <p>输出风险等级、处理意见和可执行的后续操作。</p>
            </article>
          </div>
        </section>

        <div class="feature-grid">
          <article>
            <h3>场景要素识别</h3>
            <p>识别车辆、道路、建筑、树木、水域等关键航拍要素。</p>
          </article>
          <article>
            <h3>异常模块分析</h3>
            <p>围绕车辆越界、交通密度、水域周边风险和检测可信度进行分析。</p>
          </article>
          <article>
            <h3>巡检建议生成</h3>
            <p>根据风险等级和异常模块，自动生成可执行的后续巡检建议。</p>
          </article>
        </div>
      </section>

      <section v-if="activePage === 'upload'" class="card upload-card">
        <h2>图片上传</h2>

        <div class="upload-box">
          <label class="file-picker">
            <input type="file" accept="image/*" @change="handleFileChange" />
            <span>选择图片</span>
          </label>

          <div class="file-meta">
            <strong>{{ selectedFile ? selectedFile.name : '未选择图片' }}</strong>
            <small>{{ selectedFile ? '支持 jpg、png 等常见图片格式' : '请选择一张航拍图片进行检测' }}</small>
          </div>

          <button :disabled="!selectedFile || loading" @click="detectImage">
            {{ loading ? '检测中...' : '开始智能识别' }}
          </button>
        </div>

        <div v-if="previewUrl" class="preview">
          <h3>原始图片预览</h3>
          <img :src="previewUrl" alt="原始图片" />
        </div>

        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </section>

      <section v-if="activePage === 'results' && result" class="result-shell">
        <nav class="page-tabs" aria-label="检测结果导航">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="{ active: activeTab === tab.key }"
            type="button"
            @click="switchTab(tab.key)"
          >
            {{ tab.label }}
          </button>
        </nav>

        <section v-if="activeTab === 'overview'" class="card result-card">
          <h2>检测总览</h2>

          <div class="result-layout">
            <div class="image-panel">
              <h3>检测结果图</h3>
              <img :src="backendBaseUrl + result.result_image_url" alt="检测结果图" />
            </div>

            <div class="summary-panel">
              <h3>检测摘要</h3>
              <p>图片名称：{{ result.original_filename }}</p>
              <p>检测目标总数：{{ result.total_count }}</p>
              <p v-if="analysis">场景类型：{{ analysis.scene_type }}</p>
              <p v-if="analysis">综合风险：<span :class="['risk-badge', riskClass(analysis.risk_level)]">{{ analysis.risk_level }}</span></p>

              <h3>自动分析报告</h3>
              <div class="report">
                {{ result.report }}
              </div>
            </div>
          </div>
        </section>

        <section v-if="activeTab === 'analysis' && analysis" class="card analysis-card">
          <div class="section-title">
            <div>
              <h2>场景理解与异常分析</h2>
              <p>{{ analysis.summary }}</p>
            </div>
            <div :class="['score-card', riskClass(analysis.risk_level)]">
              <span>风险评分</span>
              <strong>{{ analysis.risk_score }}</strong>
            </div>
          </div>

          <div class="tag-row" v-if="analysis.scene_tags && analysis.scene_tags.length">
            <span v-for="tag in analysis.scene_tags" :key="tag" class="scene-tag">{{ tag }}</span>
          </div>

          <div class="metric-grid">
            <div class="metric-item">
              <span>车辆总数</span>
              <strong>{{ analysis.metrics.vehicle_count }}</strong>
            </div>
            <div class="metric-item">
              <span>道路内车辆</span>
              <strong>{{ analysis.metrics.road_vehicle_count }}</strong>
            </div>
            <div class="metric-item">
              <span>疑似越界车辆</span>
              <strong>{{ analysis.metrics.offroad_vehicle_count }}</strong>
            </div>
            <div class="metric-item">
              <span>水域邻近车辆</span>
              <strong>{{ analysis.metrics.water_near_vehicle_count }}</strong>
            </div>
          </div>

          <div class="module-grid">
            <article
              v-for="module in analysis.modules"
              :key="module.key"
              :class="['module-card', statusClass(module.status)]"
            >
              <div class="module-header">
                <h3>{{ module.title }}</h3>
                <span>{{ module.status }}</span>
              </div>
              <p class="module-reason">{{ module.reason }}</p>
              <p class="module-suggestion">{{ module.suggestion }}</p>
            </article>
          </div>
        </section>

        <section v-if="activeTab === 'charts'" class="tab-stack">
          <div class="grid">
            <div class="card">
              <h2>类别数量统计</h2>
              <div ref="barChartRef" class="chart"></div>
            </div>

            <div class="card">
              <h2>类别占比统计</h2>
              <div ref="pieChartRef" class="chart"></div>
            </div>
          </div>

          <section class="card">
            <h2>场景面积占比</h2>
            <table v-if="analysis && analysis.area_ratio && Object.keys(analysis.area_ratio).length > 0" class="ratio-table">
              <thead>
                <tr>
                  <th>类别</th>
                  <th>估算占比</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, name) in analysis.area_ratio" :key="name">
                  <td>{{ name }}</td>
                  <td>
                    <div class="ratio-cell">
                      <div class="ratio-bar">
                        <span :style="{ width: `${Math.min(value, 100)}%` }"></span>
                      </div>
                      {{ value }}%
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else class="empty">暂无可用于面积占比分析的目标。</p>
          </section>
        </section>

        <section v-if="activeTab === 'recommendations' && analysis" class="card recommendation-card">
          <div class="section-title">
            <div>
              <h2>巡检建议</h2>
              <p>根据场景类型、风险等级和异常模块结果，生成后续巡检处理建议。</p>
            </div>
            <div :class="['score-card', riskClass(analysis.risk_level)]">
              <span>建议优先级</span>
              <strong>{{ recommendationPriority }}</strong>
            </div>
          </div>

          <div class="recommendation-summary">
            <h3>综合处理意见</h3>
            <p>{{ overallRecommendation }}</p>
          </div>

          <div class="recommendation-grid">
            <article
              v-for="item in recommendationItems"
              :key="item.key"
              :class="['recommendation-item', statusClass(item.status)]"
            >
              <span>{{ item.status }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.suggestion }}</p>
            </article>
          </div>

          <div class="action-panel">
            <h3>后续操作</h3>
            <ol>
              <li v-for="action in followUpActions" :key="action">{{ action }}</li>
            </ol>
          </div>
        </section>

        <section v-if="activeTab === 'details'" class="card">
          <h2>检测详情</h2>

          <table v-if="result.detections && result.detections.length > 0">
            <thead>
              <tr>
                <th>序号</th>
                <th>类别</th>
                <th>置信度</th>
                <th>面积</th>
                <th>坐标</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in result.detections" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ item.class_name }}</td>
                <td>{{ (item.confidence * 100).toFixed(2) }}%</td>
                <td>{{ item.area }}</td>
                <td>
                  x1={{ item.box.x1 }},
                  y1={{ item.box.y1 }},
                  x2={{ item.box.x2 }},
                  y2={{ item.box.y2 }}
                </td>
              </tr>
            </tbody>
          </table>

          <p v-else class="empty">
            当前图片没有检测到自训练航拍场景模型可识别的目标。
          </p>
        </section>
      </section>

      <section v-if="activePage === 'results' && !result" class="card empty-result">
        <h2>暂无检测结果</h2>
        <p>请先进入图片上传页面，选择航拍图片并完成智能识别。</p>
        <button type="button" @click="switchMainPage('upload')">去上传图片</button>
      </section>
    </main>
    </template>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const backendBaseUrl = 'http://127.0.0.1:8000'

const selectedFile = ref(null)
const previewUrl = ref('')
const result = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const activePage = ref('home')
const activeTab = ref('overview')
const authToken = ref(localStorage.getItem('auth_token') || '')
const currentUser = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
const loginLoading = ref(false)
const loginError = ref('')
const loginForm = ref({
  username: 'admin',
  password: 'admin123'
})

const barChartRef = ref(null)
const pieChartRef = ref(null)

const analysis = computed(() => result.value?.analysis || null)
const mainPages = [
  { key: 'home', label: '系统首页' },
  { key: 'upload', label: '图片上传' },
  { key: 'results', label: '检测结果' }
]
const tabs = [
  { key: 'overview', label: '检测总览' },
  { key: 'analysis', label: '异常分析' },
  { key: 'charts', label: '统计图表' },
  { key: 'recommendations', label: '巡检建议' },
  { key: 'details', label: '检测详情' }
]

const recommendationItems = computed(() => {
  if (!analysis.value?.modules) return []
  return analysis.value.modules.map(module => ({
    key: module.key,
    title: module.title,
    status: module.status,
    suggestion: module.suggestion
  }))
})

const recommendationPriority = computed(() => {
  const level = analysis.value?.risk_level
  if (level === '高风险') return '高'
  if (level === '中风险') return '中'
  if (level === '低风险') return '低'
  return '常规'
})

const overallRecommendation = computed(() => {
  if (!analysis.value) return ''
  const { scene_type, risk_level, metrics } = analysis.value
  const base = `当前图像判断为${scene_type}，综合风险等级为${risk_level}。`

  if (risk_level === '高风险') {
    return `${base}建议优先安排人工复核，对异常区域进行二次确认，并结合现场巡检或连续航拍数据判断风险变化。`
  }

  if (risk_level === '中风险') {
    return `${base}建议将该图像纳入重点复查列表，优先关注车辆分布、道路区域和水域周边目标。`
  }

  if (metrics?.offroad_vehicle_count > 0 || metrics?.water_near_vehicle_count > 0) {
    return `${base}虽然综合等级不高，但存在局部目标需要关注，建议针对异常模块进行定点复核。`
  }

  return `${base}暂未发现明显异常，可作为常规巡检记录归档，并在后续批量图像中继续对比观察。`
})

const followUpActions = computed(() => {
  if (!analysis.value) return []
  const actions = ['保存检测结果图和分析报告，作为本次巡检记录。']
  const metrics = analysis.value.metrics || {}

  if (metrics.offroad_vehicle_count > 0) {
    actions.push('复核疑似越界车辆位置，判断是否为停车区域、非道路行驶或检测误差。')
  }

  if (metrics.water_near_vehicle_count > 0) {
    actions.push('检查水域周边车辆活动，必要时标记为临水安全风险点。')
  }

  if (metrics.vehicle_count >= 12) {
    actions.push('对车辆密集区域进行交通密度评估，可结合多张图片判断拥堵趋势。')
  }

  if (metrics.low_confidence_count > 0) {
    actions.push('对低置信度目标进行人工确认，必要时提高图像分辨率后重新检测。')
  }

  if (actions.length === 1) {
    actions.push('继续上传同区域不同角度或不同时刻图片，形成可对比的巡检样本。')
  }

  return actions
})

let barChart = null
let pieChart = null

function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  selectedFile.value = file
  result.value = null
  errorMessage.value = ''
  activeTab.value = 'overview'

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  previewUrl.value = URL.createObjectURL(file)
}

async function detectImage() {
  if (!selectedFile.value) {
    errorMessage.value = '请先选择一张图片'
    return
  }

  loading.value = true
  errorMessage.value = ''
  result.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await axios.post(`${backendBaseUrl}/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${authToken.value}`
      }
    })

    result.value = response.data
    activePage.value = 'results'
    activeTab.value = 'overview'
  } catch (error) {
    console.error(error)
    if (error.response?.status === 401) {
      clearAuth()
      errorMessage.value = '登录已过期，请重新登录'
    } else {
      errorMessage.value = '检测失败，请确认后端服务是否正在运行，地址是否为 http://127.0.0.1:8000'
    }
  } finally {
    loading.value = false
  }
}

async function login() {
  loginLoading.value = true
  loginError.value = ''

  try {
    const response = await axios.post(`${backendBaseUrl}/auth/login`, loginForm.value)
    authToken.value = response.data.token
    currentUser.value = response.data.user
    localStorage.setItem('auth_token', authToken.value)
    localStorage.setItem('auth_user', JSON.stringify(currentUser.value))
  } catch (error) {
    console.error(error)
    loginError.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loginLoading.value = false
  }
}

async function logout() {
  try {
    if (authToken.value) {
      await axios.post(`${backendBaseUrl}/auth/logout`, null, {
        headers: {
          Authorization: `Bearer ${authToken.value}`
        }
      })
    }
  } catch (error) {
    console.error(error)
  } finally {
    clearAuth()
  }
}

function clearAuth() {
  authToken.value = ''
  currentUser.value = null
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_user')
}

async function switchMainPage(pageKey) {
  activePage.value = pageKey
  if (pageKey === 'results' && activeTab.value === 'charts') {
    await nextTick()
    renderCharts()
  }
}

async function switchTab(tabKey) {
  activeTab.value = tabKey
  if (tabKey === 'charts') {
    await nextTick()
    renderCharts()
  }
}

function renderCharts() {
  if (!result.value) return

  const classCount = result.value.class_count || {}
  const names = Object.keys(classCount)
  const values = Object.values(classCount)

  if (barChart) {
    barChart.dispose()
  }

  if (pieChart) {
    pieChart.dispose()
  }

  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      tooltip: {},
      xAxis: {
        type: 'category',
        data: names
      },
      yAxis: {
        type: 'value',
        minInterval: 1
      },
      series: [
        {
          name: '数量',
          type: 'bar',
          data: values
        }
      ]
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          name: '类别占比',
          type: 'pie',
          radius: '65%',
          data: names.map(name => ({
            name,
            value: classCount[name]
          }))
        }
      ]
    })
  }
}

function riskClass(level) {
  if (level === '高风险' || level === '严重异常') return 'risk-high'
  if (level === '中风险' || level === '中度异常') return 'risk-medium'
  if (level === '低风险' || level === '轻微异常') return 'risk-low'
  return 'risk-normal'
}

function statusClass(status) {
  return riskClass(status)
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fb;
  color: #1f2937;
}

.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    linear-gradient(rgba(15, 23, 42, 0.62), rgba(15, 23, 42, 0.7)),
    url('/src/assets/hero.png') center / cover no-repeat;
}

.login-panel {
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: 1.1fr 380px;
  gap: 28px;
  align-items: center;
}

.login-copy {
  color: #ffffff;
  text-align: left;
}

.login-copy h1 {
  margin: 0;
  max-width: 620px;
  color: #ffffff;
  font-size: 36px;
  line-height: 1.25;
}

.login-copy p {
  margin-top: 16px;
  max-width: 580px;
  color: #dbeafe;
  line-height: 1.8;
}

.login-card {
  display: grid;
  gap: 16px;
  padding: 26px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.24);
  text-align: left;
}

.login-card h2 {
  margin: 0;
}

.login-card label {
  display: grid;
  gap: 8px;
  color: #475569;
  font-size: 14px;
  font-weight: 700;
}

.login-card input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 11px 12px;
  color: #111827;
  background: #ffffff;
  font-size: 15px;
}

.login-card input:focus {
  outline: 2px solid #93c5fd;
  border-color: #2563eb;
}

.login-card button {
  width: 100%;
  min-height: 42px;
}

.login-hint {
  color: #64748b;
  font-size: 13px;
  text-align: center;
}

.header {
  position: relative;
  padding: 36px 24px;
  text-align: center;
  background: linear-gradient(135deg, #1e3a8a, #2563eb);
  color: white;
}

.user-bar {
  position: absolute;
  top: 14px;
  right: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #dbeafe;
  font-size: 13px;
}

.user-bar button {
  padding: 6px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  font-size: 13px;
}

.header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
}

.main-nav {
  display: inline-flex;
  gap: 8px;
  margin-top: 22px;
  padding: 6px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.14);
}

.main-nav button {
  min-width: 96px;
  padding: 8px 14px;
  border-radius: 6px;
  background: transparent;
  color: #dbeafe;
  font-weight: 700;
}

.main-nav button.active {
  background: #ffffff;
  color: #1e3a8a;
}

.container {
  max-width: min(1480px, calc(100vw - 48px));
  margin: 24px auto;
  padding: 0 0 40px;
}

.home-page {
  display: grid;
  gap: 22px;
}

.welcome-band {
  min-height: 430px;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) 420px;
  align-items: end;
  gap: 32px;
  padding: 34px;
  overflow: hidden;
  border-radius: 12px;
  background:
    linear-gradient(90deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.28)),
    url('/src/assets/hero.png') center / cover no-repeat;
  color: #ffffff;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.16);
}

.welcome-copy {
  max-width: 680px;
}

.welcome-band span {
  display: inline-flex;
  margin-bottom: 12px;
  color: #bfdbfe;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.welcome-band h2 {
  max-width: 620px;
  margin: 0;
  color: #ffffff;
  font-size: 32px;
}

.welcome-band p {
  max-width: 660px;
  margin: 14px 0 22px;
  color: #e0f2fe;
  line-height: 1.8;
}

.console-preview {
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 310px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.72);
  backdrop-filter: blur(10px);
}

.console-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #ffffff;
}

.console-header span {
  margin: 0;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.18);
  color: #86efac;
  font-size: 11px;
  letter-spacing: 0;
}

.console-main {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.console-main div {
  padding: 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
}

.console-main small {
  display: block;
  color: #bfdbfe;
  font-size: 12px;
  margin-bottom: 8px;
}

.console-main strong {
  color: #ffffff;
  font-size: 22px;
}

.console-list {
  display: grid;
  gap: 10px;
}

.console-list p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #dbeafe;
  font-size: 14px;
}

.console-list p span {
  width: 8px;
  height: 8px;
  margin: 0;
  border-radius: 999px;
  background: #60a5fa;
}

.workflow-card {
  padding: 24px;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
  text-align: left;
}

.section-heading h2 {
  margin: 0;
  color: #111827;
}

.section-heading p {
  max-width: 520px;
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  overflow: hidden;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #f8fafc;
}

.workflow-steps article {
  position: relative;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  column-gap: 10px;
  align-items: start;
  min-height: 0;
  padding: 16px;
  border-right: 1px solid #dbe4f0;
  background: transparent;
  text-align: left;
}

.workflow-steps article:last-child {
  border-right: none;
}

.workflow-steps span {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  margin: 0;
  border-radius: 8px;
  background: #dbeafe;
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
}

.workflow-steps h3 {
  margin: 0 0 5px;
  color: #111827;
  font-size: 15px;
}

.workflow-steps p {
  grid-column: 2;
  margin: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.55;
  word-break: normal;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.feature-grid article {
  min-height: 150px;
  padding: 22px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  text-align: left;
}

.feature-grid h3 {
  margin: 0 0 10px;
  color: #111827;
}

.feature-grid p {
  margin: 0;
  color: #64748b;
  line-height: 1.75;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 22px;
  margin-bottom: 22px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.card h2 {
  margin: 0 0 18px;
  font-size: 21px;
}

.result-shell {
  margin-top: 22px;
}

.page-tabs {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
  padding: 10px;
  overflow-x: auto;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}

.page-tabs button {
  flex: 0 0 auto;
  min-width: 108px;
  min-height: 40px;
  padding: 8px 14px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: #f8fafc;
  color: #475569;
  font-weight: 700;
}

.page-tabs button.active {
  background: #2563eb;
  color: #ffffff;
}

.tab-stack {
  display: block;
}

.upload-box {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.file-picker {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 18px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #1e3a8a;
  font-weight: 700;
  cursor: pointer;
  transition:
    border-color 0.2s,
    box-shadow 0.2s,
    background 0.2s;
}

.file-picker:hover {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.12);
}

.file-picker input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.file-meta {
  min-width: 240px;
  display: grid;
  gap: 3px;
  text-align: left;
}

.file-meta strong {
  max-width: 360px;
  overflow: hidden;
  color: #111827;
  font-size: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta small {
  color: #64748b;
  font-size: 12px;
}

button {
  border: none;
  background: #2563eb;
  color: white;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
}

button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.preview {
  margin-top: 20px;
}

.preview img,
.image-panel img {
  max-width: 100%;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.result-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

.summary-panel p {
  margin: 10px 0;
}

.report {
  background: #f3f4f6;
  border-left: 4px solid #2563eb;
  padding: 14px;
  border-radius: 8px;
  line-height: 1.8;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.section-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}

.section-title p {
  color: #4b5563;
  line-height: 1.8;
  margin: 0;
}

.score-card {
  min-width: 112px;
  padding: 12px 14px;
  border-radius: 8px;
  text-align: center;
}

.score-card span {
  display: block;
  font-size: 13px;
  margin-bottom: 4px;
}

.score-card strong {
  font-size: 28px;
  line-height: 1;
}

.risk-normal {
  background: #ecfdf5;
  color: #047857;
}

.risk-low {
  background: #eff6ff;
  color: #1d4ed8;
}

.risk-medium {
  background: #fff7ed;
  color: #c2410c;
}

.risk-high {
  background: #fef2f2;
  color: #b91c1c;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.scene-tag {
  background: #eef2ff;
  color: #3730a3;
  border: 1px solid #c7d2fe;
  border-radius: 999px;
  padding: 5px 11px;
  font-size: 13px;
  font-weight: 600;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.metric-item {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px;
}

.metric-item span {
  display: block;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 8px;
}

.metric-item strong {
  color: #0f172a;
  font-size: 24px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.module-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #ffffff;
}

.module-card.risk-normal {
  border-color: #bbf7d0;
}

.module-card.risk-low {
  border-color: #bfdbfe;
}

.module-card.risk-medium {
  border-color: #fed7aa;
}

.module-card.risk-high {
  border-color: #fecaca;
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.module-header h3 {
  margin: 0;
  color: #111827;
  font-size: 16px;
}

.module-header span {
  flex: 0 0 auto;
  font-size: 12px;
  font-weight: 700;
}

.module-reason,
.module-suggestion {
  margin: 0;
  line-height: 1.7;
  font-size: 14px;
}

.module-suggestion {
  color: #475569;
  margin-top: 8px;
}

.recommendation-summary {
  margin-bottom: 18px;
  padding: 16px;
  border-left: 4px solid #2563eb;
  border-radius: 8px;
  background: #f8fafc;
}

.recommendation-summary h3,
.action-panel h3 {
  margin: 0 0 10px;
  color: #111827;
  font-size: 17px;
}

.recommendation-summary p {
  margin: 0;
  color: #334155;
  line-height: 1.8;
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.recommendation-item {
  min-height: 130px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
}

.recommendation-item span {
  display: inline-flex;
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 700;
}

.recommendation-item h3 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 16px;
}

.recommendation-item p {
  margin: 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.7;
}

.action-panel {
  padding: 16px;
  border-radius: 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.action-panel ol {
  margin: 0;
  padding-left: 20px;
  color: #334155;
  line-height: 1.8;
}

.ratio-table {
  margin-bottom: 10px;
}

.ratio-cell {
  display: grid;
  grid-template-columns: minmax(120px, 1fr) 58px;
  align-items: center;
  gap: 12px;
}

.ratio-bar {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: #e5e7eb;
}

.ratio-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #2563eb;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}

.chart {
  width: 100%;
  height: 360px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  border-bottom: 1px solid #e5e7eb;
  padding: 11px 8px;
  text-align: left;
}

th {
  background: #f9fafb;
  font-weight: 600;
}

.error {
  color: #dc2626;
  margin-top: 16px;
}

.empty {
  color: #6b7280;
}

@media (max-width: 900px) {
  .login-panel {
    grid-template-columns: 1fr;
  }

  .login-copy h1 {
    font-size: 28px;
  }

  .result-layout,
  .grid,
  .module-grid,
  .metric-grid,
  .recommendation-grid,
  .feature-grid,
  .workflow-steps {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .main-nav {
    width: 100%;
    justify-content: center;
    overflow-x: auto;
  }

  .welcome-band {
    grid-template-columns: 1fr;
    min-height: 300px;
    padding: 24px;
  }

  .console-preview {
    min-height: 240px;
  }

  .welcome-band h2 {
    font-size: 26px;
  }

  .section-title {
    flex-direction: column;
  }

  .header h1 {
    font-size: 24px;
  }

  .user-bar {
    position: static;
    justify-content: center;
    margin-bottom: 18px;
  }
}
</style>
