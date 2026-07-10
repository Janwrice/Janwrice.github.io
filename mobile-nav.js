(function () {
    // ── 创建汉堡菜单按钮 ──
    var hamburger = document.createElement('button');
    hamburger.className = 'hamburger-btn';
    hamburger.setAttribute('aria-label', '菜单');
    hamburger.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<line x1="3" y1="6" x2="21" y2="6"/>' +
        '<line x1="3" y1="12" x2="21" y2="12"/>' +
        '<line x1="3" y1="18" x2="21" y2="18"/>' +
        '</svg>';

    // 插入到 navbar-right 末尾（theme-toggle 之后）
    var navbarRight = document.querySelector('.navbar-right');
    if (navbarRight) navbarRight.appendChild(hamburger);

    // ── 创建遮罩层 ──
    var overlay = document.createElement('div');
    overlay.className = 'drawer-overlay';
    document.body.appendChild(overlay);

    // ── 创建抽屉 ──
    var drawer = document.createElement('aside');
    drawer.className = 'drawer';
    drawer.innerHTML =
        '<button class="drawer-close" aria-label="关闭">&times;</button>' +
        '<div class="drawer-content"></div>';
    document.body.appendChild(drawer);

    var drawerContent = drawer.querySelector('.drawer-content');
    var closeBtn = drawer.querySelector('.drawer-close');
    var isOpen = false;
    var populated = false;

    function openDrawer() {
        if (!populated) {
            var sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                var clone = sidebar.cloneNode(true);
                // 清除克隆元素中的 id，避免与页面原有 id 冲突
                var els = clone.querySelectorAll('[id]');
                for (var i = 0; i < els.length; i++) els[i].removeAttribute('id');
                drawerContent.appendChild(clone);
            }
            populated = true;
        }
        document.body.style.overflow = 'hidden';
        drawer.classList.add('open');
        overlay.classList.add('open');
        isOpen = true;
    }

    function closeDrawer() {
        drawer.classList.remove('open');
        overlay.classList.remove('open');
        isOpen = false;
        document.body.style.overflow = '';
    }

    // ── 桌面端 / 移动端行为分发 ──
    function isMobile() {
        return window.matchMedia('(max-width: 768px)').matches;
    }

    hamburger.addEventListener('click', function () {
        if (isMobile()) {
            openDrawer();
        } else {
            document.body.classList.toggle('sidebar-hidden');
        }
    });

    // 窗口缩放到移动端时，恢复 sidebar 显示（避免桌面隐藏后切移动端丢失）
    window.addEventListener('resize', function () {
        if (isMobile()) {
            document.body.classList.remove('sidebar-hidden');
        }
    });

    closeBtn.addEventListener('click', closeDrawer);
    overlay.addEventListener('click', closeDrawer);

    // ── 点击抽屉内链接 → 滚动到目标 + 关闭抽屉 ──
    drawer.addEventListener('click', function (e) {
        var a = e.target.closest('a');
        if (!a) return;
        var href = a.getAttribute('href');
        if (!href || href.charAt(0) !== '#') return;   // 只处理锚点链接（TOC）
        e.preventDefault();
        closeDrawer();
        var target = document.getElementById(href.slice(1));
        if (target) {
            // 短暂延迟等抽屉动画结束再滚动
            setTimeout(function () {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 320);
        }
    });
})();
