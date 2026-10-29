// Trang soát tay (P2R I5) - xem evaluation/spotcheck_page.py.
// Lưu kết quả chấm trong trình duyệt (localStorage, theo bản cây + seed); nút "Tải phiếu chấm"
// xuất CSV cùng dạng review.csv. Không cần mạng, không thư viện ngoài.
(() => {
  const meta = JSON.parse(document.getElementById('meta').textContent);
  const key = 'spotcheck:' + meta.book_id + ':' + meta.nodes_sha256 + ':' + meta.seed;
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem(key) || '{}');
  } catch (e) {
    saved = {};
  }
  const save = () => {
    try {
      localStorage.setItem(key, JSON.stringify(saved));
    } catch (e) {
      // trình duyệt chặn lưu: vẫn chấm được, chỉ không giữ khi tải lại trang
    }
  };
  const units = [...document.querySelectorAll('article.unit')].filter(
    (u) => u.querySelector('.review'),
  );

  const refresh = () => {
    let done = 0;
    for (const u of units) {
      const s = saved[u.dataset.unit] || {};
      const all = meta.criteria.every((c) => s[c] === '1');
      const bad = s.bad === true;
      u.classList.toggle('done', all);
      u.classList.toggle('bad', bad && !all);
      if (all || bad) done += 1;
    }
    document.getElementById('progress').textContent = done + '/' + units.length + ' đã chấm';
  };

  for (const u of units) {
    const s = saved[u.dataset.unit] || (saved[u.dataset.unit] = {});
    for (const el of u.querySelectorAll('[data-crit]')) {
      const c = el.dataset.crit;
      if (el.type === 'checkbox') el.checked = s[c] === '1';
      else el.value = s[c] || '';
      el.addEventListener('input', () => {
        s[c] = el.type === 'checkbox' ? (el.checked ? '1' : '0') : el.value;
        if (meta.criteria.every((x) => s[x] === '1')) s.bad = false;
        save();
        refresh();
      });
    }
    u.querySelector('.mark-bad').addEventListener('click', () => {
      s.bad = true;
      for (const c of meta.criteria) if (s[c] !== '1') s[c] = '0';
      save();
      refresh();
    });
  }

  // rê chuột lên một mục bên phải → ô chữ của mục đó bên trái nháy viền
  for (const part of document.querySelectorAll('.part')) {
    const boxes = () =>
      part.closest('article').querySelectorAll('.box[data-node="' + part.dataset.node + '"]');
    part.addEventListener('mouseenter', () => boxes().forEach((b) => b.classList.add('hl')));
    part.addEventListener('mouseleave', () => boxes().forEach((b) => b.classList.remove('hl')));
  }

  // phiếu chấm CSV: bệnh chưa đụng tới → ô trống (= chưa chấm); đã chấm → ô không tích = 0
  const cell = (v) => '"' + String(v ?? '').replace(/"/g, '""') + '"';
  document.getElementById('download').addEventListener('click', () => {
    const rows = [meta.columns.join(',')];
    for (const u of units) {
      const s = saved[u.dataset.unit] || {};
      const touched = s.bad || meta.criteria.some((c) => s[c] === '1');
      const row = {
        unit_id: u.dataset.unit,
        code: u.dataset.code,
        title: u.dataset.title,
        pdf_pages: u.dataset.pages,
        note: s.note || '',
      };
      for (const c of meta.criteria) row[c] = touched ? (s[c] === '1' ? '1' : '0') : '';
      rows.push(meta.columns.map((c) => cell(row[c])).join(','));
    }
    const text = '﻿' + rows.join('\r\n') + '\r\n';
    const blob = new Blob([text], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'review_' + meta.book_id + '.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  });

  refresh();
})();
