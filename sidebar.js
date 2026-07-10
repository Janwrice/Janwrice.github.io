(function() {
    var posts = window.__POSTS__ || [];
    var base = window.location.pathname.includes('/posts/') ? '../' : '';

    var allList = document.getElementById('all-posts');
    var recentList = document.getElementById('recent-posts');

    if (allList) {
        posts.forEach(function(p) {
            var li = document.createElement('li');
            li.innerHTML = '<a href="' + base + p.url + '">' + p.title + '<span class="post-date">' + p.date + '</span></a>';
            allList.appendChild(li);
        });
    }

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
})();
