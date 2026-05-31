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
      <p class="system-name">无人机航拍场景异常检测与可视分析系统</p>
      <h1>{{ currentPageTitle }}</h1>
      <nav class="main-nav" aria-label="主导航">
        <button
          v-for="item in mainNavItems"
          :key="item.key"
          :class="{ active: activePage === item.key }"
          :disabled="item.disabled"
          type="button"
          @click="switchMainPage(item.key)"
        >
          <span>{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </nav>
      <div v-if="activePage !== 'home'" class="page-actions">
        <button type="button" @click="goBack">返回</button>
        <button type="button" @click="goHome">首页</button>
      </div>
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
            <div class="welcome-actions">
              <button type="button" @click="switchMainPage('upload')">开始上传图片</button>
              <button class="secondary-button" type="button" @click="switchMainPage('logs')">查看检测日志</button>
            </div>
          </div>
          <div class="console-preview" aria-label="系统能力预览">
            <div class="console-header">
              <strong>Inspection Console</strong>
              <span>{{ result ? 'UPDATED' : 'ONLINE' }}</span>
            </div>
            <div class="console-main">
              <div>
                <small>综合风险</small>
                <strong :class="['console-risk-value', result ? riskClass(consoleRiskLevel) : 'risk-pending']">
                  {{ consoleRiskLevel }}
                </strong>
              </div>
              <div>
                <small>检测目标</small>
                <strong>{{ consoleTargetCount }}</strong>
              </div>
              <div>
                <small>异常模块</small>
                <strong>{{ consoleAbnormalCount }}</strong>
              </div>
            </div>
            <div class="console-list">
              <p v-for="item in consoleModules" :key="item.title">
                <span :class="riskClass(item.status)"></span>{{ item.title }}
              </p>
            </div>
          </div>
        </div>

        <div class="status-grid" aria-label="工作台概览">
          <article v-for="item in quickStats" :key="item.label">
            <span>{{ item.label }}</span>
            <strong :class="item.className">{{ item.value }}</strong>
            <small>{{ item.hint }}</small>
          </article>
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

        <div
          :class="['dropzone', { dragging: isDraggingFile, ready: selectedFile }]"
          @dragenter.prevent="handleDragEnter"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleFileDrop"
        >
          <label class="dropzone-picker">
            <input type="file" accept="image/*" @change="handleFileChange" />
            <span class="dropzone-icon">+</span>
            <strong>{{ selectedFile ? selectedFile.name : '拖拽航拍图片到这里' }}</strong>
            <small>
              {{ selectedFile ? '已选择图片，可重新拖入或点击更换' : '支持 jpg、png 等常见图片格式，也可以点击选择图片' }}
            </small>
          </label>
        </div>

        <div class="upload-actions">
          <button :disabled="!selectedFile || loading" @click="detectImage">
            {{ loading ? '检测中...' : '开始智能识别' }}
          </button>
        </div>

        <div class="mode-panel">
          <div class="mode-copy">
            <span>检测策略</span>
            <strong>{{ selectedDetectionMode.label }}</strong>
            <small>{{ selectedDetectionMode.hint }}</small>
          </div>

          <div class="mode-selector" aria-label="检测模式选择">
            <label
              v-for="mode in detectionModes"
              :key="mode.value"
              :class="{ active: detectionMode === mode.value }"
            >
              <input v-model="detectionMode" type="radio" name="detection-mode" :value="mode.value" />
              <span>{{ mode.shortLabel }}</span>
            </label>
          </div>
        </div>

        <div v-if="previewUrl" class="preview">
          <h3>原始图片预览</h3>
          <img :src="previewUrl" alt="原始图片" />
        </div>

        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </section>

      <section v-if="activePage === 'logs'" class="card log-card">
        <div class="section-heading">
          <div>
            <h2>检测日志</h2>
            <p>记录每一次图片检测的操作时间、检测模式、目标数量和分析结果。</p>
          </div>
          <button type="button" :disabled="logsLoading" @click="fetchDetectionLogs">
            {{ logsLoading ? '刷新中...' : '刷新日志' }}
          </button>
        </div>

        <p v-if="logsError" class="error">{{ logsError }}</p>
        <p v-else-if="logsLoading" class="empty">正在加载检测日志...</p>

        <div v-else-if="detectionLogs.length" class="log-list">
          <article v-for="log in detectionLogs" :key="log.id" class="log-item">
            <div class="log-main">
              <img :src="backendBaseUrl + log.result_image_url" alt="检测结果缩略图" />
              <div>
                <h3>{{ log.original_filename }}</h3>
                <p>{{ formatDateTime(log.created_at) }} · {{ log.detection_mode_label }}</p>
                <p>{{ log.scene_type }}，共检测到 {{ log.total_count }} 个目标。</p>
                <div class="log-tags">
                  <span :class="['risk-badge', riskClass(log.risk_level)]">{{ log.risk_level }}</span>
                  <span>风险评分 {{ log.risk_score }}</span>
                  <span v-if="log.models_used?.length">{{ formatModelsUsed(log.models_used) }}</span>
                </div>
              </div>
            </div>

            <div class="log-report">
              {{ log.report }}
            </div>
          </article>
        </div>

        <div v-else class="empty log-empty">
          <h3>暂无检测日志</h3>
          <p>完成一次图片检测后，系统会在这里自动生成日志记录。</p>
          <button type="button" @click="switchMainPage('upload')">去上传图片</button>
        </div>
      </section>

      <section v-if="activePage === 'results' && result" class="result-shell">
        <div class="result-toolbar">
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

          <button
            class="export-button"
            type="button"
            :disabled="exportLoading || !result"
            @click="exportInspectionDocument"
          >
            {{ exportLoading ? '正在导出...' : '导出巡检文档' }}
          </button>
        </div>
        <p v-if="exportError" class="error export-status">{{ exportError }}</p>
        <p v-else-if="exportMessage" class="success export-status">{{ exportMessage }}</p>

        <section v-if="activeTab === 'overview'" class="card result-card">
          <h2>检测总览</h2>

          <section class="compare-panel">
            <h3>原始图片与检测结果对比</h3>
            <div class="compare-grid">
              <div>
                <span>原始图片</span>
                <button
                  v-if="previewUrl"
                  class="image-detail-trigger"
                  type="button"
                  @click="openImageDetail('original')"
                >
                  <img :src="previewUrl" alt="原始图片" />
                  <span class="image-detail-badge">点击查看详情</span>
                </button>
                <p v-else class="empty compare-empty">当前会话暂无原始图片预览。</p>
              </div>
              <div>
                <span>检测结果图</span>
                <button class="image-detail-trigger" type="button" @click="openImageDetail('result')">
                  <img :src="backendBaseUrl + result.result_image_url" alt="检测结果图" />
                  <span class="image-detail-badge">点击查看详情</span>
                </button>
              </div>
            </div>
          </section>

          <div class="result-layout">
            <div class="image-panel">
              <h3>检测结果图</h3>
              <button class="image-detail-trigger image-panel-trigger" type="button" @click="openImageDetail('result')">
                <img :src="backendBaseUrl + result.result_image_url" alt="检测结果图" />
                <span class="image-detail-badge">点击查看详情</span>
              </button>
            </div>

            <div class="summary-panel">
              <h3>检测摘要</h3>
              <p>图片名称：{{ result.original_filename }}</p>
              <p>检测模式：{{ result.detection_mode_label || selectedDetectionMode.label }}</p>
              <p v-if="result.models_used?.length">启用模型：{{ formatModelsUsed(result.models_used) }}</p>
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
                <th>模型来源</th>
                <th>置信度</th>
                <th>面积</th>
                <th>坐标</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in result.detections" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ item.class_name }}</td>
                <td>{{ modelRoleLabel(item.model_role) }}</td>
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

    <div
      v-if="imageDetailOpen"
      class="image-detail-modal"
      role="dialog"
      aria-modal="true"
      :aria-label="imageDetailTitle"
      @click.self="closeImageDetail"
    >
      <div class="image-detail-dialog">
        <div class="image-detail-header">
          <div>
            <span>图片详情</span>
            <h2>{{ imageDetailTitle }}</h2>
          </div>
          <button class="image-detail-close" type="button" aria-label="关闭图片详情" @click="closeImageDetail">×</button>
        </div>

        <div class="image-detail-body">
          <div class="image-detail-viewer">
            <img :src="imageDetailSrc" :alt="imageDetailTitle" />
          </div>

          <aside class="image-detail-info">
            <h3>检测信息</h3>
            <p>图片名称：{{ result?.original_filename || '当前图片' }}</p>
            <p v-if="result">检测模式：{{ result.detection_mode_label || selectedDetectionMode.label }}</p>
            <p v-if="imageDetailType === 'result' && result">目标总数：{{ result.total_count }}</p>
            <p v-if="imageDetailType === 'original'">原始图片用于和检测结果进行位置对照。</p>

            <div v-if="imageDetailType === 'result'" class="detail-detection-list">
              <h3>目标清单</h3>
              <ul v-if="result?.detections?.length">
                <li v-for="(item, index) in result.detections" :key="`${item.class_name}-${index}`">
                  <strong>{{ item.class_name }}</strong>
                  <span>{{ modelRoleLabel(item.model_role) }}</span>
                  <small>置信度 {{ formatConfidence(item.confidence) }}</small>
                </li>
              </ul>
              <p v-else class="empty">暂无检测目标。</p>
            </div>
          </aside>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onBeforeUnmount, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const backendBaseUrl = 'http://127.0.0.1:8000'

const selectedFile = ref(null)
const previewUrl = ref('')
const result = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const detectionMode = ref('fusion')
const isDraggingFile = ref(false)
const dragDepth = ref(0)
const activePage = ref('home')
const activeTab = ref('overview')
const authToken = ref(localStorage.getItem('auth_token') || '')
const currentUser = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
const loginLoading = ref(false)
const loginError = ref('')
const imageDetailOpen = ref(false)
const imageDetailType = ref('result')
const detectionLogs = ref([])
const logsLoading = ref(false)
const logsError = ref('')
const exportLoading = ref(false)
const exportError = ref('')
const exportMessage = ref('')
const loginForm = ref({
  username: 'admin',
  password: 'admin123'
})

const barChartRef = ref(null)
const pieChartRef = ref(null)

const analysis = computed(() => result.value?.analysis || null)
const imageDetailTitle = computed(() => {
  return imageDetailType.value === 'original' ? '原始图片' : '检测结果图'
})
const imageDetailSrc = computed(() => {
  if (imageDetailType.value === 'original') return previewUrl.value
  return result.value?.result_image_url ? `${backendBaseUrl}${result.value.result_image_url}` : ''
})
const detectionModes = [
  {
    value: 'fusion',
    label: '融合检测（推荐）',
    shortLabel: '融合',
    description: '场景要素 + 小目标',
    hint: '默认巡检策略会自动结合场景语义和细粒度目标，用于生成完整的异常分析与巡检建议。'
  },
  {
    value: 'fine',
    label: '细粒度目标检测',
    shortLabel: '细粒度',
    description: '车辆、行人等小目标',
    hint: '细粒度模型主要识别车辆和人员，缺少道路、水域语义时部分异常模块会以复核提示为主。'
  }
]
const selectedDetectionMode = computed(() => {
  return detectionModes.find(mode => mode.value === detectionMode.value) || detectionModes[0]
})
const pageTitles = {
  home: '系统首页',
  upload: '图片上传',
  results: '检测结果',
  logs: '检测日志'
}
const currentPageTitle = computed(() => pageTitles[activePage.value] || '系统首页')
const mainNavItems = computed(() => [
  { key: 'home', label: '首页', icon: '⌂', disabled: false },
  { key: 'upload', label: '上传检测', icon: '+', disabled: false },
  { key: 'results', label: '结果分析', icon: '▣', disabled: !result.value },
  { key: 'logs', label: '检测日志', icon: '≡', disabled: false }
])
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

const consoleRiskLevel = computed(() => analysis.value?.risk_level || '待检测')

const consoleTargetCount = computed(() => result.value?.total_count ?? '--')

const consoleAbnormalCount = computed(() => {
  if (!analysis.value?.modules) return '--'
  return analysis.value.modules.filter(module => module.score >= 20).length
})

const consoleModules = computed(() => {
  if (!analysis.value?.modules?.length) {
    return [
      { title: '车辆越界异常分析', status: '正常' },
      { title: '道路交通密度评估', status: '正常' },
      { title: '水域周边风险提示', status: '正常' }
    ]
  }

  return analysis.value.modules.slice(0, 3).map(module => ({
    title: module.title,
    status: module.status
  }))
})

const quickStats = computed(() => [
  {
    label: '当前任务',
    value: result.value ? '已完成' : selectedFile.value ? '待检测' : '未开始',
    hint: selectedFile.value ? selectedFile.value.name : '上传一张航拍图像开始分析',
    className: result.value ? 'stat-success' : selectedFile.value ? 'stat-warning' : ''
  },
  {
    label: '检测目标',
    value: consoleTargetCount.value,
    hint: result.value ? '本次识别目标总数' : '完成检测后自动统计',
    className: result.value ? 'stat-info' : ''
  },
  {
    label: '综合风险',
    value: consoleRiskLevel.value,
    hint: analysis.value ? `风险评分 ${analysis.value.risk_score}` : '等待异常分析结果',
    className: riskClass(consoleRiskLevel.value)
  },
  {
    label: '日志记录',
    value: detectionLogs.value.length || '--',
    hint: detectionLogs.value.length ? '已缓存检测记录' : '进入日志页后同步加载',
    className: detectionLogs.value.length ? 'stat-info' : ''
  }
])

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
let resizeFrame = 0

onMounted(() => {
  window.addEventListener('resize', handleChartResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleChartResize)
  if (resizeFrame) {
    cancelAnimationFrame(resizeFrame)
  }
  barChart?.dispose()
  pieChart?.dispose()
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})

function handleChartResize() {
  if (resizeFrame) {
    cancelAnimationFrame(resizeFrame)
  }
  resizeFrame = requestAnimationFrame(() => {
    barChart?.resize()
    pieChart?.resize()
  })
}

function handleFileChange(event) {
  const file = event.target.files[0]
  setSelectedFile(file)
  event.target.value = ''
}

function setSelectedFile(file) {
  if (!file) return
  if (!file.type.startsWith('image/')) {
    errorMessage.value = '请上传 jpg、png 等图片文件'
    return
  }

  selectedFile.value = file
  result.value = null
  errorMessage.value = ''
  activeTab.value = 'overview'

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  previewUrl.value = URL.createObjectURL(file)
}

function handleDragEnter() {
  dragDepth.value += 1
  isDraggingFile.value = true
}

function handleDragOver() {
  isDraggingFile.value = true
}

function handleDragLeave() {
  dragDepth.value = Math.max(0, dragDepth.value - 1)
  if (dragDepth.value === 0) {
    isDraggingFile.value = false
  }
}

function handleFileDrop(event) {
  dragDepth.value = 0
  isDraggingFile.value = false
  const file = event.dataTransfer?.files?.[0]
  setSelectedFile(file)
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
    formData.append('detection_mode', detectionMode.value)

    const response = await axios.post(`${backendBaseUrl}/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${authToken.value}`
      }
    })

    result.value = response.data
    prependDetectionLogFromResult(response.data)
    await switchMainPage('results')
    activeTab.value = 'overview'
  } catch (error) {
    console.error(error)
    if (error.response?.status === 401) {
      clearAuth()
      errorMessage.value = '登录已过期，请重新登录'
    } else {
      errorMessage.value = error.response?.data?.detail || '检测失败，请确认后端服务是否正在运行，地址是否为 http://127.0.0.1:8000'
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
  detectionLogs.value = []
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_user')
}

async function switchMainPage(pageKey) {
  activePage.value = pageKey
  if (pageKey === 'logs') {
    await fetchDetectionLogs()
  }
  if (pageKey === 'results' && activeTab.value === 'charts') {
    await nextTick()
    renderCharts()
  }
}

async function goBack() {
  if (activePage.value === 'results') {
    await switchMainPage('upload')
    return
  }
  await switchMainPage('home')
}

async function goHome() {
  await switchMainPage('home')
}

async function switchTab(tabKey) {
  activeTab.value = tabKey
  if (tabKey === 'charts') {
    await nextTick()
    renderCharts()
  }
}

async function fetchDetectionLogs() {
  logsLoading.value = true
  logsError.value = ''

  try {
    const response = await axios.get(`${backendBaseUrl}/logs`, {
      headers: {
        Authorization: `Bearer ${authToken.value}`
      }
    })
    detectionLogs.value = response.data.logs || []
  } catch (error) {
    console.error(error)
    if (error.response?.status === 401) {
      clearAuth()
      logsError.value = '登录已过期，请重新登录'
    } else {
      logsError.value = error.response?.data?.detail || '检测日志加载失败，请确认后端服务是否正在运行'
    }
  } finally {
    logsLoading.value = false
  }
}

function prependDetectionLogFromResult(data) {
  if (!data?.log_id) return

  const log = {
    id: data.log_id,
    user_id: currentUser.value?.id,
    username: currentUser.value?.username,
    image_id: data.image_id,
    original_filename: data.original_filename,
    detection_mode: data.detection_mode,
    detection_mode_label: data.detection_mode_label,
    models_used: data.models_used || [],
    total_count: data.total_count,
    risk_level: data.analysis?.risk_level || '正常',
    risk_score: data.analysis?.risk_score ?? 0,
    scene_type: data.analysis?.scene_type || '未识别到明确巡检场景',
    class_count: data.class_count || {},
    report: data.report || '',
    result_image_url: data.result_image_url,
    result_json_url: data.result_json_url,
    created_at: new Date().toISOString()
  }

  detectionLogs.value = [
    log,
    ...detectionLogs.value.filter(item => item.id !== log.id)
  ]
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

async function imageUrlToDataUrl(url) {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`图片读取失败：${response.status}`)
  }
  const blob = await response.blob()

  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

async function fileToDataUrl(file) {
  if (!file) return ''

  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

function safeFileName(value) {
  return String(value || 'inspection-result')
    .replace(/\.[^.]+$/, '')
    .replace(/[\\/:*?"<>|]/g, '-')
    .replace(/\s+/g, '-')
    .slice(0, 80)
}

function downloadBlob(blob, fileName) {
  const link = document.createElement('a')
  const objectUrl = URL.createObjectURL(blob)
  link.href = objectUrl
  link.download = fileName
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  window.setTimeout(() => {
    URL.revokeObjectURL(objectUrl)
  }, 30000)
}

async function exportInspectionDocument() {
  if (!result.value) {
    exportError.value = '暂无检测结果，无法导出巡检文档'
    return
  }

  exportLoading.value = true
  exportError.value = ''
  exportMessage.value = ''

  let originalImageDataUrl = ''
  let resultImageDataUrl = ''
  try {
    if (selectedFile.value) {
      originalImageDataUrl = await fileToDataUrl(selectedFile.value)
    }
    if (result.value.result_image_url) {
      resultImageDataUrl = await imageUrlToDataUrl(`${backendBaseUrl}${result.value.result_image_url}`)
    }
  } catch (error) {
    console.error(error)
  }

  try {
    const currentAnalysis = analysis.value
    const generatedAt = new Date().toLocaleString('zh-CN', { hour12: false })
    const classRows = Object.entries(result.value.class_count || {})
      .map(([name, count]) => `<tr><td>${escapeHtml(name)}</td><td>${count}</td></tr>`)
      .join('')
    const detectionRows = (result.value.detections || [])
      .map((item, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(item.class_name)}</td>
          <td>${escapeHtml(modelRoleLabel(item.model_role))}</td>
          <td>${escapeHtml(formatConfidence(item.confidence))}</td>
          <td>${escapeHtml(item.area)}</td>
        </tr>
      `)
      .join('')
    const moduleRows = (currentAnalysis?.modules || [])
      .map(module => `
        <tr>
          <td>${escapeHtml(module.title)}</td>
          <td>${escapeHtml(module.status)}</td>
          <td>${escapeHtml(module.score)}</td>
          <td>${escapeHtml(module.reason)}</td>
          <td>${escapeHtml(module.suggestion)}</td>
        </tr>
      `)
      .join('')
    const actionItems = followUpActions.value
      .map(action => `<li>${escapeHtml(action)}</li>`)
      .join('')
    const sceneTags = (currentAnalysis?.scene_tags || [])
      .map(tag => `<span class="tag">${escapeHtml(tag)}</span>`)
      .join('')

    const html = `
      <!doctype html>
      <html>
        <head>
          <meta charset="utf-8">
          <title>无人机航拍图像巡检分析报告</title>
          <style>
            body { font-family: "Microsoft YaHei", Arial, sans-serif; color: #111827; line-height: 1.7; }
            h1 { margin: 0 0 10px; font-size: 26px; }
            h2 { margin: 24px 0 10px; font-size: 18px; border-bottom: 1px solid #d1d5db; padding-bottom: 6px; }
            h3 { margin: 16px 0 8px; font-size: 15px; }
            .meta { color: #4b5563; margin: 4px 0; }
            .summary { padding: 12px; background: #f8fafc; border-left: 4px solid #2563eb; }
            .risk { display: inline-block; padding: 2px 8px; border-radius: 12px; background: #eff6ff; color: #1d4ed8; font-weight: 700; }
            .tag { display: inline-block; margin: 0 6px 6px 0; padding: 3px 8px; border: 1px solid #c7d2fe; border-radius: 12px; color: #3730a3; background: #eef2ff; font-size: 12px; }
            table { width: 100%; border-collapse: collapse; margin: 8px 0 16px; font-size: 13px; }
            th, td { border: 1px solid #d1d5db; padding: 8px; vertical-align: top; text-align: left; }
            th { background: #f3f4f6; }
            img { max-width: 100%; margin: 8px 0 14px; border: 1px solid #d1d5db; }
            .image-grid { display: table; width: 100%; table-layout: fixed; }
            .image-cell { display: table-cell; width: 50%; padding-right: 12px; vertical-align: top; }
          </style>
        </head>
        <body>
          <h1>无人机航拍图像巡检分析报告</h1>
          <p class="meta">生成时间：${escapeHtml(generatedAt)}</p>
          <p class="meta">图片名称：${escapeHtml(result.value.original_filename)}</p>
          <p class="meta">检测模式：${escapeHtml(result.value.detection_mode_label || selectedDetectionMode.value.label)}</p>
          <p class="meta">启用模型：${escapeHtml(formatModelsUsed(result.value.models_used || [])) || '未记录'}</p>

          <h2>一、检测摘要</h2>
          <p>检测目标总数：${escapeHtml(result.value.total_count)}</p>
          <p>场景类型：${escapeHtml(currentAnalysis?.scene_type || '未识别到明确巡检场景')}</p>
          <p>综合风险：<span class="risk">${escapeHtml(currentAnalysis?.risk_level || '未评估')}</span></p>
          <p>风险评分：${escapeHtml(currentAnalysis?.risk_score ?? '--')}</p>
          ${sceneTags ? `<p>${sceneTags}</p>` : ''}
          <div class="summary">${escapeHtml(result.value.report || currentAnalysis?.summary || '暂无自动分析报告')}</div>

          <h2>二、图片对比</h2>
          <div class="image-grid">
            <div class="image-cell">
              <h3>原始图片</h3>
              ${originalImageDataUrl ? `<img src="${originalImageDataUrl}" alt="原始图片">` : '<p>当前会话没有可导出的原始图片预览。</p>'}
            </div>
            <div class="image-cell">
              <h3>检测结果图</h3>
              ${resultImageDataUrl ? `<img src="${resultImageDataUrl}" alt="检测结果图">` : '<p>检测结果图导出失败，请在系统中查看。</p>'}
            </div>
          </div>

          <h2>三、类别数量统计</h2>
          <table>
            <thead><tr><th>类别</th><th>数量</th></tr></thead>
            <tbody>${classRows || '<tr><td colspan="2">暂无检测目标</td></tr>'}</tbody>
          </table>

          <h2>四、异常模块分析</h2>
          <table>
            <thead>
              <tr><th>模块</th><th>状态</th><th>评分</th><th>原因</th><th>建议</th></tr>
            </thead>
            <tbody>${moduleRows || '<tr><td colspan="5">暂无异常模块分析</td></tr>'}</tbody>
          </table>

          <h2>五、目标明细</h2>
          <table>
            <thead><tr><th>序号</th><th>类别</th><th>模型来源</th><th>置信度</th><th>面积</th></tr></thead>
            <tbody>${detectionRows || '<tr><td colspan="5">暂无检测目标</td></tr>'}</tbody>
          </table>

          <h2>六、综合巡检建议</h2>
          <p>${escapeHtml(overallRecommendation.value || '暂无综合巡检建议')}</p>
          <h3>后续操作</h3>
          <ol>${actionItems || '<li>保存检测结果，作为本次巡检记录。</li>'}</ol>
        </body>
      </html>
    `

    const blob = new Blob(['\ufeff', html], { type: 'application/msword;charset=utf-8' })
    downloadBlob(blob, `${safeFileName(result.value.original_filename)}-巡检分析报告.doc`)
    exportMessage.value = '巡检文档已开始下载，请在浏览器下载记录中查看。'
  } catch (error) {
    console.error(error)
    exportError.value = '巡检文档导出失败，请稍后重试'
  } finally {
    exportLoading.value = false
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

function openImageDetail(type) {
  imageDetailType.value = type
  imageDetailOpen.value = true
}

function closeImageDetail() {
  imageDetailOpen.value = false
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

function modelRoleLabel(role) {
  if (role === 'scene') return '粗粒度场景模型'
  if (role === 'fine_target') return '细粒度目标模型'
  return '未知模型'
}

function formatModelsUsed(models) {
  const labels = {
    scene: '粗粒度场景模型',
    visdrone: '细粒度 VisDrone 模型'
  }
  return models.map(model => labels[model] || model).join('、')
}

function formatConfidence(confidence) {
  return `${(Number(confidence) * 100).toFixed(1)}%`
}

function formatDateTime(value) {
  if (!value) return '--'
  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(45, 212, 191, 0.16), transparent 34rem),
    linear-gradient(180deg, #edf3f8 0%, #f8fafc 48%, #eef3f8 100%);
  color: #172033;
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
  padding: 34px 24px 24px;
  text-align: center;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(30, 64, 175, 0.9)),
    url('/src/assets/hero.png') center / cover no-repeat;
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
  margin: 8px 0 0;
  color: #ffffff;
  font-size: clamp(24px, 3vw, 34px);
  font-weight: 700;
}

.system-name {
  margin: 0;
  color: #b8f3e6;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.main-nav {
  width: min(620px, 100%);
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin: 22px auto 0;
  padding: 6px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.34);
  backdrop-filter: blur(10px);
}

.main-nav button {
  min-width: 0;
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 8px 10px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: #dbeafe;
  font-size: 13px;
  font-weight: 800;
}

.main-nav button span {
  display: inline-grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 13px;
  line-height: 1;
}

.main-nav button.active {
  background: #ffffff;
  color: #1e3a8a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.2);
}

.main-nav button:disabled {
  background: transparent;
  color: rgba(219, 234, 254, 0.48);
  cursor: not-allowed;
}

.page-actions {
  position: absolute;
  left: 24px;
  top: 24px;
  display: flex;
  gap: 8px;
}

.page-actions button {
  min-width: 70px;
  padding: 8px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
}

.page-actions button:hover,
.user-bar button:hover {
  background: rgba(255, 255, 255, 0.24);
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
  align-items: center;
  gap: 32px;
  padding: 34px;
  overflow: hidden;
  border-radius: 8px;
  background:
    linear-gradient(90deg, rgba(15, 23, 42, 0.84), rgba(19, 78, 74, 0.28)),
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

.welcome-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 12px;
}

.secondary-button {
  border: 1px solid rgba(255, 255, 255, 0.32);
  background: rgba(255, 255, 255, 0.14);
  color: #ffffff;
}

.console-preview {
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 310px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.72);
  backdrop-filter: blur(10px);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.status-grid article {
  min-width: 0;
  display: grid;
  gap: 8px;
  padding: 18px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
  text-align: left;
}

.status-grid span {
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.status-grid strong {
  min-height: 32px;
  color: #0f172a;
  font-size: 24px;
  line-height: 1.15;
  word-break: break-word;
}

.status-grid small {
  overflow: hidden;
  color: #64748b;
  font-size: 12px;
  line-height: 1.55;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-grid .stat-success,
.status-grid .risk-normal {
  color: #047857;
}

.status-grid .stat-warning,
.status-grid .risk-medium {
  color: #c2410c;
}

.status-grid .stat-info,
.status-grid .risk-low {
  color: #1d4ed8;
}

.status-grid .risk-high {
  color: #b91c1c;
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

.console-main .console-risk-value {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 18px;
  line-height: 1;
}

.console-main .risk-pending {
  background: rgba(148, 163, 184, 0.18);
  color: #e2e8f0;
}

.console-main .risk-normal {
  background: rgba(52, 211, 153, 0.16);
  color: #86efac;
}

.console-main .risk-low {
  background: rgba(96, 165, 250, 0.16);
  color: #93c5fd;
}

.console-main .risk-medium {
  background: rgba(251, 191, 36, 0.18);
  color: #fde68a;
}

.console-main .risk-high {
  background: rgba(248, 113, 113, 0.18);
  color: #fecaca;
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

.console-list p span.risk-high {
  background: #f87171;
}

.console-list p span.risk-medium {
  background: #fbbf24;
}

.console-list p span.risk-low {
  background: #38bdf8;
}

.console-list p span.risk-normal {
  background: #34d399;
}

.workflow-card {
  padding: 24px;
  border-radius: 8px;
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
  border: 1px solid #e5edf5;
  border-radius: 8px;
  padding: 22px;
  margin-bottom: 22px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.card h2 {
  margin: 0 0 18px;
  color: #111827;
  font-size: 21px;
  font-weight: 800;
}

.result-shell {
  margin-top: 22px;
}

.result-toolbar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 18px;
  padding: 10px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}

.page-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
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

.export-button {
  flex: 0 0 auto;
  min-height: 40px;
  border-radius: 6px;
  background: #047857;
  font-weight: 700;
}

.export-button:hover {
  background: #065f46;
}

.export-status {
  margin: -6px 0 14px;
  text-align: right;
  font-size: 13px;
}

.tab-stack {
  display: block;
}

.dropzone {
  display: grid;
  place-items: center;
  min-height: 190px;
  border: 2px dashed #bfdbfe;
  border-radius: 8px;
  background: #f8fbff;
  text-align: center;
  transition:
    border-color 0.2s,
    box-shadow 0.2s,
    background 0.2s,
    transform 0.2s;
}

.dropzone.dragging {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.16);
  transform: translateY(-1px);
}

.dropzone.ready {
  border-color: #60a5fa;
  background: #ffffff;
}

.dropzone-picker {
  position: relative;
  width: 100%;
  min-height: 190px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  padding: 28px;
  color: #1e3a8a;
  cursor: pointer;
}

.dropzone-icon {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 30px;
  font-weight: 400;
  line-height: 1;
}

.dropzone-picker strong {
  max-width: min(560px, 100%);
  overflow: hidden;
  color: #111827;
  font-size: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropzone-picker small {
  color: #64748b;
  font-size: 13px;
}

.dropzone-picker input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
  cursor: pointer;
}

.upload-actions {
  margin-top: 16px;
  text-align: center;
}

.mode-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 18px;
  padding: 14px 16px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #f8fafc;
  text-align: left;
}

.mode-copy {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.mode-copy span {
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.mode-copy strong {
  color: #111827;
  font-size: 16px;
}

.mode-copy small {
  max-width: 760px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.mode-selector {
  flex: 0 0 auto;
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border: 1px solid #dbe4f0;
  border-radius: 999px;
  background: #ffffff;
}

.mode-selector label {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 78px;
  padding: 8px 12px;
  border-radius: 999px;
  cursor: pointer;
  transition:
    color 0.2s,
    background 0.2s;
}

.mode-selector label.active {
  background: #2563eb;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.18);
}

.mode-selector input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.mode-selector span {
  color: #475569;
  font-size: 13px;
  font-weight: 800;
}

.mode-selector label.active span {
  color: #ffffff;
}

button {
  border: none;
  background: #2563eb;
  color: white;
  padding: 10px 18px;
  border-radius: 8px;
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
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.compare-panel {
  margin-bottom: 24px;
  text-align: left;
}

.compare-panel h3 {
  margin: 0 0 12px;
  color: #111827;
  font-size: 17px;
  font-weight: 800;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.compare-grid div {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.compare-grid span {
  color: #475569;
  font-size: 13px;
  font-weight: 800;
}

.image-detail-trigger {
  position: relative;
  display: block;
  width: 100%;
  overflow: hidden;
  padding: 0;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #f8fafc;
  cursor: zoom-in;
  text-align: left;
}

.image-detail-trigger img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: contain;
  display: block;
  border: 0;
  border-radius: 0;
}

.image-detail-trigger:hover,
.image-detail-trigger:focus-visible {
  border-color: #2563eb;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.16);
  outline: none;
}

.image-detail-trigger .image-detail-badge {
  position: absolute;
  right: 12px;
  bottom: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.78);
  color: #ffffff;
  font-size: 12px;
  font-weight: 800;
}

.image-panel-trigger {
  border-color: #e5e7eb;
  border-radius: 8px;
}

.compare-empty {
  min-height: 220px;
  display: grid;
  place-items: center;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
}

.result-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

.summary-panel p {
  margin: 10px 0;
}

.image-panel h3,
.summary-panel h3,
.preview h3 {
  color: #111827;
  font-weight: 800;
}

.report {
  background: #f3f4f6;
  border-left: 4px solid #2563eb;
  padding: 14px;
  border-radius: 8px;
  line-height: 1.8;
}

.log-card {
  text-align: left;
}

.log-list {
  display: grid;
  gap: 14px;
}

.log-item {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #ffffff;
}

.log-main {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.log-main img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;
}

.log-main h3 {
  margin: 0 0 6px;
  color: #111827;
  font-size: 17px;
}

.log-main p {
  margin: 5px 0;
  color: #475569;
  line-height: 1.6;
}

.log-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.log-tags span:not(.risk-badge) {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #eef2f7;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.log-report {
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  line-height: 1.7;
}

.log-empty {
  display: grid;
  place-items: center;
  gap: 10px;
  min-height: 260px;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
  text-align: center;
}

.log-empty h3,
.log-empty p {
  margin: 0;
}

.image-detail-modal {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.72);
}

.image-detail-dialog {
  width: min(1320px, 100%);
  max-height: min(860px, calc(100vh - 48px));
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  overflow: hidden;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.36);
}

.image-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-bottom: 1px solid #e5e7eb;
}

.image-detail-header span {
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
}

.image-detail-header h2 {
  margin: 2px 0 0;
  color: #111827;
  font-size: 20px;
}

.image-detail-close {
  width: 38px;
  height: 38px;
  padding: 0;
  border-radius: 999px;
  background: #eef2f7;
  color: #0f172a;
  font-size: 26px;
  line-height: 1;
}

.image-detail-body {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
}

.image-detail-viewer {
  min-height: 0;
  display: grid;
  place-items: center;
  overflow: auto;
  padding: 18px;
  background: #0f172a;
}

.image-detail-viewer img {
  max-width: 100%;
  max-height: 76vh;
  object-fit: contain;
  border-radius: 6px;
}

.image-detail-info {
  min-height: 0;
  overflow: auto;
  padding: 18px;
  border-left: 1px solid #e5e7eb;
  background: #f8fafc;
}

.image-detail-info h3 {
  margin: 0 0 10px;
  color: #111827;
  font-size: 15px;
}

.image-detail-info p {
  margin: 8px 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
}

.detail-detection-list {
  margin-top: 16px;
}

.detail-detection-list ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.detail-detection-list li {
  display: grid;
  gap: 3px;
  padding: 10px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #ffffff;
}

.detail-detection-list strong {
  color: #111827;
  font-size: 14px;
}

.detail-detection-list span,
.detail-detection-list small {
  color: #64748b;
  font-size: 12px;
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

.success {
  color: #047857;
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
  .compare-grid,
  .log-main,
  .grid,
  .module-grid,
  .metric-grid,
  .recommendation-grid,
  .feature-grid,
  .status-grid,
  .workflow-steps {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .header {
    padding: 78px 16px 20px;
  }

  .page-actions {
    left: 18px;
    top: 18px;
  }

  .mode-panel {
    align-items: stretch;
    flex-direction: column;
  }

  .image-detail-modal {
    padding: 12px;
  }

  .image-detail-dialog {
    max-height: calc(100vh - 24px);
  }

  .image-detail-body {
    grid-template-columns: 1fr;
  }

  .image-detail-viewer img {
    max-height: 58vh;
  }

  .image-detail-info {
    max-height: 260px;
    border-top: 1px solid #e5e7eb;
    border-left: 0;
  }

  .mode-selector {
    width: 100%;
  }

  .mode-selector label {
    flex: 1;
    min-width: 0;
  }

  .dropzone,
  .dropzone-picker {
    min-height: 160px;
  }

  .dropzone-picker strong {
    max-width: 260px;
    font-size: 16px;
  }

  .result-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .export-button {
    width: 100%;
  }

  .welcome-band {
    grid-template-columns: 1fr;
    min-height: 300px;
    padding: 24px;
  }

  .main-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .main-nav button {
    min-height: 40px;
  }

  .status-grid small {
    white-space: normal;
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
