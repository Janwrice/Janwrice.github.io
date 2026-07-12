(function() {
    var posts = window.__POSTS__ || [];
    var base = window.location.pathname.includes('/posts/') ? '../' : '';

    var allList = document.getElementById('all-posts');
    var recentList = document.getElementById('recent-posts');
    var tagFilter = document.getElementById('tag-filter');

    var currentTag = null;

    // ── 收集所有标签 ──
    var tagSet = {};
    posts.forEach(function(p) {
        (p.tags || []).forEach(function(t) {
            tagSet[t] = (tagSet[t] || 0) + 1;
        });
    });

    // ── 渲染标签筛选按钮 ──
    if (tagFilter) {
        var tags = Object.keys(tagSet).sort();
        if (tags.length) {
            var html = '<button class="tag-btn active" data-tag="">全部</button>';
            tags.forEach(function(t) {
                html += '<button class="tag-btn" data-tag="' + t + '">' + t + '</button>';
            });
            tagFilter.innerHTML = html;

            // ── 折叠多余标签 ──
            var VISIBLE_COUNT = 6;
            if (tags.length > VISIBLE_COUNT) {
                var tagBtns = tagFilter.querySelectorAll('.tag-btn');
                tagBtns.forEach(function(btn, i) {
                    if (i > VISIBLE_COUNT) btn.classList.add('folded');
                });
                var toggle = document.createElement('button');
                toggle.className = 'tag-toggle';
                toggle.textContent = '更多标签 ▼';
                toggle.addEventListener('click', function() {
                    var expanded = tagFilter.classList.toggle('expanded');
                    toggle.textContent = expanded ? '收起 ▲' : '更多标签 ▼';
                });
                tagFilter.appendChild(toggle);
            }
        }
    }

    // ── 渲染全部文章列表 ──
    function renderAllPosts() {
        if (!allList) return;
        allList.innerHTML = '';
        posts.forEach(function(p) {
            var li = document.createElement('li');
            var match = !currentTag || (p.tags && p.tags.indexOf(currentTag) !== -1);
            if (!match) li.classList.add('hidden');
            li.innerHTML = '<a href="' + base + p.url + '">' + p.title + '<span class="post-date">' + p.date + '</span></a>';
            allList.appendChild(li);
        });
    }

    if (allList) {
        renderAllPosts();
    }

    // ── 渲染最近文章 ──
    if (recentList) {
        posts.slice(0, 5).forEach(function(p) {
            var li = document.createElement('li');
            li.innerHTML = '<a href="' + base + p.url + '">' + p.title + '<span class="post-date">' + p.date + '</span></a>';
            recentList.appendChild(li);
        });

        var more = document.createElement('a');
        more.className = 'sidebar-more';
        more.href = base + 'blog.html';
        more.innerHTML = '查看更多 &rarr;';
        recentList.parentNode.appendChild(more);
    }

    // ── 标签点击事件 ──
    if (tagFilter) {
        tagFilter.addEventListener('click', function(e) {
            if (e.target.classList.contains('tag-btn')) {
                currentTag = e.target.getAttribute('data-tag') || null;
                var btns = tagFilter.querySelectorAll('.tag-btn');
                btns.forEach(function(b) { b.classList.remove('active'); });
                e.target.classList.add('active');
                renderAllPosts();
            }
        });
    }
})();
