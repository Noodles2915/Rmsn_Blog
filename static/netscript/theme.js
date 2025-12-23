/**
 * 主题管理系统
 * 支持日间、夜间和自动模式
 */

class ThemeManager {
    constructor() {
        this.THEME_KEY = 'user-theme-preference';
        this.LIGHT = 'light';
        this.DARK = 'dark';
        this.AUTO = 'auto';
        
        this.init();
    }

    /**
     * 初始化主题系统
     */
    init() {
        // 先移除加载时可能产生的动画（防止闪烁），并在稍后恢复
        this._suppressTransitionsOnStart();

        // 获取用户首选项（优先 localStorage / cookie），如果没有则使用服务器设置的 data-theme 或系统偏好
        const savedPref = this.getSavedPreference();
        const initialActual = this.getInitialActualTheme();
        const preferredTheme = savedPref || initialActual || this.getSystemPreference();

        // 立即应用主题（同步），以减少加载时的闪烁
        this.applyThemeImmediately(preferredTheme);
        this.setupListeners();
        this.setupMediaQueryListener();
    }

    /**
     * 获取已保存的主题偏好
     */
    getSavedTheme() {
        // 保留兼容方法：此方法仍用于获取页面当前应用的主题（实际主题），
        // 但不要把页面的 data-theme 当作用户首选项。
        return document.documentElement.getAttribute('data-theme');
    }

    /**
     * 获取用户真实首选项（优先 localStorage，再检索 cookie）
     */
    getSavedPreference() {
        const ls = localStorage.getItem(this.THEME_KEY);
        if (ls && [this.LIGHT, this.DARK, this.AUTO].includes(ls)) return ls;
        const ck = this.getCookie(this.THEME_KEY);
        if (ck && [this.LIGHT, this.DARK, this.AUTO].includes(ck)) return ck;
        return null;
    }

    /**
     * 获取页面初始实际主题（由服务器可能注入的 data-theme）
     */
    getInitialActualTheme() {
        const htmlTheme = document.documentElement.getAttribute('data-theme');
        if (htmlTheme && [this.LIGHT, this.DARK].includes(htmlTheme)) return htmlTheme;
        return null;
    }

    /**
     * 获取系统偏好（自动模式）
     */
    getSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return this.DARK;
        }
        return this.LIGHT;
    }

    /**
     * 应用主题
     */
    setTheme(theme) {
        if (![this.LIGHT, this.DARK, this.AUTO].includes(theme)) {
            theme = this.AUTO;
        }
        // 确定实际应用的主题（自动模式需要解析系统偏好）并应用
        let actualTheme = theme === this.AUTO ? this.getSystemPreference() : theme;
        document.documentElement.setAttribute('data-theme', actualTheme);

        // 保存用户偏好到 localStorage 与 cookie（用于在 CSS 加载前恢复）
        try { localStorage.setItem(this.THEME_KEY, theme); } catch (e) {}
        this.setCookie(this.THEME_KEY, theme, 365);

        // 触发自定义事件，以便其他脚本可以监听
        window.dispatchEvent(new CustomEvent('theme-changed', {
            detail: { theme, actualTheme }
        }));

        // 恢复过渡样式（如果存在）在下一帧或稍后
        this._restoreTransitionsSoon();
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        // 切换基于用户首选项（而非页面当前应用主题）
        const currentPref = this.getSavedPreference() || this.AUTO;
        let next;
        switch (currentPref) {
            case this.LIGHT:
                next = this.DARK;
                break;
            case this.DARK:
                next = this.AUTO;
                break;
            case this.AUTO:
            default:
                next = this.LIGHT;
        }

        this.setTheme(next);
    }

    /**
     * 获取当前主题
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || this.LIGHT;
    }

    /**
     * 获取用户偏好（可能与实际应用的主题不同，如果是自动模式）
     */
    getUserPreference() {
        return this.getSavedPreference() || this.AUTO;
    }

    /**
     * 设置监听器
     */
    setupListeners() {
        // 查找所有主题切换按钮
        const toggleButtons = document.querySelectorAll('[data-toggle-theme]');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
                this.updateButtonStates();
                this.syncWithServer();
            });
        });

        // 更新按钮状态
        this.updateButtonStates();

        // 监听自定义事件
        window.addEventListener('theme-changed', () => {
            this.updateButtonStates();
        });
    }

    /**
     * 更新按钮状态
     */
    updateButtonStates() {
        const preference = this.getUserPreference();
        const buttons = document.querySelectorAll('[data-toggle-theme]');
        
        buttons.forEach(button => {
            const themeName = this.getThemeDisplayName(preference);
            const icon = this.getThemeIcon(preference);
            
            button.textContent = `${icon} ${themeName}`;
            button.setAttribute('aria-label', `切换主题：当前为${themeName}`);
        });
    }

    /**
     * 获取主题显示名称
     */
    getThemeDisplayName(theme) {
        const names = {
            [this.LIGHT]: '日间',
            [this.DARK]: '夜间',
            [this.AUTO]: '自动'
        };
        return names[theme] || '自动';
    }

    /**
     * 获取主题图标
     */
    getThemeIcon(theme) {
        const icons = {
            [this.LIGHT]: '☀️',
            [this.DARK]: '🌙',
            [this.AUTO]: '🔄'
        };
        return icons[theme] || '🔄';
    }

    /**
     * 监听系统偏好变化
     */
    setupMediaQueryListener() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            // 处理新版本 API
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', (e) => {
                    // 只在自动模式下重新应用主题
                    const preference = this.getUserPreference();
                    if (preference === this.AUTO) {
                        const newTheme = e.matches ? this.DARK : this.LIGHT;
                        document.documentElement.setAttribute('data-theme', newTheme);
                        window.dispatchEvent(new CustomEvent('theme-changed', {
                            detail: { theme: this.AUTO, actualTheme: newTheme }
                        }));
                    }
                });
            }
            // 处理旧版本 API（过时但仍保留）
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener((e) => {
                    const preference = this.getUserPreference();
                    if (preference === this.AUTO) {
                        const newTheme = e.matches ? this.DARK : this.LIGHT;
                        document.documentElement.setAttribute('data-theme', newTheme);
                    }
                });
            }
        }
    }

    /**
     * 与服务器同步主题偏好（可选）
     */
    syncWithServer() {
        const preference = this.getUserPreference();
        
        // 发送 AJAX 请求更新服务器
        fetch('/user/api/user/theme/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({ theme: preference })
        }).catch(error => {
            console.warn('Theme sync failed:', error);
            // 即使同步失败也不影响本地主题设置
        });
    }

    /**
     * 立即应用主题（在 init 时同步执行，以减少闪烁）
     */
    applyThemeImmediately(theme) {
        if (![this.LIGHT, this.DARK, this.AUTO].includes(theme)) theme = this.AUTO;
        const actual = theme === this.AUTO ? (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? this.DARK : this.LIGHT) : theme;
        document.documentElement.setAttribute('data-theme', actual);
        try { localStorage.setItem(this.THEME_KEY, theme); } catch (e) {}
        this.setCookie(this.THEME_KEY, theme, 365);
    }

    /**
     * 设置 cookie（用于在 CSS 前恢复偏好）
     */
    setCookie(name, value, days) {
        try {
            let expires = '';
            if (days) {
                const date = new Date();
                date.setTime(date.getTime() + (days*24*60*60*1000));
                expires = '; expires=' + date.toUTCString();
            }
            document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
        } catch (e) {}
    }

    /**
     * 读取 cookie
     */
    getCookie(name) {
        const nameEQ = name + '=';
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
        }
        return null;
    }

    /**
     * 在脚本加载时禁用过渡，防止初始闪烁，然后在设置完主题后恢复
     */
    _suppressTransitionsOnStart() {
        try {
            if (document.documentElement.classList.contains('theme-init-suppressed')) return;
            document.documentElement.classList.add('theme-init-suppressed');
            const style = document.createElement('style');
            style.id = 'theme-init-style';
            style.innerHTML = '.theme-init-suppressed * { transition: none !important; }';
            document.head && document.head.appendChild(style);
        } catch (e) {}
    }

    _restoreTransitionsSoon() {
        // 在下一帧或 80ms 后恢复（兼容不同浏览器）
        requestAnimationFrame(() => {
            setTimeout(() => {
                const style = document.getElementById('theme-init-style');
                if (style && style.parentNode) style.parentNode.removeChild(style);
                document.documentElement.classList.remove('theme-init-suppressed');
            }, 80);
        });
    }

    /**
     * 获取 CSRF Token
     */
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        
        return cookieValue || '';
    }
}

// 页面加载时初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}
