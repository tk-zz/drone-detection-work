<template>
  <div class="page">
    <section v-if="!authToken" class="login-page">
      <div class="login-panel">
        <div class="login-copy">
          <h1>无人机航拍场景异常检测与可视分析系统</h1>
          <p>登录后进入航拍检测、账号管理与管理员用户管理工作台。</p>
        </div>

        <div class="login-card">
          <div class="auth-tabs">
            <button
              type="button"
              :class="{ active: authMode === 'login' }"
              @click="switchAuthMode('login')"
            >登录</button>
            <button
              type="button"
              :class="{ active: authMode === 'register' }"
              @click="switchAuthMode('register')"
            >注册</button>
          </div>

          <form v-if="authMode === 'login'" @submit.prevent="login">
            <h2>系统登录</h2>
            <label>
              用户名
              <input v-model="loginForm.username" autocomplete="off" placeholder="请输入用户名" />
            </label>
            <label>
              密码
              <input v-model="loginForm.password" autocomplete="off" placeholder="请输入密码" type="password" />
            </label>
            <button :disabled="loginLoading" type="submit">
              {{ loginLoading ? '登录中...' : '登录' }}
            </button>
            <p v-if="loginError" class="error">{{ loginError }}</p>
            <p class="login-hint">忘记密码请联系系统管理员重置</p>
          </form>

          <form v-else @submit.prevent="register">
            <h2>注册账号</h2>
            <label>
              用户名
              <input v-model="registerForm.username" autocomplete="off" placeholder="至少 3 个字符" />
            </label>
            <label>
              密码
              <input v-model="registerForm.password" autocomplete="off" placeholder="至少 6 个字符" type="password" />
            </label>
            <label>
              确认密码
              <input v-model="registerForm.confirmPassword" autocomplete="off" placeholder="再次输入密码" type="password" />
            </label>
            <button :disabled="registerLoading" type="submit">
              {{ registerLoading ? '注册中...' : '注册' }}
            </button>
            <p v-if="registerError" class="error">{{ registerError }}</p>
            <p v-if="registerSuccess" class="success-message">{{ registerSuccess }}</p>
            <p class="login-hint">注册成功后即可使用新账号登录</p>
          </form>
        </div>
      </div>
    </section>

    <template v-else>
      <header class="header">
        <div class="user-bar">
          <div class="user-bar-copy">
            <span>当前用户：{{ currentUser?.username }} · {{ currentUser?.role_label || formatRole(currentUser?.role) }}</span>
          </div>
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
              <span class="welcome-eyebrow">UAV Inspection Analysis</span>
              <h2>
                <span>无人机航拍</span>
                <span>异常检测</span>
                <span>用户工作台</span>
              </h2>
              <p class="welcome-lead">
                系统支持普通用户和管理员两种角色，覆盖媒体检测、结果分析与后台管理全流程。
              </p>
              <div class="welcome-actions">
                <button class="hero-action primary-action" type="button" @click="switchMainPage('upload')">
                  <span class="action-label">开始上传媒体</span>
                  <span class="action-arrow">→</span>
                </button>
                <button class="hero-action secondary-button" type="button" @click="switchMainPage('account')">
                  <span class="action-label">查看账号信息</span>
                  <span class="action-arrow">→</span>
                </button>
              </div>
            </div>

            <div class="cvat-showcase" aria-label="用户与检测概览">
              <div class="showcase-topbar">
                <div>
                  <strong>Detection Console</strong>
                  <span>{{ currentUser?.role_label || formatRole(currentUser?.role) }}</span>
                </div>
                <small>{{ currentUser?.username }}</small>
              </div>

              <div class="showcase-workspace">
                <aside class="showcase-queue">
                  <span>Account</span>
                  <button class="active" type="button">
                    <strong>{{ currentUser?.username }}</strong>
                    <small>{{ currentUser?.role_label || formatRole(currentUser?.role) }}</small>
                  </button>
                  <button type="button">
                    <strong>检测模式</strong>
                    <small>{{ selectedDetectionMode.shortLabel }}</small>
                  </button>
                  <button type="button">
                    <strong>日志记录</strong>
                    <small>{{ detectionLogs.length || 0 }} 条</small>
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
                    <small>Detected</small>
                    <strong>{{ consoleTargetCount }}</strong>
                  </div>
                  <div>
                    <small>Risk modules</small>
                    <strong>{{ consoleAbnormalCount }}</strong>
                  </div>
                  <div>
                    <small>Risk level</small>
                    <strong>{{ consoleRiskLevel }}</strong>
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
              <p>支持普通用户检测分析、管理员后台治理，并将检测日志与用户账号关联起来。</p>
            </div>
            <div class="workflow-steps">
              <article>
                <span>01</span>
                <h3>登录并识别身份</h3>
                <p>系统根据普通用户或管理员身份返回对应的检测与管理权限。</p>
              </article>
              <article>
                <span>02</span>
                <h3>执行智能检测</h3>
                <p>上传图片或视频后执行检测，成功后自动记录检测日志。</p>
              </article>
              <article>
                <span>03</span>
                <h3>查看结果分析</h3>
                <p>查看风险等级、异常模块、统计图表和巡检建议。</p>
              </article>
              <article>
                <span>04</span>
                <h3>管理员治理</h3>
                <p>管理员可对用户执行增删改查，并查看全部检测日志。</p>
              </article>
            </div>
          </section>
        </section>

        <section v-if="activePage === 'account'" class="card account-card">
          <div class="section-heading">
            <div>
              <h2>账号信息</h2>
              <p>查看当前用户名、角色和账号状态。</p>
            </div>
            <button type="button" :disabled="accountLoading" @click="fetchCurrentUser">
              {{ accountLoading ? '刷新中...' : '刷新信息' }}
            </button>
          </div>

          <div v-if="currentUser" class="account-grid">
            <article class="account-panel">
              <span>用户名</span>
              <strong>{{ currentUser.username }}</strong>
              <small>当前登录账号</small>
            </article>
            <article class="account-panel">
              <span>当前角色</span>
              <strong>{{ currentUser.role_label || formatRole(currentUser.role) }}</strong>
              <small>{{ accountRoleDescription }}</small>
            </article>
            <article class="account-panel">
              <span>账号状态</span>
              <strong>{{ currentUser.is_active ? '启用' : '停用' }}</strong>
              <small>由管理员维护账号启用状态</small>
            </article>
            <article class="account-panel">
              <span>注册时间</span>
              <strong>{{ formatDateTime(currentUser.created_at) }}</strong>
              <small>最近更新：{{ formatDateTime(currentUser.updated_at) }}</small>
            </article>
          </div>

          <p v-if="accountError" class="error">{{ accountError }}</p>
          <p v-if="accountMessage" class="success-message">{{ accountMessage }}</p>

          <section class="account-section">
            <div class="section-heading">
              <div>
                <h3>修改密码</h3>
                <p>定期更换密码可以更好地保护账号安全，修改成功后需要重新登录。</p>
              </div>
            </div>
            <form class="password-form" @submit.prevent="submitChangePassword">
              <label>
                <span>当前密码</span>
                <input
                  v-model="passwordForm.current"
                  type="password"
                  autocomplete="current-password"
                  placeholder="请输入当前密码"
                  required
                  :disabled="passwordSubmitting"
                />
              </label>
              <label>
                <span>新密码</span>
                <input
                  v-model="passwordForm.next"
                  type="password"
                  autocomplete="new-password"
                  placeholder="至少 6 位，建议字母数字组合"
                  minlength="6"
                  required
                  :disabled="passwordSubmitting"
                />
              </label>
              <label>
                <span>确认新密码</span>
                <input
                  v-model="passwordForm.confirm"
                  type="password"
                  autocomplete="new-password"
                  placeholder="再次输入新密码"
                  minlength="6"
                  required
                  :disabled="passwordSubmitting"
                />
              </label>
              <div class="form-actions">
                <button type="submit" :disabled="passwordSubmitting">
                  {{ passwordSubmitting ? '提交中...' : '更新密码' }}
                </button>
                <button
                  type="button"
                  class="ghost-button"
                  :disabled="passwordSubmitting"
                  @click="resetPasswordForm"
                >
                  重置
                </button>
              </div>
              <p v-if="passwordError" class="error">{{ passwordError }}</p>
              <p v-if="passwordMessage" class="success-message">{{ passwordMessage }}</p>
            </form>
          </section>
        </section>

        <section v-if="activePage === 'upload'" class="card upload-card">
          <div class="section-heading">
            <div>
              <h2>媒体上传</h2>
              <p>上传图片或视频执行检测，系统将自动分析场景异常并生成报告。</p>
            </div>
          </div>

          <div class="media-type-selector" aria-label="媒体类型选择">
            <label :class="{ active: mediaType === 'image' }">
              <input v-model="mediaType" type="radio" name="media-type" value="image" />
              <span class="media-type-icon">🖼️</span>
              <span class="media-type-label">图片检测</span>
            </label>
            <label :class="{ active: mediaType === 'video' }">
              <input v-model="mediaType" type="radio" name="media-type" value="video" />
              <span class="media-type-icon">🎬</span>
              <span class="media-type-label">视频检测</span>
            </label>
          </div>

          <div
            :class="['dropzone', { dragging: isDraggingFile, ready: selectedFiles.length }]"
            @dragenter.prevent="handleDragEnter"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleFileDrop"
          >
            <label class="dropzone-picker">
              <input type="file" :accept="mediaType === 'image' ? 'image/*' : 'video/*'" multiple @change="handleFileChange" />
              <span class="dropzone-icon">+</span>
              <strong>{{ selectedFileLabel }}</strong>
              <small>
                {{ selectedFiles.length ? '已选择媒体文件，可重新拖入或点击更换整批文件' : mediaType === 'image' ? '支持 jpg、png 等常见图片格式，点击或拖入多份文件进行批量检测' : '支持 mp4、mov 等常见视频格式，点击或拖入多个视频进行批量检测' }}
              </small>
            </label>
          </div>

          <div v-if="selectedFiles.length" class="selected-file-list" aria-label="已选择媒体列表">
            <div class="batch-summary">
              <strong>已选择 {{ selectedFiles.length }} 个文件</strong>
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
                <h3>{{ currentPreview?.kind === 'video' ? '原始视频首帧预览' : '原始文件预览' }}</h3>
                <p>{{ currentPreview.file.name }}（{{ activePreviewIndex + 1 }}/{{ currentMediaPreviews.length }}）</p>
              </div>
              <div v-if="currentMediaPreviews.length > 1" class="pager-controls">
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
                v-if="currentMediaPreviews.length > 1"
                class="preview-arrow preview-arrow-left"
                type="button"
                aria-label="查看上一份原始文件"
                @click.stop="showPreviousPreview"
              >
                ‹
              </button>
              <video
                v-if="currentPreview?.kind === 'video'"
                :src="currentPreview.url"
                controls
                playsinline
                preload="metadata"
                class="preview-media"
              ></video>
              <img
                v-else
                :src="currentPreview.url"
                :alt="currentPreview.kind === 'video' ? '视频首帧预览' : '原始图片'"
                draggable="false"
                class="preview-media"
              />
              <button
                v-if="currentMediaPreviews.length > 1"
                class="preview-arrow preview-arrow-right"
                type="button"
                aria-label="查看下一份原始文件"
                @click.stop="showNextPreview"
              >
                ›
              </button>
            </div>
            <div v-if="currentMediaPreviews.length > 1" class="preview-strip" aria-label="原始文件缩略图列表">
              <button
                v-for="(item, index) in currentMediaPreviews"
                :key="`${item.file.name}-${item.file.size}-${item.file.lastModified}`"
                :class="{ active: activePreviewIndex === index }"
                type="button"
                @click="setActivePreview(index)"
              >
                <video
                  v-if="item.kind === 'video'"
                  :src="item.url"
                  muted
                  preload="metadata"
                  class="strip-media"
                ></video>
                <img v-else :src="item.url" :alt="item.file.name" class="strip-media" />
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
              <p>记录每一次图片或视频检测的操作时间、检测模式、目标数量和分析结果。</p>
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
            <p>完成一次图片或视频检测后，系统会在这里自动生成日志记录。</p>
            <button type="button" @click="switchMainPage('upload')">去上传媒体</button>
          </div>
        </section>

        <section v-if="activePage === 'users' && isAdmin" class="card user-admin-card">
          <div class="section-heading">
            <div>
              <h2>用户管理</h2>
              <p>管理员可以执行用户增删改查，并查看全部检测日志。</p>
            </div>
            <button type="button" :disabled="usersLoading" @click="fetchUsers">
              {{ usersLoading ? '刷新中...' : '刷新用户' }}
            </button>
          </div>

          <form class="user-create-form" @submit.prevent="createUser">
            <label>
              用户名
              <input v-model="userForm.username" autocomplete="off" placeholder="至少 3 个字符" />
            </label>
            <label>
              密码
              <input v-model="userForm.password" autocomplete="off" placeholder="至少 6 个字符" type="password" />
            </label>
            <label>
              角色
              <select v-model="userForm.role">
                <option value="NORMAL">普通用户</option>
                <option value="ADMIN">管理员</option>
              </select>
            </label>
            <button :disabled="usersLoading" type="submit">创建用户</button>
          </form>

          <p v-if="usersError" class="error">{{ usersError }}</p>
          <p v-if="usersMessage" class="success-message">{{ usersMessage }}</p>

          <table v-if="users.length" class="user-table">
            <thead>
              <tr>
                <th>用户名</th>
                <th>角色</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.username }}</td>
                <td>
                  <select :value="user.role" :disabled="user.id === currentUser?.id" @change="changeUserRole(user, $event.target.value)">
                    <option value="NORMAL">普通用户</option>
                    <option value="ADMIN">管理员</option>
                  </select>
                </td>
                <td>{{ user.is_active ? '启用' : '停用' }}</td>
                <td>{{ formatDateTime(user.created_at) }}</td>
                <td>
                  <div class="table-actions">
                    <button
                      type="button"
                      :disabled="user.id === currentUser?.id"
                      @click="openAdminPasswordDialog(user)"
                    >
                      重置密码
                    </button>
                    <button
                      type="button"
                      :disabled="user.id === currentUser?.id"
                      @click="toggleUserStatus(user)"
                    >
                      {{ user.is_active ? '停用' : '启用' }}
                    </button>
                    <button
                      type="button"
                      class="danger-table-button"
                      :disabled="user.id === currentUser?.id"
                      @click="deleteUser(user)"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-else-if="!usersLoading" class="empty">
            <h3>暂无用户数据</h3>
            <p>点击刷新用户或创建新用户。</p>
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

          <section v-if="currentBatchResults.length > 1" class="card batch-results-card">
            <div class="section-heading">
              <div>
                <h2>批量检测结果</h2>
                <p>共完成 {{ currentBatchResults.length }} 个文件检测，当前查看第 {{ activeResultIndex + 1 }} 个。</p>
              </div>
              <div class="pager-controls">
                <button type="button" @click="showPreviousResult">上一张</button>
                <button type="button" @click="showNextResult">下一张</button>
              </div>
            </div>
            <div class="batch-result-list" aria-label="批量检测结果列表">
              <button
                v-for="(item, index) in currentBatchResults"
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
                  <h3>批量媒体检测概览</h3>
                  <p>每个文件的原始预览、检测结果和摘要如下，点击卡片可切换下方详情。</p>
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
                        <span>{{ item.preview?.kind === 'video' ? '选中帧' : '原图' }}</span>
                        <img :src="item.sourcePreviewUrl" :alt="`${item.result.original_filename} 原始预览`" />
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
              <h3>{{ result.input_type === 'video' ? '选中帧与检测结果对比' : '原始图片与检测结果对比' }}</h3>
              <div class="compare-grid">
                <div>
                  <span>{{ result.input_type === 'video' ? '选中帧' : '原始图片' }}</span>
                  <button
                    v-if="originalCompareImageUrl"
                    class="image-detail-trigger"
                    type="button"
                    @click="openImageDetail('original')"
                  >
                    <img :src="originalCompareImageUrl" :alt="result.input_type === 'video' ? '选中帧' : '原始图片'" />
                    <span class="image-detail-badge">点击查看详情</span>
                  </button>
                  <p v-else class="empty compare-empty">当前会话暂无可对照的原始预览。</p>
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
                <div class="summary-panel-inner">
                  <div class="panel-section">
                    <h3>基本信息</h3>
                    <p>图片名称：<strong>{{ result.original_filename }}</strong></p>
                    <p>输入类型：<strong>{{ result.media_type_label || (result.input_type === 'video' ? '视频' : '图片') }}</strong></p>
                    <p>检测模式：<strong>{{ result.detection_mode_label || selectedDetectionMode.label }}</strong></p>
                    <p v-if="result.models_used?.length">启用模型：<strong>{{ formatModelsUsed(result.models_used) }}</strong></p>
                    <p>检测目标总数：<strong>{{ result.total_count }}</strong></p>
                    <p v-if="result.video_sampling?.selected_frame">选中帧：<strong>第 {{ result.video_sampling.selected_frame.frame_index }} 帧 · {{ formatTimestampMs(result.video_sampling.selected_frame.timestamp_ms) }}</strong></p>
                  </div>

                  <div class="panel-divider"></div>

                  <div v-if="analysis" class="panel-section">
                    <h3>风险评估</h3>
                    <p>场景类型：<strong>{{ analysis.scene_type }}</strong></p>
                    <p>综合风险：<span :class="['risk-badge', riskClass(analysis.risk_level)]">{{ analysis.risk_level }}</span></p>
                    <p v-if="analysis.scene_tags?.length">
                      场景标签：<span v-for="tag in analysis.scene_tags" :key="tag" class="scene-tag">{{ tag }}</span>
                    </p>
                  </div>

                  <div class="panel-divider"></div>

                  <div v-if="result.video_sampling" class="panel-section">
                    <h3>视频抽帧信息</h3>
                    <p>抽帧轮次：<strong>{{ result.video_sampling.total_attempts }}/{{ result.video_sampling.max_attempts }}</strong></p>
                    <p>质量阈值：<strong>{{ result.video_sampling.quality_threshold }}</strong>，最终质量分：<strong>{{ result.video_sampling.selected_frame?.quality_score ?? '--' }}</strong></p>
                    <p>视频时长：<strong>{{ formatDurationMs(result.video_sampling.duration_ms) }}</strong></p>
                    <p>抽帧结果：<strong>{{ result.video_sampling.threshold_met ? '达到检测标准' : '未达到阈值，已返回最佳帧' }}</strong></p>
                    <div v-if="result.video_sampling.attempts?.length" class="frame-preview-grid">
                      <h4>抽帧详情</h4>
                      <div class="frames-table">
                        <div class="frames-table-header">
                          <span>轮次</span>
                          <span>帧号</span>
                          <span>时间戳</span>
                          <span>质量分</span>
                          <span>检测数</span>
                        </div>
                        <div
                          v-for="(attempt, idx) in result.video_sampling.attempts"
                          :key="idx"
                        >
                          <div
                            v-for="(frame, fIdx) in attempt.frames"
                            :key="fIdx"
                            class="frames-table-row"
                            :class="{
                              'selected': result.video_sampling.selected_frame?.frame_index === frame.frame_index,
                              'best-in-attempt': fIdx === 0
                            }"
                          >
                            <span>第 {{ idx + 1 }} 轮</span>
                            <span class="frame-num">{{ frame.frame_index }}</span>
                            <span>{{ formatTimestampMs(frame.timestamp_ms) }}</span>
                            <span :class="getQualityClass(frame.quality_score)">{{ frame.quality_score }}</span>
                            <span>{{ frame.total_count }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="videoConsensus" class="panel-section">
                    <h3>连续帧共识</h3>
                    <div class="consensus-summary">
                      <div class="consensus-stat">
                        <span class="stat-label">时序帧数</span>
                        <span class="stat-value">{{ videoConsensus.frames_used }}<span class="unit">帧</span></span>
                      </div>
                      <div class="consensus-stat">
                        <span class="stat-label">采样帧数</span>
                        <span class="stat-value">{{ videoConsensus.sampling_frames_used }}<span class="unit">帧</span></span>
                      </div>
                      <div class="consensus-stat">
                        <span class="stat-label">平均质量分</span>
                        <span class="stat-value">{{ videoConsensus.average_quality_score?.toFixed(1) ?? '--' }}<span class="unit">分</span></span>
                      </div>
                      <div class="consensus-stat">
                        <span class="stat-label">平均目标数</span>
                        <span class="stat-value">{{ videoConsensus.average_total_count?.toFixed(1) ?? '--' }}<span class="unit">个</span></span>
                      </div>
                    </div>
                    <div class="consensus-tags">
                      <span class="tag-label">稳定类别：</span>
                      <span v-if="videoConsensus.stable_classes?.length" v-for="cls in videoConsensus.stable_classes" :key="cls" class="tag-item">{{ cls }}</span>
                      <span v-else class="tag-empty">暂无</span>
                    </div>
                    <div class="consensus-votes">
                      <span>场景投票：<strong>{{ formatVoteSummary(videoConsensus.scene_type_votes) }}</strong></span>
                      <span>风险投票：<strong>{{ formatVoteSummary(videoConsensus.risk_level_votes) }}</strong></span>
                    </div>
                    <div v-if="result?.video_sampling?.temporal_context?.module" class="temporal-analysis-box">
                      <div class="temporal-analysis-header">
                        <strong>{{ result.video_sampling.temporal_context.module.title }}</strong>
                        <span :class="['temporal-status', riskClass(result.video_sampling.temporal_context.module.status)]">
                          {{ result.video_sampling.temporal_context.module.status }} ({{ result.video_sampling.temporal_context.module.score }}分)
                        </span>
                      </div>
                      <p class="temporal-reason">{{ result.video_sampling.temporal_context.module.reason }}</p>
                      <p class="temporal-suggestion">{{ result.video_sampling.temporal_context.module.suggestion }}</p>
                      <div v-if="result.video_sampling.temporal_context.module.details" class="temporal-details">
                        <span v-if="result.video_sampling.temporal_context.module.details.vehicle_offroad > 0" class="detail-tag danger">车辆越界 {{ result.video_sampling.temporal_context.module.details.vehicle_offroad }}条</span>
                        <span v-if="result.video_sampling.temporal_context.module.details.vehicle_edge > 0" class="detail-tag warning">边缘行驶 {{ result.video_sampling.temporal_context.module.details.vehicle_edge }}条</span>
                        <span v-if="result.video_sampling.temporal_context.module.details.vehicle_lane_change > 0" class="detail-tag normal">变道 {{ result.video_sampling.temporal_context.module.details.vehicle_lane_change }}条</span>
                        <span v-if="result.video_sampling.temporal_context.module.details.person_offroad > 0" class="detail-tag danger">行人越界 {{ result.video_sampling.temporal_context.module.details.person_offroad }}条</span>
                        <span v-if="result.video_sampling.temporal_context.module.details.person_near_water > 0" class="detail-tag danger">行人近水 {{ result.video_sampling.temporal_context.module.details.person_near_water }}条</span>
                        <span v-if="result.video_sampling.temporal_context.module.details.vehicle_near_water > 0" class="detail-tag danger">车辆近水 {{ result.video_sampling.temporal_context.module.details.vehicle_near_water }}条</span>
                      </div>
                    </div>
                  </div>

                  <div class="panel-divider"></div>

                  <div class="panel-section">
                    <h3>自动分析报告</h3>
                    <div class="report">{{ result.report }}</div>
                    <div v-if="videoConsensus" class="report" style="margin-top: 10px">
                      <strong>连续帧共识摘要：</strong>本次视频共参考 <strong>{{ videoConsensus.frames_used }}</strong> 帧稳定类别{{ videoConsensus.stable_classes?.length ? `包括：${videoConsensus.stable_classes.join('、')}` : '暂无稳定类别' }}，场景投票为 <strong>{{ formatVoteSummary(videoConsensus.scene_type_votes) }}</strong>，风险投票为 <strong>{{ formatVoteSummary(videoConsensus.risk_level_votes) }}</strong>。
                    </div>
                  </div>
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

            <section v-if="videoConsensus" class="video-consensus-card">
              <div class="section-heading">
                <div>
                  <h3>连续帧时序分析（锚点帧±2帧，共5帧）</h3>
                  <p>通过分析锚点帧前后各2帧，判断车辆是否越界、变道或存在其他违规行为。</p>
                </div>
              </div>
              <div class="video-consensus-grid">
                <div v-for="item in videoConsensusRows" :key="item.label">
                  <span>{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                </div>
              </div>
              <div class="video-consensus-votes">
                <p>场景投票：{{ formatVoteSummary(videoConsensus.scene_type_votes) }}</p>
                <p>风险投票：{{ formatVoteSummary(videoConsensus.risk_level_votes) }}</p>
              </div>
              <div v-if="result?.video_sampling?.temporal_context?.module" class="temporal-analysis-box" style="margin-top: 16px">
                <div class="temporal-analysis-header">
                  <strong>{{ result.video_sampling.temporal_context.module.title }}</strong>
                  <span :class="['temporal-status', riskClass(result.video_sampling.temporal_context.module.status)]">
                    {{ result.video_sampling.temporal_context.module.status }} ({{ result.video_sampling.temporal_context.module.score }}分)
                  </span>
                </div>
                <p class="temporal-reason">{{ result.video_sampling.temporal_context.module.reason }}</p>
                <p class="temporal-suggestion">{{ result.video_sampling.temporal_context.module.suggestion }}</p>
                <div v-if="result.video_sampling.temporal_context.module.details" class="temporal-details">
                  <span v-if="result.video_sampling.temporal_context.module.details.vehicle_offroad > 0" class="detail-tag danger">车辆越界 {{ result.video_sampling.temporal_context.module.details.vehicle_offroad }}条</span>
                  <span v-if="result.video_sampling.temporal_context.module.details.vehicle_edge > 0" class="detail-tag warning">边缘行驶 {{ result.video_sampling.temporal_context.module.details.vehicle_edge }}条</span>
                  <span v-if="result.video_sampling.temporal_context.module.details.vehicle_lane_change > 0" class="detail-tag normal">变道 {{ result.video_sampling.temporal_context.module.details.vehicle_lane_change }}条</span>
                  <span v-if="result.video_sampling.temporal_context.module.details.person_offroad > 0" class="detail-tag danger">行人越界 {{ result.video_sampling.temporal_context.module.details.person_offroad }}条</span>
                  <span v-if="result.video_sampling.temporal_context.module.details.person_near_water > 0" class="detail-tag danger">行人近水 {{ result.video_sampling.temporal_context.module.details.person_near_water }}条</span>
                  <span v-if="result.video_sampling.temporal_context.module.details.vehicle_near_water > 0" class="detail-tag danger">车辆近水 {{ result.video_sampling.temporal_context.module.details.vehicle_near_water }}条</span>
                </div>
              </div>
            </section>

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
              当前文件没有检测到自训练航拍场景模型可识别的目标。
            </p>
          </section>
        </section>

        <section v-if="activePage === 'results' && !result" class="card empty-result">
          <h2>暂无检测结果</h2>
          <p>请先进入媒体上传页面，选择航拍图片或视频并完成智能识别。</p>
          <button type="button" @click="switchMainPage('upload')">去上传媒体</button>
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
              <span>文件详情</span>
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
              <p>文件名称：{{ result?.original_filename || '当前文件' }}</p>
              <p v-if="result">检测模式：{{ result.detection_mode_label || selectedDetectionMode.label }}</p>
              <p v-if="imageDetailType === 'result' && result">目标总数：{{ result.total_count }}</p>
              <p v-if="imageDetailType === 'original'">{{ result?.input_type === 'video' ? '当前展示的是视频中用于检测的关键帧。' : '原始图片用于和检测结果进行位置对照。' }}</p>

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

  <div
    v-if="adminPasswordTarget"
    class="image-detail-modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="admin-password-title"
  >
    <div class="image-detail-dialog admin-password-dialog">
      <button
        type="button"
        class="image-detail-close"
        aria-label="关闭"
        :disabled="adminPasswordSubmitting"
        @click="closeAdminPasswordDialog"
      >
        ×
      </button>
      <div class="admin-password-content">
        <h3 id="admin-password-title">重置用户密码</h3>
        <p>正在为 <strong>{{ adminPasswordTarget.username }}</strong> 设置新密码，操作成功后将自动使该账号的现有登录失效。</p>
        <form class="password-form" @submit.prevent="submitAdminPasswordReset">
          <label>
            <span>新密码</span>
            <input
              v-model="adminPasswordValue"
              type="password"
              autocomplete="new-password"
              minlength="6"
              placeholder="至少 6 位，建议字母数字组合"
              required
              :disabled="adminPasswordSubmitting"
            />
          </label>
          <div class="form-actions">
            <button type="submit" :disabled="adminPasswordSubmitting">
              {{ adminPasswordSubmitting ? '提交中...' : '保存新密码' }}
            </button>
            <button
              type="button"
              class="ghost-button"
              :disabled="adminPasswordSubmitting"
              @click="closeAdminPasswordDialog"
            >
              取消
            </button>
          </div>
          <p v-if="adminPasswordError" class="error">{{ adminPasswordError }}</p>
          <p v-if="adminPasswordMessage" class="success-message">{{ adminPasswordMessage }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onBeforeUnmount, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const backendBaseUrl = 'http://127.0.0.1:8000'

const mediaType = ref('image')
const selectedImageFiles = ref([])
const selectedVideoFiles = ref([])
const selectedImagePreviews = ref([])
const selectedVideoPreviews = ref([])
const activePreviewIndex = ref(0)
const selectedFile = ref(null)
const previewUrl = ref('')
const result = ref(null)
const imageBatchResults = ref([])
const videoBatchResults = ref([])
const activeResultIndex = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const detectionMode = ref('fusion')
const isDraggingFile = ref(false)
const dragDepth = ref(0)

const selectedFiles = computed(() => {
  return mediaType.value === 'image' ? selectedImageFiles.value : selectedVideoFiles.value
})

const currentMediaPreviews = computed(() => {
  return mediaType.value === 'image' ? selectedImagePreviews.value : selectedVideoPreviews.value
})

const currentBatchResults = computed(() => {
  return mediaType.value === 'image' ? imageBatchResults.value : videoBatchResults.value
})
const activePage = ref('home')
const activeTab = ref('overview')
const authToken = ref(localStorage.getItem('auth_token') || '')
const currentUser = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
const authMode = ref('login')
const loginLoading = ref(false)
const loginError = ref('')
const registerLoading = ref(false)
const registerError = ref('')
const registerSuccess = ref('')
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})
const imageDetailOpen = ref(false)
const imageDetailType = ref('result')
const detectionLogs = ref([])
const logsLoading = ref(false)
const logsError = ref('')
const users = ref([])
const usersLoading = ref(false)
const usersError = ref('')
const usersMessage = ref('')
const accountLoading = ref(false)
const accountError = ref('')
const accountMessage = ref('')
const passwordForm = ref({ current: '', next: '', confirm: '' })
const passwordSubmitting = ref(false)
const passwordError = ref('')
const passwordMessage = ref('')
const adminPasswordTarget = ref(null)
const adminPasswordValue = ref('')
const adminPasswordSubmitting = ref(false)
const adminPasswordError = ref('')
const adminPasswordMessage = ref('')
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
  username: '',
  password: ''
})
const userForm = ref({
  username: '',
  password: '',
  role: 'NORMAL'
})

const barChartRef = ref(null)
const pieChartRef = ref(null)

const detectionModes = [
  {
    value: 'fusion',
    label: '融合检测',
    shortLabel: '融合',
    hint: '巡检策略自动结合场景语义和细粒度目标，生成完整的异常分析与巡检建议。'
  }
]

const tabs = [
  { key: 'overview', label: '检测总览' },
  { key: 'analysis', label: '异常分析' },
  { key: 'charts', label: '统计图表' },
  { key: 'recommendations', label: '巡检建议' },
  { key: 'details', label: '检测详情' }
]

const analysis = computed(() => result.value?.analysis || null)
const isAdmin = computed(() => currentUser.value?.role === 'ADMIN')
const accountRoleDescription = computed(() => {
  if (currentUser.value?.role === 'NORMAL') return '普通用户可上传图片或视频执行检测，并查看自己的检测日志。'
  return '管理员可查看和管理所有用户，并查看全部检测日志。'
})
const videoConsensus = computed(() => {
  return result.value?.video_sampling?.consensus || analysis.value?.video_consensus || result.value?.video_consensus || null
})
const currentPreview = computed(() => currentMediaPreviews.value[activePreviewIndex.value] || null)
const batchOverviewItems = computed(() => {
  return currentBatchResults.value.map((item, idx) => ({
    ...item,
    preview: currentMediaPreviews.value[idx] || null,
    sourcePreviewUrl: item.result?.source_image_url
      ? `${backendBaseUrl}${item.result.source_image_url}`
      : currentMediaPreviews.value[idx]?.url || ''
  }))
})
const originalCompareImageUrl = computed(() => {
  if (result.value?.source_image_url) {
    return `${backendBaseUrl}${result.value.source_image_url}`
  }
  return currentPreview.value?.url || ''
})
const imageDetailTitle = computed(() => {
  if (imageDetailType.value === 'result') return '检测结果图'
  return result.value?.input_type === 'video' ? '视频选中帧' : '原始图片'
})
const imageDetailSrc = computed(() => {
  if (imageDetailType.value === 'original') return originalCompareImageUrl.value
  return result.value?.result_image_url ? `${backendBaseUrl}${result.value.result_image_url}` : ''
})
const selectedDetectionMode = computed(() => {
  return detectionModes.find(mode => mode.value === detectionMode.value) || detectionModes[0]
})
const selectedFileLabel = computed(() => {
  if (!selectedFiles.value.length) return mediaType.value === 'image' ? '拖拽航拍图片到这里' : '拖拽视频到这里'
  if (selectedFiles.value.length === 1) return selectedFiles.value[0].name
  const unit = mediaType.value === 'image' ? '张图片' : '个视频'
  return `已选择 ${selectedFiles.value.length} ${unit}`
})
const uploadActionLabel = computed(() => {
  if (!loading.value) {
    const prefix = mediaType.value === 'image' ? '图片' : '视频'
    return selectedFiles.value.length > 1 ? `开始批量${prefix}智能识别` : `开始${prefix}智能识别`
  }
  if (batchProgress.value.total > 1) {
    return `检测中 ${batchProgress.value.completed}/${batchProgress.value.total}`
  }
  return '检测中...'
})
const pageTitles = {
  home: '系统首页',
  account: '账号信息',
  upload: '媒体上传',
  results: '检测结果',
  logs: '检测日志',
  users: '用户管理'
}
const currentPageTitle = computed(() => pageTitles[activePage.value] || '系统首页')
const mainNavItems = computed(() => {
  const items = [
    { key: 'home', label: '首页', icon: '⌂', disabled: false },
    { key: 'account', label: '账号信息', icon: '¤', disabled: false },
    { key: 'upload', label: '上传检测', icon: '+', disabled: false },
    { key: 'results', label: '结果分析', icon: '▣', disabled: !result.value },
    { key: 'logs', label: '检测日志', icon: '≡', disabled: false }
  ]
  if (isAdmin.value) {
    items.push({ key: 'users', label: '用户管理', icon: '◎', disabled: false })
  }
  return items
})
const recommendationItems = computed(() => {
  if (!analysis.value?.modules) return []
  return analysis.value.modules.map(module => ({
    key: module.key,
    title: module.title,
    status: module.status,
    suggestion: module.suggestion
  }))
})
const videoConsensusRows = computed(() => {
  if (!videoConsensus.value) return []
  const temporalContext = result.value?.video_sampling?.temporal_context
  const temporalModule = temporalContext?.module
  const details = temporalModule?.details || {}
  return [
    { label: '时序帧数', value: videoConsensus.value.frames_used ?? '--', unit: '帧' },
    { label: '采样帧数', value: videoConsensus.value.sampling_frames_used ?? '--', unit: '帧' },
    { label: '平均质量分', value: videoConsensus.value.average_quality_score?.toFixed(1) ?? '--', unit: '分' },
    { label: '平均目标数', value: videoConsensus.value.average_total_count?.toFixed(1) ?? '--', unit: '个' },
    { label: '稳定类别', value: videoConsensus.value.stable_classes?.length ? videoConsensus.value.stable_classes.join('、') : '暂无' },
    { label: '时序评分', value: temporalContext?.combined_score?.toFixed(1) ?? '--', unit: '分' },
    { label: '时序状态', value: temporalModule?.status ?? '--' },
    { label: '车辆越界', value: details.vehicle_offroad ?? 0, unit: '条' },
    { label: '车辆边缘', value: details.vehicle_edge ?? 0, unit: '条' },
    { label: '车辆变道', value: details.vehicle_lane_change ?? 0, unit: '条' },
    { label: '行人越界', value: details.person_offroad ?? 0, unit: '条' },
    { label: '行人近水', value: details.person_near_water ?? 0, unit: '条' },
    { label: '车辆近水', value: details.vehicle_near_water ?? 0, unit: '条' }
  ]
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
const quickStats = computed(() => [
  {
    label: '当前身份',
    value: currentUser.value?.role_label || formatRole(currentUser.value?.role),
    hint: accountRoleDescription.value,
    className: currentUser.value?.role === 'ADMIN' ? 'stat-info' : 'stat-warning'
  },
  {
    label: '检测目标',
    value: consoleTargetCount.value,
    hint: result.value ? '最近一次检测结果' : '完成检测后显示',
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
    hint: '已加载最近检测记录',
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
  if (metrics.offroad_vehicle_count > 0) actions.push('复核疑似越界车辆位置，判断是否为停车区域、非道路行驶或检测误差。')
  if (metrics.water_near_vehicle_count > 0) actions.push('检查水域周边车辆活动，必要时标记为临水安全风险点。')
  if (metrics.vehicle_count >= 12) actions.push('对车辆密集区域进行交通密度评估，可结合多张图片或连续帧判断拥堵趋势。')
  if (metrics.low_confidence_count > 0) actions.push('对低置信度目标进行人工确认，必要时提高图像分辨率后重新检测。')
  if (actions.length === 1) actions.push('继续上传同区域不同角度或不同时刻的图片、视频，形成可对比的巡检样本。')
  return actions
})

let barChart = null
let pieChart = null
let resizeFrame = 0
let previewSwipeStartX = 0
let previewSwipeCurrentX = 0
let previewSwipeActive = false

onMounted(async () => {
  window.addEventListener('resize', handleChartResize)
  loginForm.value = { username: '', password: '', confirmPassword: '' }
  userForm.value = { username: '', password: '', role: 'NORMAL' }
  if (authToken.value) {
    await fetchCurrentUser()
    // 登录后自动获取日志
    await fetchDetectionLogs()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleChartResize)
  if (resizeFrame) cancelAnimationFrame(resizeFrame)
  barChart?.dispose()
  pieChart?.dispose()
  revokePreviewUrls()
})

function handleChartResize() {
  if (resizeFrame) cancelAnimationFrame(resizeFrame)
  resizeFrame = requestAnimationFrame(() => {
    barChart?.resize()
    pieChart?.resize()
  })
}

function authHeaders() {
  return {
    Authorization: `Bearer ${authToken.value}`
  }
}

function formatRole(role) {
  if (role === 'ADMIN') return '管理员'
  if (role === 'NORMAL') return '普通用户'
  return role || '--'
}

function switchAuthMode(mode) {
  authMode.value = mode
  loginError.value = ''
  registerError.value = ''
  registerSuccess.value = ''
  registerForm.value = { username: '', password: '', confirmPassword: '' }
}

function syncCurrentUser(user) {
  if (!user) return
  currentUser.value = user
  localStorage.setItem('auth_user', JSON.stringify(currentUser.value))
  // 用户信息同步后自动获取日志
  fetchDetectionLogs()
}

async function fetchCurrentUser() {
  if (!authToken.value) return
  accountLoading.value = true
  accountError.value = ''
  try {
    const response = await axios.get(`${backendBaseUrl}/auth/me`, {
      headers: authHeaders()
    })
    syncCurrentUser(response.data.user)
  } catch (error) {
    console.error(error)
    if (error.response?.status === 401) {
      clearAuth()
      accountError.value = '登录已过期，请重新登录'
    } else {
      accountError.value = error.response?.data?.detail || '账号信息加载失败'
    }
  } finally {
    accountLoading.value = false
  }
}

function resetPasswordForm() {
  passwordForm.value = { current: '', next: '', confirm: '' }
  passwordError.value = ''
  passwordMessage.value = ''
}

async function submitChangePassword() {
  passwordError.value = ''
  passwordMessage.value = ''
  const { current, next, confirm } = passwordForm.value
  if (!current || !next || !confirm) {
    passwordError.value = '请完整填写当前密码与新密码'
    return
  }
  if (next.length < 6) {
    passwordError.value = '新密码至少需要 6 个字符'
    return
  }
  if (next !== confirm) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  if (next === current) {
    passwordError.value = '新密码不能与当前密码相同'
    return
  }
  passwordSubmitting.value = true
  try {
    const response = await axios.post(
      `${backendBaseUrl}/auth/change-password`,
      { current_password: current, new_password: next },
      { headers: authHeaders() }
    )
    passwordMessage.value = response.data?.message || '密码修改成功，请重新登录'
    resetPasswordForm()
    window.setTimeout(() => {
      clearAuth()
    }, 1200)
  } catch (error) {
    console.error(error)
    passwordError.value = error.response?.data?.detail || '密码修改失败，请稍后再试'
  } finally {
    passwordSubmitting.value = false
  }
}

function handleFileChange(event) {
  setSelectedFiles(event.target.files)
  event.target.value = ''
}

async function setSelectedFiles(fileList) {
  const files = Array.from(fileList || [])
  if (!files.length) return

  const filterType = mediaType.value === 'image' ? 'image/' : 'video/'
  const mediaFiles = files.filter(file => file.type.startsWith(filterType))
  if (!mediaFiles.length) {
    errorMessage.value = mediaType.value === 'image' ? '请上传 jpg、png 等图片文件' : '请上传 mp4、mov 等视频文件'
    return
  }

  if (mediaType.value === 'image') {
    selectedImageFiles.value = mediaFiles
  } else {
    selectedVideoFiles.value = mediaFiles
  }

  const previews = await Promise.all(mediaFiles.map(async file => {
    const url = URL.createObjectURL(file)
    const kind = file.type.startsWith('video/') ? 'video' : 'image'
    const posterUrl = kind === 'video' ? await createVideoPoster(url) : url
    return { file, url, kind, posterUrl }
  }))

  if (mediaType.value === 'image') {
    revokeImagePreviewUrls()
    selectedImagePreviews.value = previews
    imageBatchResults.value = []
  } else {
    revokeVideoPreviewUrls()
    selectedVideoPreviews.value = previews
    videoBatchResults.value = []
  }

  activePreviewIndex.value = 0
  selectedFile.value = mediaFiles[0]
  previewUrl.value = previews[0]?.url || ''
  result.value = null
  errorMessage.value = ''
  activeTab.value = 'overview'
  batchProgress.value = {
    total: 0,
    completed: 0,
    failed: 0,
    currentName: ''
  }
  if (mediaFiles.length < files.length) {
    errorMessage.value = `已忽略 ${files.length - mediaFiles.length} 个非媒体文件`
  }
}

function revokeImagePreviewUrls() {
  selectedImagePreviews.value.forEach(item => {
    if (item.posterUrl && item.posterUrl !== item.url) URL.revokeObjectURL(item.posterUrl)
    URL.revokeObjectURL(item.url)
  })
  selectedImagePreviews.value = []
}

function revokeVideoPreviewUrls() {
  selectedVideoPreviews.value.forEach(item => {
    if (item.posterUrl && item.posterUrl !== item.url) URL.revokeObjectURL(item.posterUrl)
    URL.revokeObjectURL(item.url)
  })
  selectedVideoPreviews.value = []
}

function revokePreviewUrls() {
  revokeImagePreviewUrls()
  revokeVideoPreviewUrls()
  previewUrl.value = ''
}

function setActivePreview(index) {
  if (!currentMediaPreviews.value.length) return
  const nextIndex = (index + currentMediaPreviews.value.length) % currentMediaPreviews.value.length
  const nextPreview = currentMediaPreviews.value[nextIndex]
  activePreviewIndex.value = nextIndex
  selectedFile.value = nextPreview.file
  previewUrl.value = nextPreview.url
}

// 点击帧缩略图时切换到该帧
function selectFrameFromPreview(frameInfo) {
  if (!currentMediaPreviews.value.length) return
  // 查找匹配的帧预览
  const matchIndex = currentMediaPreviews.value.findIndex(
    p => p.url && frameInfo.source_image_url && p.url.includes(frameInfo.source_image_url.split('/').pop())
  )
  if (matchIndex >= 0) {
    setActivePreview(matchIndex)
  }
}

function showPreviousPreview() {
  setActivePreview(activePreviewIndex.value - 1)
}

function showNextPreview() {
  setActivePreview(activePreviewIndex.value + 1)
}

async function selectBatchResult(index) {
  if (!currentBatchResults.value.length) return
  const nextIndex = (index + currentBatchResults.value.length) % currentBatchResults.value.length
  const item = currentBatchResults.value[nextIndex]
  activeResultIndex.value = nextIndex
  result.value = item.result
  setActivePreview(nextIndex)
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
  if (currentMediaPreviews.value.length < 2) return
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
  if (deltaX > 0) showPreviousPreview()
  else showNextPreview()
}

function cancelPreviewSwipe() {
  previewSwipeActive = false
}

function formatFileSize(size) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

function formatTimestampMs(value) {
  if (value === null || value === undefined) return '--'
  return `${(Number(value) / 1000).toFixed(2)} 秒`
}

function formatDurationMs(value) {
  if (value === null || value === undefined) return '--'
  const totalSeconds = Math.round(Number(value) / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  if (!minutes) return `${seconds} 秒`
  return `${minutes} 分 ${seconds} 秒`
}

function getQualityClass(score) {
  if (score === null || score === undefined) return ''
  if (score >= 60) return 'quality-high'
  if (score >= 40) return 'quality-medium'
  return 'quality-low'
}

function formatVoteSummary(votes) {
  if (!votes || !Object.keys(votes).length) return '暂无投票结果'
  return Object.entries(votes)
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .map(([label, count]) => `${label} ${count} 票`)
    .join('，')
}

function createVideoPoster(videoUrl) {
  return new Promise(resolve => {
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.muted = true
    video.playsInline = true

    const fallback = () => resolve(videoUrl)
    const cleanup = () => {
      video.pause()
      video.removeAttribute('src')
      video.load()
    }

    video.addEventListener('error', () => {
      cleanup()
      fallback()
    }, { once: true })

    video.addEventListener('loadeddata', () => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = video.videoWidth || 1280
        canvas.height = video.videoHeight || 720
        const context = canvas.getContext('2d')
        if (!context) {
          cleanup()
          fallback()
          return
        }
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        canvas.toBlob(blob => {
          cleanup()
          if (!blob) {
            fallback()
            return
          }
          resolve(URL.createObjectURL(blob))
        }, 'image/jpeg', 0.92)
      } catch (error) {
        cleanup()
        fallback()
      }
    }, { once: true })

    video.src = videoUrl
  })
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
  if (dragDepth.value === 0) isDraggingFile.value = false
}

function handleFileDrop(event) {
  dragDepth.value = 0
  isDraggingFile.value = false
  setSelectedFiles(event.dataTransfer?.files)
}

async function detectImage() {
  if (!selectedFiles.value.length) {
    errorMessage.value = '请先选择图片或视频文件'
    return
  }

  loading.value = true
  errorMessage.value = ''
  result.value = null
  if (mediaType.value === 'image') {
    imageBatchResults.value = []
  } else {
    videoBatchResults.value = []
  }
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
            ...authHeaders(),
            'Content-Type': 'multipart/form-data'
          }
        })

        latestResult = response.data
        result.value = response.data
        const batchResults = mediaType.value === 'image' ? imageBatchResults : videoBatchResults
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
        errorMessage.value = error.response?.data?.detail || '部分文件检测失败'
      }
    }

    batchProgress.value.currentName = ''

    if (latestResult) {
      await selectBatchResult(currentBatchResults.value.length - 1)
      await switchMainPage('results')
      activeTab.value = 'overview'
    }

    if (batchProgress.value.failed && batchProgress.value.completed) {
      errorMessage.value = `批量检测完成，成功 ${batchProgress.value.completed} 个，失败 ${batchProgress.value.failed} 个`
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
    localStorage.setItem('auth_token', authToken.value)
    syncCurrentUser(response.data.user)
    resetAllState()
    await fetchDetectionLogs()
    await switchMainPage('home')
  } catch (error) {
    console.error(error)
    loginError.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loginLoading.value = false
  }
}

function resetAllState() {
  mediaType.value = 'image'
  selectedImageFiles.value = []
  selectedVideoFiles.value = []
  selectedImagePreviews.value = []
  selectedVideoPreviews.value = []
  activePreviewIndex.value = 0
  selectedFile.value = null
  previewUrl.value = ''
  result.value = null
  imageBatchResults.value = []
  videoBatchResults.value = []
  activeResultIndex.value = 0
  activePage.value = 'home'
  activeTab.value = 'overview'
  imageDetailOpen.value = false
  imageDetailType.value = 'result'
  loading.value = false
  errorMessage.value = ''
}

async function register() {
  registerError.value = ''
  registerSuccess.value = ''

  if (registerForm.value.username.trim().length < 3) {
    registerError.value = '用户名至少需要 3 个字符'
    return
  }
  if (registerForm.value.password.length < 6) {
    registerError.value = '密码至少需要 6 个字符'
    return
  }
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerError.value = '两次输入的密码不一致'
    return
  }

  registerLoading.value = true
  try {
    await axios.post(`${backendBaseUrl}/register`, {
      username: registerForm.value.username.trim(),
      password: registerForm.value.password,
    })
    registerSuccess.value = '注册成功！请使用新账号登录。'
    registerForm.value = { username: '', password: '', confirmPassword: '' }
    setTimeout(() => switchAuthMode('login'), 1500)
  } catch (error) {
    console.error(error)
    registerError.value = error.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    registerLoading.value = false
  }
}

async function logout() {
  try {
    if (authToken.value) {
      await axios.post(`${backendBaseUrl}/auth/logout`, null, {
        headers: authHeaders()
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
  users.value = []
  loginForm.value = { username: '', password: '' }
  userForm.value = { username: '', password: '', role: 'NORMAL' }
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_user')
  resetAllState()
}

async function switchMainPage(pageKey) {
  activePage.value = pageKey
  if (pageKey === 'logs') await fetchDetectionLogs()
  if (pageKey === 'users' && isAdmin.value) await fetchUsers()
  if (pageKey === 'account') await fetchCurrentUser()
  if (pageKey === 'results' && activeTab.value === 'charts') {
    await nextTick()
    renderCharts()
  }
}

async function fetchUsers() {
  if (!isAdmin.value) return
  usersLoading.value = true
  usersError.value = ''
  usersMessage.value = ''

  try {
    const response = await axios.get(`${backendBaseUrl}/users`, {
      headers: authHeaders()
    })
    users.value = response.data.users || []
  } catch (error) {
    console.error(error)
    if (error.response?.status === 401) {
      clearAuth()
      usersError.value = '登录已过期，请重新登录'
    } else {
      usersError.value = error.response?.data?.detail || '用户列表加载失败'
    }
  } finally {
    usersLoading.value = false
  }
}

async function createUser() {
  usersLoading.value = true
  usersError.value = ''
  usersMessage.value = ''
  try {
    await axios.post(`${backendBaseUrl}/users`, userForm.value, {
      headers: authHeaders()
    })
    usersMessage.value = '用户创建成功'
    userForm.value = {
      username: '',
      password: '',
      role: 'NORMAL'
    }
    await fetchUsers()
  } catch (error) {
    console.error(error)
    usersError.value = error.response?.data?.detail || '用户创建失败'
  } finally {
    usersLoading.value = false
  }
}

async function updateUser(userId, payload) {
  usersError.value = ''
  usersMessage.value = ''
  try {
    await axios.patch(`${backendBaseUrl}/users/${userId}`, payload, {
      headers: authHeaders()
    })
    usersMessage.value = '用户信息已更新'
    await fetchUsers()
  } catch (error) {
    console.error(error)
    usersError.value = error.response?.data?.detail || '用户更新失败'
    await fetchUsers()
  }
}

async function changeUserRole(user, role) {
  await updateUser(user.id, { role })
}

async function toggleUserStatus(user) {
  await updateUser(user.id, { status: user.is_active ? 0 : 1 })
}

async function deleteUser(user) {
  const confirmed = window.confirm(`确认删除用户 ${user.username} 吗？此操作不可撤销。`)
  if (!confirmed) return
  usersError.value = ''
  usersMessage.value = ''
  try {
    await axios.delete(`${backendBaseUrl}/users/${user.id}`, {
      headers: authHeaders()
    })
    usersMessage.value = '用户已删除'
    await fetchUsers()
  } catch (error) {
    console.error(error)
    usersError.value = error.response?.data?.detail || '删除用户失败'
  }
}

function openAdminPasswordDialog(user) {
  adminPasswordTarget.value = user
  adminPasswordValue.value = ''
  adminPasswordError.value = ''
  adminPasswordMessage.value = ''
}

function closeAdminPasswordDialog() {
  if (adminPasswordSubmitting.value) return
  adminPasswordTarget.value = null
  adminPasswordValue.value = ''
  adminPasswordError.value = ''
  adminPasswordMessage.value = ''
}

async function submitAdminPasswordReset() {
  if (!adminPasswordTarget.value) return
  adminPasswordError.value = ''
  adminPasswordMessage.value = ''
  const newPassword = adminPasswordValue.value.trim()
  if (!newPassword) {
    adminPasswordError.value = '请输入新密码'
    return
  }
  if (newPassword.length < 6) {
    adminPasswordError.value = '新密码至少需要 6 个字符'
    return
  }
  adminPasswordSubmitting.value = true
  try {
    await axios.patch(
      `${backendBaseUrl}/users/${adminPasswordTarget.value.id}`,
      { password: newPassword },
      { headers: authHeaders() }
    )
    adminPasswordMessage.value = `已为 ${adminPasswordTarget.value.username} 重置密码`
    window.setTimeout(() => {
      adminPasswordTarget.value = null
      adminPasswordValue.value = ''
    }, 1200)
  } catch (error) {
    console.error(error)
    adminPasswordError.value = error.response?.data?.detail || '重置密码失败，请稍后再试'
  } finally {
    adminPasswordSubmitting.value = false
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
      headers: authHeaders()
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

  detectionLogs.value = [log, ...detectionLogs.value.filter(item => item.id !== log.id)]
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
  if (!response.ok) throw new Error(`图片读取失败：${response.status}`)
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
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 30000)
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
    if (result.value?.source_image_url) {
      originalImageDataUrl = await imageUrlToDataUrl(`${backendBaseUrl}${result.value.source_image_url}`)
    } else if (selectedFile.value && selectedFile.value.type.startsWith('image/')) {
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
    const currentVideoConsensus = videoConsensus.value
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
    const consensusRows = currentVideoConsensus
      ? `
        <p>参考帧数：${escapeHtml(currentVideoConsensus.frames_used ?? '--')}</p>
        <p>平均质量分：${escapeHtml(currentVideoConsensus.average_quality_score ?? '--')}</p>
        <p>平均目标数：${escapeHtml(currentVideoConsensus.average_total_count ?? '--')}</p>
        <p>稳定类别：${escapeHtml(currentVideoConsensus.stable_classes?.length ? currentVideoConsensus.stable_classes.join('、') : '暂无稳定类别')}</p>
        <p>场景投票：${escapeHtml(formatVoteSummary(currentVideoConsensus.scene_type_votes))}</p>
        <p>风险投票：${escapeHtml(formatVoteSummary(currentVideoConsensus.risk_level_votes))}</p>
      `
      : ''

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
          <p class="meta">文件名称：${escapeHtml(result.value.original_filename)}</p>
          <p class="meta">输入类型：${escapeHtml(result.value.media_type_label || (result.value.input_type === 'video' ? '视频' : '图片'))}</p>
          <p class="meta">检测模式：${escapeHtml(result.value.detection_mode_label || selectedDetectionMode.value.label)}</p>
          <p class="meta">启用模型：${escapeHtml(formatModelsUsed(result.value.models_used || [])) || '未记录'}</p>

          <h2>一、检测摘要</h2>
          <p>检测目标总数：${escapeHtml(result.value.total_count)}</p>
          <p>场景类型：${escapeHtml(currentAnalysis?.scene_type || '未识别到明确巡检场景')}</p>
          <p>综合风险：<span class="risk">${escapeHtml(currentAnalysis?.risk_level || '未评估')}</span></p>
          <p>风险评分：${escapeHtml(currentAnalysis?.risk_score ?? '--')}</p>
          ${sceneTags ? `<p>${sceneTags}</p>` : ''}
          <div class="summary">${escapeHtml(result.value.report || currentAnalysis?.summary || '暂无自动分析报告')}</div>
          ${currentVideoConsensus ? `<div class="summary">${consensusRows}</div>` : ''}

          <h2>二、结果对比</h2>
          <div class="image-grid">
            <div class="image-cell">
              <h3>${result.value.input_type === 'video' ? '选中帧' : '原始图片'}</h3>
              ${originalImageDataUrl ? `<img src="${originalImageDataUrl}" alt="${result.value.input_type === 'video' ? '选中帧' : '原始图片'}">` : '<p>当前会话没有可导出的原始预览。</p>'}
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

  if (barChart) barChart.dispose()
  if (pieChart) pieChart.dispose()

  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      tooltip: {},
      xAxis: { type: 'category', data: names },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{ name: '数量', type: 'bar', data: values }]
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        name: '类别占比',
        type: 'pie',
        radius: '65%',
        data: names.map(name => ({ name, value: classCount[name] }))
      }]
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
    radial-gradient(ellipse at 20% 0%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 100%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
    linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  color: #172033;
}

.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 27, 75, 0.8) 50%, rgba(15, 23, 42, 0.85) 100%),
    url('/src/assets/hero.png') center / cover no-repeat;
  position: relative;
  overflow: hidden;
}

.login-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.4) 0%, transparent 40%),
    radial-gradient(circle at 70% 80%, rgba(16, 185, 129, 0.3) 0%, transparent 40%);
  pointer-events: none;
  animation: login-bg-float 12s ease-in-out infinite alternate;
}

@keyframes login-bg-float {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(2%, -2%) scale(1.05);
  }
}

.login-panel {
  position: relative;
  z-index: 1;
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: 1.1fr 380px;
  gap: 28px;
  align-items: center;
  animation: panel-fade-in 0.8s ease;
}

@keyframes panel-fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-copy {
  color: #ffffff;
  text-align: left;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  gap: 16px;
  height: 100%;
  min-height: 100%;
  padding: 24px 8px;
}

.login-copy h1 {
  margin: 0;
  max-width: 620px;
  color: #ffffff;
  font-size: 38px;
  line-height: 1.2;
  font-weight: 700;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.login-copy p {
  margin: 0;
  max-width: 580px;
  color: #dbeafe;
  line-height: 1.8;
  font-size: 16px;
}

.login-card {
  display: grid;
  gap: 0;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.4);
  text-align: left;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  align-self: stretch;
  height: 100%;
}

.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
}

.auth-tabs button {
  min-height: 50px;
  border: none;
  border-radius: 0;
  background: transparent;
  color: #64748b;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
}

.auth-tabs button:hover:not(.active) {
  background: rgba(255, 255, 255, 0.6);
  color: #1e293b;
}

.auth-tabs button.active {
  background: #ffffff;
  color: #6366f1;
}

.auth-tabs button.active::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 3px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 3px 3px 0 0;
}

.login-card form {
  display: grid;
  gap: 18px;
  padding: 30px;
}

.login-card h2 {
  margin: 0;
  color: #1e1b4b;
  font-size: 22px;
}

.login-card label,
.user-create-form label,
.quota-adjust-form label {
  display: grid;
  gap: 8px;
  color: #475569;
  font-size: 14px;
  font-weight: 700;
}

.login-card input,
.user-create-form input,
.user-create-form select,
.user-table select,
.quota-adjust-form input {
  width: 100%;
  box-sizing: border-box;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  color: #1e293b;
  background: #f8fafc;
  font-size: 15px;
  transition: all 0.25s ease;
}

.login-card input:hover,
.user-create-form input:hover,
.user-create-form select:hover,
.user-table select:hover,
.quota-adjust-form input:hover {
  border-color: #94a3b8;
  background: #ffffff;
}

.login-card input:focus,
.user-create-form input:focus,
.user-create-form select:focus,
.user-table select:focus,
.quota-adjust-form input:focus {
  outline: none;
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

.login-card button {
  width: 100%;
  min-height: 46px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
}

.login-card button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
}

.login-card button:active {
  transform: translateY(0);
}

.login-card button:disabled {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.login-hint {
  color: #64748b;
  font-size: 13px;
  text-align: center;
}

.header {
  position: relative;
  padding: 40px 24px 28px;
  text-align: center;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(49, 46, 129, 0.92) 50%, rgba(15, 23, 42, 0.96) 100%),
    url('/src/assets/hero.png') center / cover no-repeat;
  color: white;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.15);
}

.user-bar {
  position: absolute;
  top: 16px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #dbeafe;
  font-size: 13px;
}

.user-bar-copy {
  display: grid;
  gap: 2px;
  text-align: right;
}

.user-bar-copy small {
  color: #bfdbfe;
  font-size: 12px;
}

.user-bar button {
  padding: 8px 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  transition: all 0.25s ease;
}

.user-bar button:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.32);
  transform: translateY(-1px);
}

.header h1 {
  margin: 10px 0 0;
  color: #ffffff;
  font-size: clamp(26px, 3vw, 36px);
  font-weight: 700;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.system-name {
  margin: 0;
  color: #a5f3fc;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.main-nav {
  width: min(820px, 100%);
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 6px;
  margin: 24px auto 0;
  padding: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.main-nav button {
  min-width: 0;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 8px 10px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: #dbeafe;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.25s ease;
}

.main-nav button:hover:not(:disabled):not(.active) {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.main-nav button span {
  display: inline-grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.16);
  font-size: 13px;
  line-height: 1;
  transition: all 0.25s ease;
}

.main-nav button.active {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  color: #4f46e5;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  transform: translateY(-1px);
}

.main-nav button.active span {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
}

.main-nav button:disabled {
  background: transparent;
  color: rgba(219, 234, 254, 0.4);
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
  min-width: 80px;
  padding: 9px 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  transition: all 0.25s ease;
}

.page-actions button:hover,
.user-bar button:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.32);
  transform: translateY(-1px);
}

.container {
  max-width: min(1480px, calc(100vw - 48px));
  margin: 24px auto;
  padding: 0 0 40px;
}

.home-page {
  display: grid;
  gap: 18px;
}

.welcome-band {
  position: relative;
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

.welcome-band::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(115deg, rgba(255, 255, 255, 0.18), transparent 26%),
    radial-gradient(circle at 18% 34%, rgba(251, 191, 36, 0.18), transparent 32%);
  opacity: 0.72;
  pointer-events: none;
}

.welcome-copy {
  position: relative;
  z-index: 1;
  max-width: 680px;
}

.welcome-eyebrow {
  display: inline-flex;
  margin-bottom: 12px;
  color: #bfdbfe;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0;
  animation: hero-reveal 0.85s ease forwards;
}

.welcome-band h2 {
  max-width: 620px;
  margin: 0;
  color: #ffffff;
  font-size: clamp(48px, 6vw, 86px);
  font-weight: 500;
  line-height: 1.08;
}

.welcome-band h2 span {
  display: block;
  opacity: 0;
  transform: translateY(32px);
  animation: hero-reveal 0.95s cubic-bezier(0.21, 0.8, 0.24, 1) forwards;
}

.welcome-band h2 span:nth-child(1) {
  animation-delay: 0.16s;
}

.welcome-band h2 span:nth-child(2) {
  animation-delay: 0.32s;
}

.welcome-band h2 span:nth-child(3) {
  animation-delay: 0.48s;
}

.welcome-lead {
  max-width: 660px;
  margin: 26px 0 34px;
  color: #e0f2fe;
  font-size: 22px;
  line-height: 1.8;
  opacity: 0;
  transform: translateY(24px);
  animation: hero-reveal 0.9s ease 0.62s forwards;
}

.welcome-actions {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 16px;
  opacity: 0;
  transform: translateY(24px);
  animation: hero-reveal 0.9s ease 0.78s forwards;
}

.hero-action {
  position: relative;
  min-width: 220px;
  min-height: 72px;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  overflow: hidden;
  padding: 18px 28px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 800;
  isolation: isolate;
}

.hero-action::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.22), transparent);
  transform: translateX(-120%);
  transition: transform 0.45s ease;
}

.hero-action:hover::before {
  transform: translateX(120%);
}

.hero-action:not(:disabled):hover {
  transform: translateY(-4px);
}

.primary-action {
  background: linear-gradient(90deg, #2563eb, #c78311);
  box-shadow: 0 18px 34px rgba(2, 6, 23, 0.3);
}

.secondary-button {
  border: 3px solid rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.22);
  color: #ffffff;
}

.action-label,
.action-arrow {
  position: relative;
  z-index: 1;
}

.action-arrow {
  display: inline-grid;
  place-items: center;
  min-width: 48px;
  font-size: 34px;
  line-height: 1;
  transition: transform 0.22s ease;
}

.hero-action:hover .action-arrow {
  transform: translateX(8px);
}

.cvat-showcase {
  position: relative;
  z-index: 1;
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

@keyframes hero-reveal {
  from {
    opacity: 0;
    transform: translateY(36px);
    filter: blur(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

@keyframes meter-rise {
  0%,
  100% {
    opacity: 0.9;
  }
  50% {
    opacity: 1;
  }
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.status-grid article,
.account-panel {
  min-width: 0;
  display: grid;
  gap: 8px;
  padding: 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(226, 232, 240, 0.8);
  text-align: left;
  transition: all 0.3s ease;
}

.status-grid article:hover,
.account-panel:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
}

.status-grid span,
.account-panel span {
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.status-grid strong,
.account-panel strong {
  min-height: 28px;
  color: #0f172a;
  font-size: 22px;
  line-height: 1.15;
  word-break: break-word;
}

.status-grid small,
.account-panel small {
  overflow: hidden;
  color: #64748b;
  font-size: 12px;
  line-height: 1.55;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-grid .stat-success,
.status-grid .risk-normal,
.account-panel .stat-success {
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

.workflow-card,
.card {
  padding: 24px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.1), 0 2px 4px rgba(15, 23, 42, 0.06);
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 14px;
  text-align: left;
}

.section-heading h2,
.section-heading h3 {
  margin: 0;
  color: #111827;
}

.section-heading p {
  max-width: 760px;
  margin: 0;
  color: #64748b;
  line-height: 1.6;
  font-size: 14px;
}

.section-heading h2 {
  color: #1e1b4b;
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-heading h2::before {
  content: "";
  display: block;
  width: 4px;
  height: 22px;
  background: linear-gradient(180deg, #6366f1, #8b5cf6);
  border-radius: 4px;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
}

.workflow-steps article {
  position: relative;
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  column-gap: 12px;
  align-items: start;
  min-height: 0;
  padding: 20px;
  border-right: 1px solid #f1f5f9;
  text-align: left;
  transition: background 0.25s ease;
}

.workflow-steps article:hover {
  background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
}

.workflow-steps article:last-child {
  border-right: none;
}

.workflow-steps span {
  display: inline-grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.workflow-steps h3 {
  margin: 0 0 6px;
  color: #1e1b4b;
  font-size: 15px;
  font-weight: 700;
}

.workflow-steps p {
  grid-column: 2;
  margin: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.account-actions {
  margin-top: 18px;
}

.upgrade-button {
  background: #c05621;
}

.account-note {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.quota-chip {
  display: inline-grid;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eff6ff;
  color: #1d4ed8;
  text-align: right;
}

.quota-chip span {
  font-size: 12px;
  font-weight: 800;
}

.quota-chip strong {
  font-size: 20px;
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
  gap: 6px;
  overflow-x: auto;
  padding: 4px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 12px;
}

.page-tabs button {
  flex: 0 0 auto;
  min-width: 100px;
  min-height: 38px;
  padding: 8px 16px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.25s ease;
}

.page-tabs button:hover:not(.active) {
  background: rgba(255, 255, 255, 0.8);
  color: #1e293b;
}

.page-tabs button.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.export-button {
  flex: 0 0 auto;
  min-height: 40px;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  font-weight: 700;
  font-size: 13px;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  transition: all 0.25s ease;
}

.export-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
}

.export-status {
  margin: -6px 0 14px;
  text-align: right;
  font-size: 13px;
}

.tab-stack {
  display: block;
}

.media-type-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.media-type-selector label {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s ease;
}

.media-type-selector label:hover {
  border-color: #c7d2fe;
  background: #f1f5f9;
}

.media-type-selector label.active {
  border-color: #6366f1;
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.media-type-selector label input {
  display: none;
}

.media-type-icon {
  font-size: 24px;
}

.media-type-label {
  font-weight: 600;
  color: #334155;
}

.media-type-selector label.active .media-type-label {
  color: #4338ca;
}

.dropzone {
  display: grid;
  place-items: center;
  min-height: 200px;
  border: 2px dashed #c7d2fe;
  border-radius: 16px;
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  text-align: center;
  transition: all 0.3s ease;
}

.dropzone.dragging {
  border-color: #6366f1;
  background: linear-gradient(135deg, #e0e7ff 0%, #ede9fe 100%);
  box-shadow: 0 14px 30px rgba(99, 102, 241, 0.2);
  transform: translateY(-2px) scale(1.01);
}

.dropzone.ready {
  border-color: #818cf8;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: inset 0 2px 8px rgba(99, 102, 241, 0.08);
}

.dropzone-picker {
  position: relative;
  width: 100%;
  min-height: 200px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
  padding: 32px;
  color: #4f46e5;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.dropzone-picker:hover {
  transform: scale(1.02);
}

.dropzone-icon {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  font-size: 28px;
  line-height: 1;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.dropzone-picker:hover .dropzone-icon {
  transform: translateY(-4px) rotate(5deg);
  box-shadow: 0 12px 28px rgba(99, 102, 241, 0.45);
}

.dropzone-picker strong {
  max-width: min(560px, 100%);
  overflow: hidden;
  color: #1e1b4b;
  font-size: 18px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropzone-picker small {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
}

.dropzone-picker input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.upload-actions button {
  padding: 14px 40px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
}

.upload-actions button:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.45);
}

.upload-actions button:active:not(:disabled) {
  transform: translateY(-1px);
}

.upload-actions button:disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  cursor: not-allowed;
  box-shadow: none;
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

.selected-file-list li button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
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
  margin-top: 20px;
  padding: 18px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  text-align: left;
}

.mode-copy {
  min-width: 0;
  display: grid;
  gap: 6px;
}

.mode-copy span {
  color: #6366f1;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.mode-copy strong {
  color: #1e1b4b;
  font-size: 16px;
  font-weight: 700;
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
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
}

.mode-selector label {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 84px;
  padding: 9px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.mode-selector label:hover:not(.active) {
  background: rgba(99, 102, 241, 0.08);
}

.mode-selector label.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.35);
}

.mode-selector input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.mode-selector span {
  color: #475569;
  font-size: 13px;
  font-weight: 700;
  transition: color 0.25s ease;
}

.mode-selector label.active span {
  color: #ffffff;
}

button {
  border: none;
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
  color: white;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

button:disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
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

.preview-carousel img,
.preview-carousel video,
.image-panel img {
  max-width: 100%;
  border-radius: 8px;
}

.preview-carousel {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
  touch-action: pan-y;
  user-select: none;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.15);
}

.preview-carousel img,
.preview-carousel video {
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

.preview-strip img,
.preview-strip video {
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

/* 视频播放器样式 */
.preview-media {
  width: 100%;
  max-height: 520px;
  object-fit: contain;
  border-radius: 12px;
  background: #0f172a;
}

.preview-media::-webkit-media-controls-panel {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.7), transparent);
}

.strip-media {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: none;
  border-radius: 6px;
  transition: transform 0.2s ease, filter 0.2s ease;
}

.preview-strip button:hover .strip-media {
  transform: scale(1.05);
  filter: brightness(1.1);
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
.batch-result-list small,
.batch-card-copy strong,
.batch-card-copy small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.video-sampling-panel,
.video-consensus-panel,
.video-consensus-card,
.quota-admin-panel {
  margin-top: 16px;
  padding: 14px 16px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #f8fafc;
}

.metric-grid,
.recommendation-grid,
.grid {
  display: grid;
  gap: 10px;
}

.frame-preview-grid {
  overflow-x: auto;
  margin-top: 12px;
}

.consensus-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.consensus-stat {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value .unit {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 400;
  margin-left: 2px;
}

.consensus-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.tag-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.tag-item {
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.tag-empty {
  color: #94a3b8;
  font-size: 13px;
}

.consensus-votes {
  display: flex;
  gap: 20px;
  margin-top: 12px;
  font-size: 13px;
  color: #475569;
}

.consensus-votes strong {
  color: #1e293b;
}

.temporal-reason {
  margin-top: 8px;
  padding: 8px 10px;
  background: #fef9c3;
  border-left: 3px solid #ca8a04;
  border-radius: 4px;
  font-size: 13px;
  color: #713f12;
}

.temporal-analysis-box {
  margin-top: 12px;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.temporal-analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.temporal-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.temporal-suggestion {
  margin-top: 6px;
  font-size: 13px;
  color: #475569;
}

.temporal-details {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.detail-tag.danger {
  background: #fee2e2;
  color: #dc2626;
}

.detail-tag.warning {
  background: #fef3c7;
  color: #d97706;
}

.detail-tag.normal {
  background: #dcfce7;
  color: #16a34a;
}

/* 移除了重复的 .video-consensus-grid div 样式，已整合到上方 */

.metric-item {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
}

.result-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
  align-items: stretch;
}

.image-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: linear-gradient(160deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 20px 22px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  min-height: 0;
  overflow: hidden;
  max-height: calc(100vh - 240px);
  position: relative;
}

.image-panel h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  flex-shrink: 0;
  padding-top: 2px;
}

.image-panel .image-detail-trigger {
  border: none;
  padding: 0;
  background: transparent;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.1);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  flex: 1;
  display: flex;
  align-items: flex-start;
  min-height: 0;
}

.image-panel .image-detail-trigger:hover {
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.18);
  transform: translateY(-1px);
}

.image-panel .image-detail-trigger img {
  width: 100%;
  height: 100%;
  max-height: none;
  object-fit: contain;
  display: block;
  border-radius: 12px;
}

.image-panel .image-detail-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(15, 23, 42, 0.75);
  color: #ffffff;
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 20px;
  backdrop-filter: blur(8px);
  font-weight: 600;
  pointer-events: none;
}

.summary-panel {
  background: linear-gradient(160deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  max-height: calc(100vh - 240px);
  align-self: stretch;
}

.summary-panel > *:not(.summary-panel-inner) {
  flex-shrink: 0;
}

.summary-panel-inner {
  flex: 1;
  overflow-y: auto;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.45) rgba(226, 232, 240, 0.5);
  padding: 0;
}

.summary-panel-inner::-webkit-scrollbar {
  width: 7px;
}

.summary-panel-inner::-webkit-scrollbar-track {
  background: rgba(226, 232, 240, 0.3);
  border-radius: 4px;
}

.summary-panel-inner::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 4px;
}

.summary-panel .panel-section {
  padding: 0 24px;
}

.summary-panel .panel-section:first-child {
  padding-top: 20px;
}

.summary-panel .panel-section h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
  position: sticky;
  top: 0;
  background: linear-gradient(160deg, #ffffff 0%, #f8fafc 100%);
  padding: 12px 0 10px;
  z-index: 2;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 12px;
}

.summary-panel .panel-section h3::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, #6366f1, #8b5cf6);
  border-radius: 2px;
  flex-shrink: 0;
}

.summary-panel .panel-section p {
  margin: 0 0 10px;
  font-size: 13.5px;
  color: #475569;
  line-height: 1.7;
  word-break: break-all;
}

.summary-panel .panel-section p:last-child {
  margin-bottom: 0;
}

.summary-panel .panel-section p strong {
  color: #1e293b;
  font-weight: 600;
}

.frame-preview-grid {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
}

.frame-preview-grid h4 {
  margin: 0 0 12px;
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.frames-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  overflow-x: auto;
  display: block;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.frames-table-header {
  display: grid;
  grid-template-columns: 60px 70px 90px 70px 70px;
  gap: 8px;
  padding: 10px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
  text-align: left;
  min-width: 400px;
  border-radius: 8px 8px 0 0;
}

.frames-table-row {
  display: grid;
  grid-template-columns: 60px 70px 90px 70px 70px;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s ease;
  align-items: center;
  min-width: 400px;
}

.frames-table-row:last-child {
  border-bottom: none;
}

.frames-table-row:hover {
  background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);
}

.frames-table-row.selected {
  background: linear-gradient(90deg, #eff6ff 0%, #dbeafe 100%);
  border-left: 3px solid #667eea;
}

.frames-table-row.best-in-attempt {
  font-weight: 500;
  background: #fafafa;
}

.frame-num {
  font-family: monospace;
  color: #6366f1;
  font-weight: 600;
}

.quality-high {
  color: #16a34a;
  font-weight: 600;
}

.quality-medium {
  color: #ca8a04;
  font-weight: 500;
}

.quality-low {
  color: #dc2626;
}

.risk-高风险 {
  color: #dc2626;
  font-weight: 600;
}

.risk-中风险 {
  color: #ca8a04;
  font-weight: 500;
}

.risk-低风险 {
  color: #16a34a;
}

.risk-正常 {
  color: #64748b;
}

.frame-attempt-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 12px;
}

.attempt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
}

.attempt-meta {
  color: #64748b;
  font-size: 12px;
}

.attempt-frames {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.frame-thumb {
  position: relative;
  width: 80px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.frame-thumb:hover {
  border-color: #6366f1;
  transform: scale(1.05);
}

.frame-thumb.active {
  border-color: #22c55e;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.3);
}

.frame-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.frame-thumb .frame-index {
  position: absolute;
  bottom: 2px;
  left: 2px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
}

.frame-thumb .frame-quality {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(0, 0, 0, 0.6);
  color: #fbbf24;
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
}

.summary-panel .panel-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  margin: 16px 24px;
  flex-shrink: 0;
}

.report {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  border-left: 4px solid #6366f1;
  padding: 16px 18px;
  border-radius: 12px;
  line-height: 1.8;
  color: #1e293b;
  font-size: 14px;
  box-shadow: inset 0 2px 4px rgba(99, 102, 241, 0.05);
}

.log-card,
.user-admin-card {
  text-align: left;
}

.user-create-form,
.quota-adjust-form {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  align-items: end;
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}

.account-section {
  margin-top: 24px;
  padding: 22px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.account-section .section-heading {
  margin-bottom: 16px;
}

.password-form {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: end;
  margin-top: 4px;
}

.password-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.password-form input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  font-size: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.password-form input:hover {
  border-color: #94a3b8;
}

.password-form input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.password-form .form-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  grid-column: 1 / -1;
  justify-content: flex-end;
}

.password-form .form-actions button {
  padding: 9px 18px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(99, 102, 241, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.password-form .form-actions button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(99, 102, 241, 0.4);
}

.password-form .form-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.password-form .form-actions .ghost-button {
  background: transparent;
  color: #475569;
  border: 1px solid #cbd5e1;
  box-shadow: none;
}

.password-form .form-actions .ghost-button:hover:not(:disabled) {
  background: #f1f5f9;
  color: #1e293b;
  box-shadow: none;
}

.password-form .error,
.password-form .success-message {
  grid-column: 1 / -1;
  margin: 0;
}

.admin-password-dialog {
  max-width: 460px;
  width: 100%;
}

.admin-password-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 28px 32px 32px;
}

.admin-password-content h3 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
}

.admin-password-content p {
  margin: 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
}

.admin-password-content .password-form {
  grid-template-columns: 1fr;
}

@media (max-width: 720px) {
  .password-form {
    grid-template-columns: 1fr;
  }
  .admin-password-content {
    padding: 24px;
  }
}

.quota-adjust-form {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.quota-adjust-actions,
.table-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-create-form button,
.user-table button,
.quota-adjust-actions button {
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.user-create-form button:hover:not(:disabled),
.user-table button:hover:not(:disabled),
.quota-adjust-actions button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.secondary-table-button {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%) !important;
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.3) !important;
}

.secondary-table-button:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(100, 116, 139, 0.4) !important;
}

.danger-table-button {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3) !important;
}

.danger-table-button:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(220, 38, 38, 0.45) !important;
}

.success-message {
  color: #047857;
  font-weight: 700;
  padding: 10px 16px;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-radius: 10px;
  border-left: 4px solid #10b981;
}

.user-table {
  margin-top: 20px;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
}

.user-table th {
  padding: 14px 16px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: #f8fafc;
  font-weight: 700;
  text-align: left;
  font-size: 13px;
  letter-spacing: 0.02em;
}

.user-table td {
  padding: 14px 16px;
  background: #ffffff;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.2s ease;
}

.user-table tr:hover td {
  background: #f8fafc;
}

.user-table tr:last-child td {
  border-bottom: none;
}

.log-list {
  display: grid;
  gap: 16px;
}

.log-item {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  transition: all 0.25s ease;
}

.log-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  border-color: #c7d2fe;
}

.log-main {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.log-main img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
  transition: all 0.25s ease;
}

.log-main img:hover {
  transform: scale(1.03);
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12);
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

.image-detail-modal {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  animation: modal-fade-in 0.25s ease;
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.image-detail-dialog {
  width: min(1320px, 100%);
  max-height: min(860px, calc(100vh - 48px));
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  overflow: hidden;
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 25px 80px rgba(15, 23, 42, 0.4);
  animation: modal-zoom-in 0.3s cubic-bezier(0.21, 0.8, 0.24, 1);
}

@keyframes modal-zoom-in {
  from {
    transform: scale(0.92);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.image-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.image-detail-header span {
  color: #6366f1;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.image-detail-header h2 {
  margin: 4px 0 0;
  color: #1e1b4b;
  font-size: 20px;
  font-weight: 700;
}

.image-detail-close {
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #475569;
  font-size: 26px;
  line-height: 1;
  transition: all 0.25s ease;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
}

.image-detail-close:hover {
  background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
  color: #991b1b;
  transform: rotate(90deg);
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
  padding: 20px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.image-detail-viewer img {
  max-width: 100%;
  max-height: 76vh;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.image-detail-info {
  min-height: 0;
  overflow: auto;
  padding: 20px;
  border-left: 1px solid #e2e8f0;
  background: #f8fafc;
}

.image-detail-info h3 {
  color: #1e1b4b;
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #6366f1;
  display: inline-block;
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
  gap: 4px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #ffffff;
  transition: all 0.25s ease;
}

.detail-detection-list li:hover {
  border-color: #c7d2fe;
  background: linear-gradient(135deg, #ffffff 0%, #eef2ff 100%);
  transform: translateX(2px);
}

.detail-detection-list li strong {
  color: #1e1b4b;
  font-size: 14px;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.section-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.score-card {
  min-width: 120px;
  padding: 14px 18px;
  border-radius: 14px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.score-card span {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
  opacity: 0.95;
}

.score-card strong {
  font-size: 30px;
  line-height: 1;
  font-weight: 800;
}

.risk-normal {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
}

.risk-low {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.risk-medium {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
  color: #9a3412;
}

.risk-high {
  background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
  color: #991b1b;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.scene-tag {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #5b21b6;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #c4b5fd;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.1);
}

.metric-grid {
  grid-template-columns: repeat(4, 1fr);
  margin-bottom: 20px;
  gap: 14px;
}

.metric-item {
  padding: 16px 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: all 0.25s ease;
}

.metric-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
}

.metric-item span {
  display: block;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.metric-item strong {
  color: #1e1b4b;
  font-size: 26px;
  font-weight: 800;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.module-card {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: all 0.25s ease;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.module-header h3 {
  margin: 0;
  color: #1e1b4b;
  font-size: 16px;
  font-weight: 700;
}

.module-reason,
.module-suggestion {
  margin: 0;
  line-height: 1.7;
  font-size: 14px;
  color: #1e293b;
}

.module-suggestion {
  color: #475569;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #e2e8f0;
}

.recommendation-summary {
  margin-bottom: 20px;
  padding: 18px 20px;
  border-left: 4px solid #6366f1;
  border-radius: 12px;
  background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06);
}

.recommendation-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 20px;
}

.recommendation-item {
  min-height: 130px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: all 0.25s ease;
}

.recommendation-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.recommendation-item h3 {
  margin: 0 0 10px;
  color: #1e1b4b;
  font-size: 16px;
  font-weight: 700;
}

.recommendation-item p {
  margin: 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.7;
}

.action-panel {
  padding: 18px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
}

.action-panel h3 {
  color: #1e1b4b;
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 12px;
}

.action-panel ol {
  margin: 0;
  padding-left: 20px;
  color: #475569;
  font-size: 14px;
  line-height: 1.8;
}

.action-panel li {
  margin-bottom: 6px;
}

.ratio-cell {
  display: grid;
  grid-template-columns: minmax(120px, 1fr) 60px;
  align-items: center;
  gap: 12px;
}

.ratio-bar {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.ratio-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  transition: width 0.6s ease;
}

.grid {
  grid-template-columns: 1fr 1fr;
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
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  font-weight: 700;
  color: #1e1b4b;
  text-align: left;
  padding: 12px 16px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  font-size: 14px;
  transition: background 0.2s ease;
}

tr:hover td {
  background: #f8fafc;
}

.empty {
  color: #6b7280;
  text-align: center;
  padding: 20px;
  font-size: 14px;
}

.error {
  color: #991b1b;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 10px;
  border-left: 4px solid #ef4444;
  font-size: 14px;
  font-weight: 500;
  margin: 12px 0;
}

.success {
  color: #065f46;
  padding: 12px 16px;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-radius: 10px;
  border-left: 4px solid #10b981;
  font-size: 14px;
  font-weight: 500;
  margin: 12px 0;
}

@media (max-width: 900px) {
  .login-panel,
  .result-layout,
  .compare-grid,
  .log-main,
  .grid,
  .module-grid,
  .metric-grid,
  .recommendation-grid,
  .status-grid,
  .account-grid,
  .workflow-steps,
  .user-create-form,
  .quota-adjust-form {
    grid-template-columns: 1fr;
  }

  .header {
    padding: 92px 16px 20px;
  }

  .page-actions {
    left: 18px;
    top: 18px;
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

  .image-detail-info {
    max-height: 260px;
    border-top: 1px solid #e5e7eb;
    border-left: 0;
  }

  .summary-panel {
    max-height: none;
    align-self: auto;
  }

  .summary-panel-inner {
    overflow-y: visible;
  }

  .image-panel {
    max-height: none;
    align-self: auto;
  }

  .image-panel .image-detail-trigger img {
    max-height: none;
    height: auto;
  }

  .welcome-band {
    grid-template-columns: 1fr;
    min-height: 300px;
    padding: 24px;
  }

  .main-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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

  .section-title,
  .section-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .user-bar {
    position: static;
    justify-content: center;
    margin-bottom: 18px;
    flex-direction: column;
  }

  .user-bar-copy {
    text-align: center;
  }
}
</style>
