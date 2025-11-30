<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Admin · G School</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <style>
    body { max-width:1200px; margin:auto; padding:1rem }
    body, label, h3, h4, .mini, button, .btn { color:#000 !important; }
    table { width:100%; border-collapse:collapse; margin-top:10px }
    th, td { border:1px solid #ccc; padding:6px; text-align:left }
    td input[type="url"] { width:100% }
    .mini { font-size: 0.85rem; color:#444; }
    .flex-row { display:flex; flex-wrap:wrap; gap:1rem; align-items:flex-start; }
    .flex-1 { flex:1; min-width:260px; }
    .flex-2 { flex:2; min-width:320px; }
    .pill { display:inline-block; padding:2px 6px; border-radius:999px; background:#eef; font-size:0.8rem; margin-right:4px; }
    .pill-danger { background:#fee; color:#900; }
    .pill-ok { background:#e6ffed; color:#065f46; }
    .pill-muted { background:#f3f4f6; color:#374151; }
    .badge { display:inline-block; padding:1px 6px; border-radius:999px; font-size:0.75rem; background:#eee; margin-left:4px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:0.5rem 1rem; }
  </style>
</head>
<body>
<nav>
  <ul><li><strong>Admin</strong></li></ul>
  <ul><li><a href="/teacher">Teacher</a></li><li><a href="/logout">Logout</a></li></ul>
</nav>

<h3>Settings</h3>
<article>
  <label>Default Blocked Redirect URL 
    <input id="blocked" type="url" value="{{ data.settings.blocked_redirect|default('https://blocked.gdistrict.org/Gschool%20block') }}">
  </label>
  <label>
    <input id="chat" type="checkbox" {{ 'checked' if data.settings.chat_enabled|default(False) else '' }}>
    Enable Chat
  </label>
  <label>Extension Passcode
    <input id="passcode" type="password" placeholder="admin1234">
  </label>
  <label>
    <input id="bypassEnabled" type="checkbox" {{ 'checked' if data.settings.bypass_enabled|default(False) else '' }}>
    Enable Bypass Override on Block Pages
  </label>
  <label>Bypass Code
    <input id="bypassCode" type="password" value="{{ data.settings.bypass_code|default('') }}" placeholder="e.g. secret123">
  </label>
  <label>Bypass Duration (minutes)
    <input id="bypassTTL" type="number" min="1" max="1440" value="{{ data.settings.bypass_ttl_minutes|default(10) }}">
  </label>
  <button id="save">Save Settings</button>
  <small id="saveMsg" class="mini"></small>
</article>

<h3>Policies</h3>
<article>
  <!-- existing policies UI unchanged -->
  <!-- ... all your original policy HTML here ... -->

  <div class="flex-row">
    <div class="flex-1">
      <h4>Existing Policies</h4>
      <ul id="policiesList"></ul>
      <button id="newPolicyBtn" class="secondary">New Policy</button>
      <button id="deletePolicyBtn" class="secondary" style="background:#fee2e2;border-color:#fecaca;">Delete Selected</button>
      <p class="mini">
        Click a policy to edit. “(default)” means it’s the default when a student has no other policy.
      </p>
    </div>

    <!-- Policy editor -->
    <div class="flex-2">
      <h4>Edit Policy</h4>
      <!-- ... rest of existing policy editor ... -->
      <label>Student Emails (one per line)
        <textarea id="policyEmails" rows="4" placeholder="student1@example.com&#10;student2@example.com"></textarea>
      </label>

      <button id="savePolicyBtn">Save Policy</button>
      <small id="policiesMsg" class="mini" style="margin-left:8px;"></small>
    </div>
  </div>
</article>


<h3>AI Image Filter</h3>
<article>
  <details open>
    <summary>Realtime Image Safety Filter</summary>
    <p class="mini">
      The AI image filter runs inside the browser extension and calls the server
      in realtime to classify images on any website. Blocked images are blurred
      and replaced with a lock icon before students can see them.
    </p>

    <div class="grid">
      <label>
        <input id="imgFilterEnabled" type="checkbox">
        Enable AI image filter for students
      </label>

      <label>
        Mode
        <select id="imgFilterMode">
          <option value="block">Block &amp; blur images above threshold</option>
          <option value="monitor">Monitor only (log events, do not blur)</option>
        </select>
        <small class="mini">
          Monitor mode is useful for testing – you can see what <em>would</em> be blocked
          without affecting students.
        </small>
      </label>

      <label>
        Block threshold (0.1 – 0.99)
        <input id="imgFilterThreshold" type="number" step="0.01" min="0.1" max="0.99" value="0.60">
        <small class="mini">
          Lower = stricter (more images blocked). Higher = looser (fewer blocked).
        </small>
      </label>

      <label>
        <input id="imgFilterAlertOnBlock" type="checkbox" checked>
        Create an alert whenever an image is blocked
      </label>

      <label>
        Max events kept in log
        <input id="imgFilterMaxLog" type="number" min="100" max="5000" value="500">
        <small class="mini">
          Older events are automatically dropped when this limit is reached.
        </small>
      </label>
    </div>

    <button id="imgFilterSaveBtn" class="contrast" style="margin-top:0.5rem;">Save Image Filter Settings</button>
    <small id="imgFilterMsg" class="mini" style="margin-left:0.5rem;"></small>

    <hr>

    <h4>Recent Image Filter Events</h4>
    <p class="mini">
      These are the most recent images that the AI filter has evaluated and either blocked
      or monitored. New events automatically appear here in realtime while this page is open.
    </p>
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Student</th>
          <th>Action</th>
          <th>Reason</th>
          <th>Score</th>
          <th>Page / Image</th>
        </tr>
      </thead>
      <tbody id="imgFilterEventsBody">
      </tbody>
    </table>
  </details>
</article>

<!-- SIMPLE USER MANAGEMENT (no student stuff here) -->
<h3>Users</h3>
<article>
  <details open>
    <summary>Admin &amp; Teacher Accounts</summary>
    <p class="mini">
      Create / update / delete sign-in accounts for the teacher and admin dashboards.
      These accounts <b>do not</b> affect student extension logins.
    </p>

    <!-- Create / Update -->
    <h4>Create or Update User</h4>
    <label>Email
      <input type="email" id="userEmail" placeholder="teacher@example.com">
    </label>
    <label>Password
      <input type="password" id="userPassword" placeholder="Set or reset password">
    </label>
    <label>Role
      <select id="userRole">
        <option value="teacher">Teacher</option>
        <option value="admin">Admin</option>
      </select>
    </label>
    <button id="saveUser">Save User</button>
    <p id="userMsg" class="mini"></p>

    <hr>

    <!-- Delete -->
    <h4>Delete User</h4>
    <label>Email
      <input type="email" id="deleteEmail" placeholder="teacher@example.com">
    </label>
    <button id="deleteUser" class="secondary">Delete User</button>
    <p id="deleteMsg" class="mini"></p>
  </details>
</article>

<script>
  // ============ Settings ============
  document.getElementById('save').onclick = async () => {
    const body = {
      blocked_redirect: document.getElementById('blocked').value,
      chat_enabled: document.getElementById('chat').checked,
      passcode: document.getElementById('passcode').value,
      bypass_enabled: document.getElementById('bypassEnabled').checked,
      bypass_code: document.getElementById('bypassCode').value,
      bypass_ttl_minutes: parseInt(document.getElementById('bypassTTL').value || '10', 10)
    };
    try {
      const r = await fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      });
      const msg = document.getElementById('saveMsg');
      if (r.ok) {
        msg.textContent = 'Saved.';
        msg.style.color = 'green';
      } else {
        const t = await r.text();
        msg.textContent = 'Error: ' + t;
        msg.style.color = 'crimson';
      }
    } catch (e) {
      const msg = document.getElementById('saveMsg');
      msg.textContent = 'Error: ' + e;
      msg.style.color = 'crimson';
    }
  };

  // ============ Users ============
  document.getElementById('saveUser').onclick = async () => {
    const email = document.getElementById('userEmail').value.trim();
    const password = document.getElementById('userPassword').value;
    const role = document.getElementById('userRole').value;
    const msgEl = document.getElementById('userMsg');

    msgEl.textContent = '';
    msgEl.style.color = '#444';

    if (!email || !password) {
      msgEl.textContent = 'Email and password required';
      msgEl.style.color = 'crimson';
      return;
    }

    const r = await fetch('/api/users', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email, password, role })
    });

    if (r.ok) {
      msgEl.textContent = 'User saved';
      msgEl.style.color = 'green';
      document.getElementById('userPassword').value = '';
    } else {
      const t = await r.text();
      msgEl.textContent = 'Error: ' + t;
      msgEl.style.color = 'crimson';
    }
  };

  document.getElementById('deleteUser').onclick = async () => {
    const email = document.getElementById('deleteEmail').value.trim();
    const msgEl = document.getElementById('deleteMsg');
    msgEl.textContent = '';
    msgEl.style.color = '#444';

    if (!email) {
      msgEl.textContent = 'Email required';
      msgEl.style.color = 'crimson';
      return;
    }

    const r = await fetch('/api/users', {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email })
    });

    if (r.ok) {
      msgEl.textContent = 'User deleted';
      msgEl.style.color = 'green';
    } else {
      const t = await r.text();
      msgEl.textContent = 'Error: ' + t;
      msgEl.style.color = 'crimson';
    }
  };

  // ... existing AI categories / policy JS unchanged above ...

  (async()=>{
    // existing initialization for AI categories + policies
    await loadAiCategories();
    await loadPoliciesUI();

    const saveBtn = document.getElementById('savePolicyBtn');
    const newBtn = document.getElementById('newPolicyBtn');
    const delBtn = document.getElementById('deletePolicyBtn');

    if (saveBtn) saveBtn.onclick = (ev)=>{ ev.preventDefault(); saveCurrentPolicy(); };
    if (newBtn) newBtn.onclick = (ev)=>{ ev.preventDefault(); fillPolicyForm(null); };
    if (delBtn) delBtn.onclick = (ev)=>{ ev.preventDefault(); deleteCurrentPolicy(); };
  })();

  // ============ AI Image Filter (admin controls) ============
  let IMG_FILTER_CFG = null;
  let IMG_FILTER_EVENTS = [];
  let IMG_FILTER_POLL_TIMER = null;

  async function loadImageFilterConfig() {
    try {
      const r = await fetch('/api/image_filter/config');
      if (!r.ok) return;
      const j = await r.json();
      if (!j.ok) return;
      IMG_FILTER_CFG = j.config || {};

      const enabledEl = document.getElementById('imgFilterEnabled');
      const modeEl = document.getElementById('imgFilterMode');
      const thEl = document.getElementById('imgFilterThreshold');
      const alertEl = document.getElementById('imgFilterAlertOnBlock');
      const maxLogEl = document.getElementById('imgFilterMaxLog');

      if (enabledEl) enabledEl.checked = !!IMG_FILTER_CFG.enabled;
      if (modeEl && IMG_FILTER_CFG.mode) modeEl.value = IMG_FILTER_CFG.mode;
      if (thEl && typeof IMG_FILTER_CFG.block_threshold === 'number') {
        thEl.value = IMG_FILTER_CFG.block_threshold.toFixed(2);
      }
      if (alertEl && Object.prototype.hasOwnProperty.call(IMG_FILTER_CFG, 'alert_on_block')) {
        alertEl.checked = !!IMG_FILTER_CFG.alert_on_block;
      }
      if (maxLogEl && IMG_FILTER_CFG.max_log_entries) {
        maxLogEl.value = IMG_FILTER_CFG.max_log_entries;
      }
    } catch (e) {
      console.error('loadImageFilterConfig error', e);
    }
  }

  async function saveImageFilterConfig() {
    const msgEl = document.getElementById('imgFilterMsg');
    if (msgEl) { msgEl.textContent = ''; msgEl.style.color = '#444'; }

    const enabledEl = document.getElementById('imgFilterEnabled');
    const modeEl = document.getElementById('imgFilterMode');
    const thEl = document.getElementById('imgFilterThreshold');
    const alertEl = document.getElementById('imgFilterAlertOnBlock');
    const maxLogEl = document.getElementById('imgFilterMaxLog');

    const body = {
      enabled: enabledEl ? !!enabledEl.checked : false,
      mode: modeEl ? modeEl.value : 'block',
      alert_on_block: alertEl ? !!alertEl.checked : true
    };

    if (thEl && thEl.value) {
      body.block_threshold = parseFloat(thEl.value);
    }
    if (maxLogEl && maxLogEl.value) {
      body.max_log_entries = parseInt(maxLogEl.value, 10);
    }

    try {
      const r = await fetch('/api/image_filter/config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      });
      if (!r.ok) {
        const t = await r.text();
        if (msgEl) {
          msgEl.textContent = 'Error saving: ' + t;
          msgEl.style.color = 'crimson';
        }
        return;
      }
      const j = await r.json();
      if (!j.ok) {
        if (msgEl) {
          msgEl.textContent = 'Error saving: ' + (j.error || 'unknown');
          msgEl.style.color = 'crimson';
        }
        return;
      }
      IMG_FILTER_CFG = j.config || {};
      if (msgEl) {
        msgEl.textContent = 'Saved.';
        msgEl.style.color = 'green';
      }
    } catch (e) {
      console.error('saveImageFilterConfig error', e);
      if (msgEl) {
        msgEl.textContent = 'Error saving: ' + e;
        msgEl.style.color = 'crimson';
      }
    }
  }

  function renderImageFilterEvents(events) {
    const tbody = document.getElementById('imgFilterEventsBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    (events || []).slice().reverse().forEach(ev => {
      const tr = document.createElement('tr');

      const tdTime = document.createElement('td');
      const d = new Date((ev.ts || 0) * 1000);
      tdTime.textContent = d.toLocaleTimeString() + '\n' + d.toLocaleDateString();
      tdTime.className = 'mini';

      const tdStudent = document.createElement('td');
      tdStudent.textContent = ev.student || '';
      tdStudent.className = 'mini';

      const tdAction = document.createElement('td');
      tdAction.textContent = ev.action || '';
      tdAction.className = 'mini';

      const tdReason = document.createElement('td');
      tdReason.textContent = ev.label || ev.reason || '';
      tdReason.className = 'mini';

      const tdScore = document.createElement('td');
      tdScore.textContent = (typeof ev.score === 'number' ? ev.score.toFixed(2) : '');
      tdScore.className = 'mini';

      const tdUrl = document.createElement('td');
      const link = document.createElement('a');
      link.href = ev.page_url || ev.src || '#';
      link.textContent = (ev.page_url || ev.src || '').slice(0, 80) || '(no url)';
      link.target = '_blank';
      tdUrl.appendChild(link);
      tdUrl.className = 'mini';

      tr.appendChild(tdTime);
      tr.appendChild(tdStudent);
      tr.appendChild(tdAction);
      tr.appendChild(tdReason);
      tr.appendChild(tdScore);
      tr.appendChild(tdUrl);
      tbody.appendChild(tr);
    });
  }

  async function pollImageFilterEventsOnce() {
    try {
      const r = await fetch('/api/image_filter/logs');
      if (!r.ok) return;
      const j = await r.json();
      if (!j.ok) return;
      IMG_FILTER_EVENTS = j.events || [];
      renderImageFilterEvents(IMG_FILTER_EVENTS);
    } catch (e) {
      console.error('pollImageFilterEventsOnce error', e);
    }
  }

  function startImageFilterPolling() {
    if (IMG_FILTER_POLL_TIMER) {
      clearInterval(IMG_FILTER_POLL_TIMER);
      IMG_FILTER_POLL_TIMER = null;
    }
    pollImageFilterEventsOnce();
    IMG_FILTER_POLL_TIMER = setInterval(pollImageFilterEventsOnce, 10000);
  }

  // Kick off image filter UI once the page script has loaded
  (function(){
    const btn = document.getElementById('imgFilterSaveBtn');
    if (btn) {
      btn.addEventListener('click', function(ev){
        ev.preventDefault();
        saveImageFilterConfig();
      });
    }
    loadImageFilterConfig();
    startImageFilterPolling();
  })();

</script>
</body>
</html>
