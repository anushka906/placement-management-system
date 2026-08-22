const state = {
  token: localStorage.getItem("pms_token"),
  role: localStorage.getItem("pms_role"),
  fullName: localStorage.getItem("pms_name"),
  profileExists: false,
  companies: [],
  jobs: [],
  applications: [],
};

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => [...document.querySelectorAll(selector)];

function showToast(message) {
  const toast = qs("#toast");
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3200);
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  let response;
  try {
    response = await fetch(`/api${path}`, { ...options, headers });
  } catch {
    throw new Error("Cannot reach the server. Make sure FastAPI is running.");
  }

  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    const error = contentType.includes("application/json") ? await response.json() : null;
    throw new Error(error?.detail || `Server error (${response.status})`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function formDataToObject(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  Object.keys(data).forEach((key) => {
    if (data[key] === "") {
      data[key] = null;
    }
  });
  return data;
}

function setAuthSession(payload) {
  state.token = payload.access_token;
  state.role = payload.role;
  state.fullName = payload.full_name;
  localStorage.setItem("pms_token", state.token);
  localStorage.setItem("pms_role", state.role);
  localStorage.setItem("pms_name", state.fullName);
}

function clearAuthSession() {
  state.token = null;
  state.role = null;
  state.fullName = null;
  localStorage.removeItem("pms_token");
  localStorage.removeItem("pms_role");
  localStorage.removeItem("pms_name");
}

function updateAuthView() {
  const isLoggedIn = Boolean(state.token);
  qs("#authView").classList.toggle("hidden", isLoggedIn);
  qs("#appView").classList.toggle("hidden", !isLoggedIn);
  qs("#logoutBtn").classList.toggle("hidden", !isLoggedIn);
  qs("#userBadge").classList.toggle("hidden", !isLoggedIn);
  qs("#userBadge").textContent = isLoggedIn ? `${state.fullName} - ${state.role}` : "";

  qsa(".admin-only").forEach((node) => node.classList.toggle("hidden", state.role !== "admin"));
  qsa(".student-only").forEach((node) => node.classList.toggle("hidden", state.role !== "student"));
  qs("#dashboardTitle").textContent = state.role === "admin" ? "Admin Overview" : "Student Overview";
}

function switchPanel(view) {
  qsa(".module-tab").forEach((btn) => btn.classList.toggle("active", btn.dataset.view === view));
  qsa(".view-panel").forEach((panel) => panel.classList.add("hidden"));
  qs(`#${view}Panel`).classList.remove("hidden");
}

function renderStats(stats = {}) {
  const studentStats = {
    open_jobs: state.jobs.length,
    applications: state.applications.length,
    shortlisted: state.applications.filter((item) => item.status === "shortlisted").length,
    selected: state.applications.filter((item) => item.status === "selected").length,
  };
  const data = state.role === "admin" ? stats : studentStats;

  qs("#statsGrid").innerHTML = Object.entries(data)
    .map(
      ([label, value]) => `
        <article class="stat-card">
          <span>${label.replaceAll("_", " ")}</span>
          <strong>${value}</strong>
        </article>
      `,
    )
    .join("");
}

function renderJobs() {
  const search = qs("#jobSearch").value.toLowerCase();
  const branch = qs("#branchFilter").value.toLowerCase();
  const appliedJobIds = new Set(state.applications.map((application) => application.job.id));
  const jobs = state.jobs.filter((job) => {
    const matchesSearch = !search || job.title.toLowerCase().includes(search);
    const matchesBranch = !branch || (job.eligible_branches || "").toLowerCase().includes(branch);
    return matchesSearch && matchesBranch;
  });

  qs("#jobsList").innerHTML =
    jobs
      .map((job) => {
        const alreadyApplied = appliedJobIds.has(job.id);
        const applyButton =
          state.role === "student"
            ? `<button class="primary" data-apply="${job.id}" ${alreadyApplied ? "disabled" : ""}>${
                alreadyApplied ? "Applied" : "Apply"
              }</button>`
            : "";
        return `
          <article class="data-card">
            <div>
              <h3>${job.title}</h3>
              <p>${job.company.name} - ${job.location}</p>
            </div>
            <p>${job.description}</p>
            <div class="meta">CGPA ${job.min_cgpa}+ | ${job.package_lpa || "N/A"} LPA | ${
              job.eligible_branches || "All branches"
            }</div>
            <div class="card-actions">
              <span class="badge">${job.job_type}</span>
              ${applyButton}
            </div>
          </article>
        `;
      })
      .join("") || `<p class="empty">No jobs found.</p>`;
}

function renderApplications() {
  qs("#applicationsList").innerHTML =
    state.applications
      .map((application) => {
        const adminActions =
          state.role === "admin"
            ? `
              <select data-status="${application.id}">
                <option value="applied" ${application.status === "applied" ? "selected" : ""}>Applied</option>
                <option value="shortlisted" ${application.status === "shortlisted" ? "selected" : ""}>Shortlisted</option>
                <option value="rejected" ${application.status === "rejected" ? "selected" : ""}>Rejected</option>
                <option value="selected" ${application.status === "selected" ? "selected" : ""}>Selected</option>
              </select>
            `
            : "";
        return `
          <article class="data-card">
            <div>
              <h3>${application.job.title}</h3>
              <p>${application.job.company.name} - ${application.student.user.full_name}</p>
            </div>
            <span class="status">${application.status}</span>
            <p>${application.note || "No note added."}</p>
            <div class="card-actions">${adminActions}</div>
          </article>
        `;
      })
      .join("") || `<p class="empty">No applications yet.</p>`;
}

function renderOverview() {
  const latestJobs = state.jobs.slice(0, 4);
  qs("#overviewList").innerHTML =
    latestJobs
      .map(
        (job) => `
        <article class="data-card">
          <h3>${job.title}</h3>
          <p>${job.company.name} is hiring for ${job.location}.</p>
          <div class="meta">${job.required_skills || "Skills not specified"}</div>
        </article>
      `,
      )
      .join("") || `<p class="empty">No job posts yet.</p>`;
}

function refreshCompanySelect() {
  qs("#companySelect").innerHTML = state.companies
    .map((company) => `<option value="${company.id}">${company.name}</option>`)
    .join("");
}

async function loadProfile() {
  if (state.role !== "student") return;
  try {
    const profile = await api("/students/me");
    state.profileExists = true;
    const form = qs("#profileForm");
    Object.entries(profile).forEach(([key, value]) => {
      if (form.elements[key] && value !== null) {
        form.elements[key].value = value;
      }
    });
    form.elements.roll_number.disabled = true;
  } catch {
    state.profileExists = false;
    qs("#profileForm").elements.roll_number.disabled = false;
  }
}

async function loadDashboard() {
  updateAuthView();
  const statsPromise = state.role === "admin" ? api("/admin/stats") : Promise.resolve({});
  const [stats, companies, jobs, applications] = await Promise.all([
    statsPromise,
    api("/companies"),
    api("/jobs"),
    api("/applications"),
  ]);

  state.companies = companies;
  state.jobs = jobs;
  state.applications = applications;
  await loadProfile();
  renderStats(stats);
  renderOverview();
  renderJobs();
  renderApplications();
  refreshCompanySelect();
}

qsa("[data-auth-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    qsa("[data-auth-tab]").forEach((tab) => tab.classList.remove("active"));
    button.classList.add("active");
    qs("#loginForm").classList.toggle("hidden", button.dataset.authTab !== "login");
    qs("#registerForm").classList.toggle("hidden", button.dataset.authTab !== "register");
  });
});

qsa("[data-view]").forEach((button) => {
  button.addEventListener("click", () => switchPanel(button.dataset.view));
});

qs("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const body = new URLSearchParams({
    username: form.email.value,
    password: form.password.value,
  });

  try {
    const payload = await api("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    setAuthSession(payload);
    await loadDashboard();
    showToast("Logged in successfully");
  } catch (error) {
    showToast(error.message);
  }
});

qs("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formDataToObject(event.currentTarget);
  try {
    await api("/auth/register", { method: "POST", body: JSON.stringify(payload) });
    showToast("Account created. You can login now.");
    qs("[data-auth-tab='login']").click();
  } catch (error) {
    showToast(error.message);
  }
});

qs("#logoutBtn").addEventListener("click", () => {
  clearAuthSession();
  updateAuthView();
  switchPanel("overview");
});

qs("#refreshBtn").addEventListener("click", () => loadDashboard().catch((error) => showToast(error.message)));
qs("#jobSearch").addEventListener("input", renderJobs);
qs("#branchFilter").addEventListener("input", renderJobs);

qs("#profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formDataToObject(event.currentTarget);
  payload.graduation_year = Number(payload.graduation_year);
  payload.cgpa = Number(payload.cgpa);
  try {
    const method = state.profileExists ? "PUT" : "POST";
    await api("/students/me", { method, body: JSON.stringify(payload) });
    await loadDashboard();
    showToast("Profile saved");
  } catch (error) {
    showToast(error.message);
  }
});

qs("#companyForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formDataToObject(event.currentTarget);
  try {
    await api("/companies", { method: "POST", body: JSON.stringify(payload) });
    event.currentTarget.reset();
    await loadDashboard();
    showToast("Company added");
  } catch (error) {
    showToast(error.message);
  }
});

qs("#jobForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formDataToObject(event.currentTarget);
  payload.company_id = Number(payload.company_id);
  payload.min_cgpa = Number(payload.min_cgpa || 0);
  payload.package_lpa = payload.package_lpa ? Number(payload.package_lpa) : null;
  payload.deadline = payload.deadline ? new Date(payload.deadline).toISOString() : null;
  try {
    await api("/jobs", { method: "POST", body: JSON.stringify(payload) });
    event.currentTarget.reset();
    await loadDashboard();
    showToast("Job published");
  } catch (error) {
    showToast(error.message);
  }
});

qs("#jobsList").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-apply]");
  if (!button) return;
  try {
    await api("/applications", {
      method: "POST",
      body: JSON.stringify({ job_id: Number(button.dataset.apply), note: "Applied from student portal" }),
    });
    await loadDashboard();
    showToast("Application submitted");
  } catch (error) {
    showToast(error.message);
  }
});

qs("#applicationsList").addEventListener("change", async (event) => {
  const select = event.target.closest("[data-status]");
  if (!select) return;
  try {
    await api(`/applications/${select.dataset.status}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: select.value }),
    });
    await loadDashboard();
    showToast("Application status updated");
  } catch (error) {
    showToast(error.message);
  }
});

updateAuthView();
if (state.token) {
  loadDashboard().catch((error) => {
    clearAuthSession();
    updateAuthView();
    showToast(error.message);
  });
}
