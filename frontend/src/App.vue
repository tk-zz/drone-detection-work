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
          <div class="cvat-showcase" aria-label="动态检测工作台预览">
            <div class="showcase-topbar">
              <div>
                <strong>UAV Review Studio</strong>
                <span>{{ result ? 'Result synced' : 'Live preview' }}</span>
              </div>
              <small>{{ result ? consoleRiskLevel : 'Ready' }}</small>
            </div>

            <div class="showcase-workspace">
              <aside class="showcase-queue">
                <span>Queue</span>
                <button class="active" type="button">
                  <strong>巡检图像 01</strong>
                  <small>{{ result ? `${consoleTargetCount} targets` : 'pending' }}</small>
                </button>
                <button type="button">
                  <strong>巡检图像 02</strong>
                  <small>road scan</small>
                </button>
                <button type="button">
                  <strong>巡检图像 03</strong>
                  <small>water risk</small>
                </button>
              </aside>

              <div class="showcase-canvas">
                <img src="/src/assets/hero.png" alt="航拍检测工作台预览" />
                <span class="scan-line"></span>
                <span class="detect-box detect-box-car"><em>vehicle 0.91</em></span>
                <span class="detect-box detect-box-road"><em>road 0.87</em></span>
                <span class="detect-box detect-box-water"><em>water 0.76</em></span>
              </div>

              <aside class="showcase-panel">
                <span>Analysis</span>
                <div>
                  <small>Targets</small>
                  <strong>{{ consoleTargetCount }}</strong>
                </div>
                <div>
                  <small>Risk modules</small>
                  <strong>{{ consoleAbnormalCount }}</strong>
                </div>
                <div class="showcase-meter">
                  <i></i>
                </div>
              </aside>
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
          :class="['dropzone', { dragging: isDraggingFile, ready: selectedFiles.length }]"
          @dragenter.prevent="handleDragEnter"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleFileDrop"
        >
          <label class="dropzone-picker">
            <input type="file" accept="image/*" multiple @change="handleFileChange" />
            <span class="dropzone-icon">+</span>
            <strong>{{ selectedFileLabel }}</strong>
            <small>
              {{ selectedFiles.length ? '已选择图片，可重新拖入或点击更换整批文件' : '支持 jpg、png 等常见图片格式，也可以点击选择多张图片' }}
            </small>
          </label>
        </div>

        <div v-if="selectedFiles.length" class="selected-file-list" aria-label="已选择图片列表">
          <div class="batch-summary">
            <strong>已选择 {{ selectedFiles.length }} 张图片</strong>
            <span v-if="batchProgress.total">
              已完成 {{ batchProgress.completed }}/{{ batchProgress.total }}
              <template v-if="batchProgress.failed">，失败 {{ batchProgress.failed }}</template>
            </span>
          </div>
          <ul>
            <li
              v-for="(file, index) in selectedFiles"
              :key="`${file.name}-${file.size}-${file.lastModified}`"
              :class="{ active: activePreviewIndex === index }"
            >
              <button type="button" @click="setActivePreview(index)">
                <span>{{ file.name }}</span>
                <small>{{ formatFileSize(file.size) }}</small>
              </button>
            </li>
          </ul>
          <p v-if="batchProgress.currentName" class="batch-current">正在检测：{{ batchProgress.currentName }}</p>
        </div>

        <div class="upload-actions">
          <button :disabled="!selectedFiles.length || loading" @click="detectImage">
            {{ uploadActionLabel }}
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

        <div v-if="currentPreview" class="preview">
          <div class="preview-header">
            <div>
              <h3>原始图片预览</h3>
              <p>{{ currentPreview.file.name }}（{{ activePreviewIndex + 1 }}/{{ selectedImagePreviews.length }}）</p>
            </div>
            <div v-if="selectedImagePreviews.length > 1" class="pager-controls">
              <button type="button" @click="showPreviousPreview">上一张</button>
              <button type="button" @click="showNextPreview">下一张</button>
            </div>
          </div>
          <div
            class="preview-carousel"
            @mousedown="startPreviewSwipe"
            @mousemove="movePreviewSwipe"
            @mouseup="endPreviewSwipe"
            @mouseleave="cancelPreviewSwipe"
            @touchstart.passive="startPreviewSwipe"
            @touchmove.passive="movePreviewSwipe"
            @touchend="endPreviewSwipe"
            @touchcancel="cancelPreviewSwipe"
          >
            <button
              v-if="selectedImagePreviews.length > 1"
              class="preview-arrow preview-arrow-left"
              type="button"
              aria-label="查看上一张原始图片"
              @click.stop="showPreviousPreview"
            >
              ‹
            </button>
            <img :src="currentPreview.url" alt="原始图片" draggable="false" />
            <button
              v-if="selectedImagePreviews.length > 1"
              class="preview-arrow preview-arrow-right"
              type="button"
              aria-label="查看下一张原始图片"
              @click.stop="showNextPreview"
            >
              ›
            </button>
          </div>
          <div v-if="selectedImagePreviews.length > 1" class="preview-strip" aria-label="原始图片缩略图列表">
            <button
              v-for="(item, index) in selectedImagePreviews"
              :key="`${item.file.name}-${item.file.size}-${item.file.lastModified}`"
              :class="{ active: activePreviewIndex === index }"
              type="button"
              @click="setActivePreview(index)"
            >
              <img :src="item.url" :alt="item.file.name" />
              <span>{{ index + 1 }}</span>
            </button>
          </div>
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

        <section v-if="batchResults.length > 1" class="card batch-results-card">
          <div class="section-heading">
            <div>
              <h2>批量检测结果</h2>
              <p>共完成 {{ batchResults.length }} 张图片检测，当前查看第 {{ activeResultIndex + 1 }} 张。</p>
            </div>
            <div class="pager-controls">
              <button type="button" @click="showPreviousResult">上一张</button>
              <button type="button" @click="showNextResult">下一张</button>
            </div>
          </div>
          <div class="batch-result-list" aria-label="批量检测结果列表">
            <button
              v-for="(item, index) in batchResults"
              :key="`${item.result.image_id}-${index}`"
              :class="{ active: activeResultIndex === index }"
              type="button"
              @click="selectBatchResult(index)"
            >
              <span>{{ index + 1 }}</span>
              <strong>{{ item.result.original_filename }}</strong>
              <small>{{ item.result.total_count }} 个目标 · {{ item.result.analysis?.risk_level || '待分析' }}</small>
            </button>
          </div>
        </section>

        <section v-if="activeTab === 'overview'" class="card result-card">
          <h2>检测总览</h2>

          <section v-if="batchOverviewItems.length > 1" class="batch-overview-panel">
            <div class="section-heading">
              <div>
                <h3>批量图片检测概览</h3>
                <p>每张图片的原图、检测结果和摘要如下，点击卡片可切换下方详情。</p>
              </div>
            </div>
            <div class="batch-overview-grid">
              <article
                v-for="(item, index) in batchOverviewItems"
                :key="`${item.result.image_id}-${index}`"
                :class="{ active: activeResultIndex === index }"
              >
                <button type="button" @click="selectBatchResult(index)">
                  <div class="batch-image-pair">
                    <div>
                      <span>原图</span>
                      <img :src="item.preview?.url" :alt="`${item.result.original_filename} 原图`" />
                    </div>
                    <div>
                      <span>检测图</span>
                      <img :src="backendBaseUrl + item.result.result_image_url" :alt="`${item.result.original_filename} 检测结果`" />
                    </div>
                  </div>
                  <div class="batch-card-copy">
                    <strong>{{ item.result.original_filename }}</strong>
                    <small>{{ item.result.total_count }} 个目标 · {{ item.result.analysis?.risk_level || '待分析' }}</small>
                    <small>{{ item.result.analysis?.scene_type || '未识别到明确巡检场景' }}</small>
                  </div>
                </button>
              </article>
            </div>
          </section>

          <section class="compare-panel">
            <h3>原始图片与检测结果对比</h3>
            <div class="compare-grid">
              <div>
                <span>原始图片</span>
                <button
                  v-if="currentPreview"
                  class="image-detail-trigger"
                  type="button"
                  @click="openImageDetail('original')"
                >
                  <img :src="currentPreview.url" alt="原始图片" />
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

const selectedFiles = ref([])
const selectedImagePreviews = ref([])
const activePreviewIndex = ref(0)
const selectedFile = ref(null)
const previewUrl = ref('')
const result = ref(null)
const batchResults = ref([])
const activeResultIndex = ref(0)
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
const batchProgress = ref({
  total: 0,
  completed: 0,
  failed: 0,
  currentName: ''
})
const loginForm = ref({
  username: 'admin',
  password: 'admin123'
})

const barChartRef = ref(null)
const pieChartRef = ref(null)

const analysis = computed(() => result.value?.analysis || null)
const currentPreview = computed(() => selectedImagePreviews.value[activePreviewIndex.value] || null)
const batchOverviewItems = computed(() => {
  return batchResults.value.map(item => ({
    ...item,
    preview: selectedImagePreviews.value[item.fileIndex] || null
  }))
})
const imageDetailTitle = computed(() => {
  return imageDetailType.value === 'original' ? '原始图片' : '检测结果图'
})
const imageDetailSrc = computed(() => {
  if (imageDetailType.value === 'original') return currentPreview.value?.url || ''
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
const selectedFileLabel = computed(() => {
  if (!selectedFiles.value.length) return '拖拽航拍图片到这里'
  if (selectedFiles.value.length === 1) return selectedFiles.value[0].name
  return `已选择 ${selectedFiles.value.length} 张航拍图片`
})
const uploadActionLabel = computed(() => {
  if (!loading.value) {
    return selectedFiles.value.length > 1 ? '开始批量智能识别' : '开始智能识别'
  }

  if (batchProgress.value.total > 1) {
    return `检测中 ${batchProgress.value.completed}/${batchProgress.value.total}`
  }

  return '检测中...'
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
    value: result.value ? '已完成' : selectedFiles.value.length ? '待检测' : '未开始',
    hint: selectedFiles.value.length ? selectedFileLabel.value : '上传一张或多张航拍图像开始分析',
    className: result.value ? 'stat-success' : selectedFiles.value.length ? 'stat-warning' : ''
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
let previewSwipeStartX = 0
let previewSwipeCurrentX = 0
let previewSwipeActive = false

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
  revokePreviewUrls()
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
  setSelectedFiles(event.target.files)
  event.target.value = ''
}

function setSelectedFiles(fileList) {
  const files = Array.from(fileList || [])
  if (!files.length) return

  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  if (!imageFiles.length) {
    errorMessage.value = '请上传 jpg、png 等图片文件'
    return
  }

  selectedFiles.value = imageFiles
  revokePreviewUrls()
  selectedImagePreviews.value = imageFiles.map(file => ({
    file,
    url: URL.createObjectURL(file)
  }))
  activePreviewIndex.value = 0
  selectedFile.value = imageFiles[0]
  previewUrl.value = selectedImagePreviews.value[0]?.url || ''
  batchResults.value = []
  activeResultIndex.value = 0
  result.value = null
  errorMessage.value = ''
  activeTab.value = 'overview'
  batchProgress.value = {
    total: 0,
    completed: 0,
    failed: 0,
    currentName: ''
  }
  if (imageFiles.length < files.length) {
    errorMessage.value = `已忽略 ${files.length - imageFiles.length} 个非图片文件`
  }
}

function revokePreviewUrls() {
  selectedImagePreviews.value.forEach(item => URL.revokeObjectURL(item.url))
  selectedImagePreviews.value = []
  previewUrl.value = ''
}

function setActivePreview(index) {
  if (!selectedImagePreviews.value.length) return
  const nextIndex = (index + selectedImagePreviews.value.length) % selectedImagePreviews.value.length
  const nextPreview = selectedImagePreviews.value[nextIndex]
  activePreviewIndex.value = nextIndex
  selectedFile.value = nextPreview.file
  previewUrl.value = nextPreview.url
}

function showPreviousPreview() {
  setActivePreview(activePreviewIndex.value - 1)
}

function showNextPreview() {
  setActivePreview(activePreviewIndex.value + 1)
}

async function selectBatchResult(index) {
  if (!batchResults.value.length) return
  const nextIndex = (index + batchResults.value.length) % batchResults.value.length
  const item = batchResults.value[nextIndex]
  activeResultIndex.value = nextIndex
  result.value = item.result
  setActivePreview(item.fileIndex)

  if (activeTab.value === 'charts') {
    await nextTick()
    renderCharts()
  }
}

function showPreviousResult() {
  selectBatchResult(activeResultIndex.value - 1)
}

function showNextResult() {
  selectBatchResult(activeResultIndex.value + 1)
}

function getSwipeClientX(event) {
  return event.touches?.[0]?.clientX ?? event.changedTouches?.[0]?.clientX ?? event.clientX ?? 0
}

function startPreviewSwipe(event) {
  if (selectedImagePreviews.value.length < 2) return
  previewSwipeActive = true
  previewSwipeStartX = getSwipeClientX(event)
  previewSwipeCurrentX = previewSwipeStartX
}

function movePreviewSwipe(event) {
  if (!previewSwipeActive) return
  previewSwipeCurrentX = getSwipeClientX(event)
}

function endPreviewSwipe(event) {
  if (!previewSwipeActive) return
  previewSwipeCurrentX = getSwipeClientX(event)
  const deltaX = previewSwipeCurrentX - previewSwipeStartX
  previewSwipeActive = false

  if (Math.abs(deltaX) < 48) return
  if (deltaX > 0) {
    showPreviousPreview()
  } else {
    showNextPreview()
  }
}

function cancelPreviewSwipe() {
  previewSwipeActive = false
}

function formatFileSize(size) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
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
  setSelectedFiles(event.dataTransfer?.files)
}

async function detectImage() {
  if (!selectedFiles.value.length) {
    errorMessage.value = '请先选择一张或多张图片'
    return
  }

  loading.value = true
  errorMessage.value = ''
  result.value = null
  batchResults.value = []
  activeResultIndex.value = 0
  batchProgress.value = {
    total: selectedFiles.value.length,
    completed: 0,
    failed: 0,
    currentName: ''
  }

  try {
    let latestResult = null

    for (const [fileIndex, file] of selectedFiles.value.entries()) {
      batchProgress.value.currentName = file.name
      setActivePreview(fileIndex)

      const formData = new FormData()
      formData.append('file', file)
      formData.append('detection_mode', detectionMode.value)

      try {
        const response = await axios.post(`${backendBaseUrl}/detect`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${authToken.value}`
          }
        })

        latestResult = response.data
        result.value = response.data
        batchResults.value.push({
          fileIndex,
          result: response.data
        })
        activeResultIndex.value = batchResults.value.length - 1
        prependDetectionLogFromResult(response.data)
        batchProgress.value.completed += 1
      } catch (error) {
        console.error(error)
        if (error.response?.status === 401) {
          clearAuth()
          errorMessage.value = '登录已过期，请重新登录'
          return
        }
        batchProgress.value.failed += 1
      }
    }

    batchProgress.value.currentName = ''

    if (latestResult) {
      await selectBatchResult(batchResults.value.length - 1)
      await switchMainPage('results')
      activeTab.value = 'overview'
    }

    if (batchProgress.value.failed) {
      errorMessage.value = `批量检测完成，成功 ${batchProgress.value.completed} 张，失败 ${batchProgress.value.failed} 张`
    }
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
  min-height: 500px;
  display: grid;
  grid-template-columns: minmax(360px, 0.88fr) minmax(560px, 1.12fr);
  align-items: center;
  gap: 36px;
  padding: 42px;
  overflow: hidden;
  border-radius: 8px;
  background:
    linear-gradient(90deg, rgba(8, 15, 29, 0.9), rgba(15, 23, 42, 0.62)),
    url('/src/assets/hero.png') center / cover no-repeat;
  color: #ffffff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.18);
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
  width: 100%;
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

.cvat-showcase {
  align-self: stretch;
  min-height: 390px;
  display: grid;
  grid-template-rows: auto 1fr;
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.18);
  border-radius: 8px;
  background: #0b1220;
  box-shadow: 0 24px 54px rgba(2, 6, 23, 0.34);
}

.showcase-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  background: #111827;
}

.showcase-topbar div {
  display: grid;
  gap: 3px;
}

.showcase-topbar strong {
  color: #f8fafc;
  font-size: 15px;
}

.showcase-topbar span,
.showcase-topbar small {
  color: #93c5fd;
  font-size: 12px;
  font-weight: 800;
}

.showcase-topbar small {
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.18);
}

.showcase-workspace {
  min-height: 0;
  display: grid;
  grid-template-columns: 138px minmax(0, 1fr) 132px;
  background: #0f172a;
}

.showcase-queue,
.showcase-panel {
  min-width: 0;
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 14px;
  border-right: 1px solid rgba(148, 163, 184, 0.16);
  background: #111827;
}

.showcase-panel {
  border-right: 0;
  border-left: 1px solid rgba(148, 163, 184, 0.16);
}

.showcase-queue > span,
.showcase-panel > span {
  margin: 0;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.showcase-queue button {
  min-width: 0;
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(15, 23, 42, 0.9);
  color: #e2e8f0;
  text-align: left;
}

.showcase-queue button.active {
  border-color: rgba(96, 165, 250, 0.82);
  background: rgba(37, 99, 235, 0.18);
}

.showcase-queue strong,
.showcase-queue small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.showcase-queue strong {
  font-size: 12px;
}

.showcase-queue small {
  color: #94a3b8;
  font-size: 11px;
}

.showcase-canvas {
  position: relative;
  min-height: 320px;
  overflow: hidden;
  background: #020617;
}

.showcase-canvas img {
  width: 100%;
  height: 100%;
  min-height: 320px;
  display: block;
  object-fit: cover;
  opacity: 0.72;
  filter: saturate(0.9) contrast(1.06);
}

.showcase-canvas::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.06) 1px, transparent 1px);
  background-size: 34px 34px;
  pointer-events: none;
}

.scan-line {
  position: absolute;
  top: -20%;
  left: 0;
  z-index: 2;
  width: 100%;
  height: 80px;
  background: linear-gradient(180deg, transparent, rgba(56, 189, 248, 0.34), transparent);
  animation: scan-canvas 5.2s ease-in-out infinite;
}

.detect-box {
  position: absolute;
  z-index: 3;
  border: 2px solid #38bdf8;
  border-radius: 4px;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.65), 0 0 24px rgba(56, 189, 248, 0.18);
  animation: detect-pulse 2.8s ease-in-out infinite;
}

.detect-box em {
  position: absolute;
  left: -2px;
  top: -26px;
  padding: 4px 6px;
  border-radius: 4px;
  background: #0ea5e9;
  color: #ffffff;
  font-size: 11px;
  font-style: normal;
  font-weight: 800;
  white-space: nowrap;
}

.detect-box-car {
  left: 18%;
  top: 57%;
  width: 22%;
  height: 18%;
}

.detect-box-road {
  left: 46%;
  top: 42%;
  width: 30%;
  height: 16%;
  border-color: #22c55e;
  animation-delay: 0.7s;
}

.detect-box-road em {
  background: #16a34a;
}

.detect-box-water {
  left: 58%;
  top: 70%;
  width: 24%;
  height: 15%;
  border-color: #f59e0b;
  animation-delay: 1.2s;
}

.detect-box-water em {
  background: #d97706;
}

.showcase-panel div {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.92);
}

.showcase-panel small {
  color: #94a3b8;
  font-size: 11px;
  font-weight: 800;
}

.showcase-panel strong {
  color: #f8fafc;
  font-size: 24px;
}

.showcase-meter {
  height: 90px;
  align-items: end;
}

.showcase-meter i {
  display: block;
  width: 100%;
  height: 58%;
  border-radius: 6px;
  background: linear-gradient(180deg, #38bdf8, #2563eb);
  animation: meter-rise 4s ease-in-out infinite;
}

@keyframes scan-canvas {
  0%,
  18% {
    transform: translateY(0);
    opacity: 0;
  }

  28% {
    opacity: 1;
  }

  72% {
    opacity: 1;
  }

  100% {
    transform: translateY(520%);
    opacity: 0;
  }
}

@keyframes detect-pulse {
  0%,
  100% {
    opacity: 0.72;
    transform: scale(0.995);
  }

  45% {
    opacity: 1;
    transform: scale(1.015);
  }
}

@keyframes meter-rise {
  0%,
  100% {
    height: 42%;
  }

  50% {
    height: 74%;
  }
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

.selected-file-list {
  margin-top: 16px;
  padding: 14px 16px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #f8fafc;
  text-align: left;
}

.batch-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #111827;
}

.batch-summary strong {
  font-size: 15px;
}

.batch-summary span,
.batch-current {
  color: #2563eb;
  font-size: 13px;
  font-weight: 800;
}

.selected-file-list ul {
  max-height: 150px;
  overflow: auto;
  display: grid;
  gap: 8px;
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.selected-file-list li {
  min-width: 0;
}

.selected-file-list li button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: #ffffff;
  color: inherit;
  text-align: left;
}

.selected-file-list li.active button {
  border-color: #2563eb;
  background: #eff6ff;
}

.selected-file-list li span {
  min-width: 0;
  overflow: hidden;
  color: #334155;
  font-size: 13px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-file-list li small {
  flex: 0 0 auto;
  color: #64748b;
  font-size: 12px;
}

.batch-current {
  margin: 12px 0 0;
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

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  text-align: left;
}

.preview-header h3 {
  margin: 0;
}

.preview-header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.pager-controls {
  flex: 0 0 auto;
  display: inline-flex;
  gap: 8px;
}

.pager-controls button {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #1e3a8a;
  font-size: 13px;
  font-weight: 800;
}

.pager-controls button:hover {
  background: #eff6ff;
}

.preview-carousel img,
.image-panel img {
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.preview-carousel {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  background: #f8fafc;
  touch-action: pan-y;
  user-select: none;
}

.preview-carousel img {
  display: block;
  width: 100%;
  max-height: 520px;
  object-fit: contain;
}

.preview-arrow {
  position: absolute;
  top: 50%;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 42px;
  height: 54px;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.58);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.58);
  color: #ffffff;
  font-size: 34px;
  line-height: 1;
  transform: translateY(-50%);
}

.preview-arrow:hover {
  background: rgba(15, 23, 42, 0.78);
  transform: translateY(-50%);
}

.preview-arrow-left {
  left: 12px;
}

.preview-arrow-right {
  right: 12px;
}

.preview-strip {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.preview-strip button {
  position: relative;
  min-width: 0;
  overflow: hidden;
  padding: 0;
  border: 2px solid transparent;
  background: #ffffff;
}

.preview-strip button.active {
  border-color: #2563eb;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.14);
}

.preview-strip img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: none;
  border-radius: 6px;
}

.preview-strip span {
  position: absolute;
  left: 6px;
  top: 6px;
  display: grid;
  place-items: center;
  min-width: 24px;
  height: 24px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.78);
  color: #ffffff;
  font-size: 12px;
  font-weight: 900;
}

.batch-results-card {
  margin-bottom: 18px;
}

.batch-result-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.batch-result-list button {
  min-width: 0;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 4px 10px;
  padding: 12px;
  border: 1px solid #dbe4f0;
  background: #ffffff;
  color: #334155;
  text-align: left;
}

.batch-result-list button.active {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.12);
}

.batch-result-list span {
  grid-row: span 2;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 13px;
  font-weight: 900;
}

.batch-result-list strong,
.batch-result-list small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-result-list strong {
  color: #111827;
  font-size: 14px;
}

.batch-result-list small {
  color: #64748b;
  font-size: 12px;
}

.batch-overview-panel {
  margin: 18px 0 24px;
  text-align: left;
}

.batch-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.batch-overview-grid article {
  min-width: 0;
}

.batch-overview-grid article > button {
  width: 100%;
  min-width: 0;
  padding: 12px;
  border: 1px solid #dbe4f0;
  background: #ffffff;
  color: #334155;
  text-align: left;
}

.batch-overview-grid article.active > button {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12);
}

.batch-image-pair {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.batch-image-pair div {
  display: grid;
  gap: 6px;
}

.batch-image-pair span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.batch-image-pair img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #f8fafc;
}

.batch-card-copy {
  display: grid;
  gap: 4px;
  margin-top: 10px;
}

.batch-card-copy strong,
.batch-card-copy small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-card-copy strong {
  color: #111827;
  font-size: 14px;
}

.batch-card-copy small {
  color: #64748b;
  font-size: 12px;
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

  .cvat-showcase {
    min-height: 360px;
  }

  .showcase-workspace {
    grid-template-columns: 104px minmax(0, 1fr);
  }

  .showcase-panel {
    display: none;
  }

  .showcase-queue {
    padding: 10px;
  }

  .showcase-canvas,
  .showcase-canvas img {
    min-height: 280px;
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
