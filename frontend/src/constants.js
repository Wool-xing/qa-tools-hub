/** Central constants for QA通关 frontend.
 *  All magic strings, localStorage keys, and app-wide config live here.
 */

// ==================== localStorage Keys ====================
export const LS_TOKEN = 'qa-pro-token'
export const LS_LAB_VISITS = 'qa-lab-visits'
export const LS_LAB_COUNT = 'qa-lab-count'
export const LS_DARK_MODE = 'qa-dark-mode'
export const LS_ACHIEVEMENTS = 'qa-achievements'

// ==================== App Identity ====================
export const APP_NAME = 'QA通关'
export const APP_TITLE = 'QA通关 — 测试工程师学习平台'
export const APP_COPYRIGHT = 'QA通关 © 2026'

// ==================== API Base URL ====================
// Vite injects import.meta.env.VITE_API_BASE at build time.
// Falls back to '' (same-origin) for production deployments behind nginx.
export const API_BASE = import.meta.env.VITE_API_BASE || ''

// ==================== Timeouts (ms) ====================
export const TOAST_DURATION = 4000
export const TOAST_SHORT = 2000
export const COPY_FEEDBACK = 3000
export const REDIRECT_DELAY = 3000
export const HIGHLIGHT_DURATION = 1200
export const SEARCH_DEBOUNCE = 300
export const RETRY_DELAY_MS = 800

// ==================== Retry ====================
export const FETCH_MAX_RETRIES = 3

// ==================== UI Thresholds ====================
export const SCROLL_THRESHOLD = 400
export const MOBILE_BREAKPOINT = 768
export const SIDEBAR_WIDTH = 250
export const TEXT_PREVIEW_LENGTH = 120

// ==================== Validation ====================
export const TEAM_NAME_MIN = 2
export const TEAM_NAME_MAX = 50
export const INVITE_CODE_LEN = 8

// ==================== Score Thresholds ====================
export const PASS_SCORE = 70
export const PASSWORD_STRENGTH_MIN = 50

// ==================== Password Strength Weights ====================
export const PW_WEIGHT_LEN8 = 25
export const PW_WEIGHT_LEN12 = 15
export const PW_WEIGHT_LOWER = 15
export const PW_WEIGHT_UPPER = 15
export const PW_WEIGHT_DIGIT = 15
export const PW_WEIGHT_SPECIAL = 15

// ==================== Dashboard Milestones ====================
export const MILESTONE_STARTER = 8
export const MILESTONE_JOURNEYMAN = 23
export const MILESTONE_EXPERT = 35
export const MILESTONE_MASTER = 80
export const MILESTONE_ALL = 102

// ==================== Stage Ordering ====================
export const STAGE_ORDER = [
  'beginner', 'intermediate', 'web', 'api', 'mobile',
  'performance', 'security', 'network', 'ops', 'cicd',
  'automotive', 'accessibility', 'data', 'chaos', 'visual',
  'advanced', 'fintech',
]
