/* HbF Evidence Atlas — interactive dashboard.
 * Vanilla JS + GSAP + Three.js (vendored, ES-module build of Three.js).
 * Runs offline from dashboard/index.html; data is embedded as window.ATLAS_DATA.
 */
import * as THREE from "./vendor/three.min.js";

const data = window.ATLAS_DATA || {};
const rows = Array.isArray(data.rows) ? data.rows : [];
const observations = Array.isArray(data.observations) ? data.observations : [];

const READOUT_HUE = {
  "gamma-globin-rna": 0x3b82f6,
  "hbF-percent": 0x8b5cf6,
  "f-cell-percent": 0x06b6d4,
  "hbF-per-cell": 0xf59e0b,
  "vo-free-event": 0x22c55e,
};
const STATUS_LEVEL = { supported: 1, contradicted: -1, insufficient: 0 };

const el = (id) => document.getElementById(id);
const tc = (text, cls) => {
  const e = document.createElement("span");
  if (cls) e.className = cls;
  e.textContent = text == null ? "" : String(text);
  return e;
};
const isSafeLink = (url) => typeof url === "string" && /^https?:\/\//i.test(url);

/* ---------------- helpers ---------------- */

function studyOf(row) {
  const c = (row.obs && row.obs.context) || {};
  return [c.species, c.model].filter(Boolean).join("/") || "(unknown)";
}

function valueLabel(obs) {
  if (!obs || obs.value == null) return "(no value)";
  return obs.value + (obs.unit ? " " + obs.unit : "");
}

function denominatorLabel(obs) {
  if (!obs) return "-";
  if (typeof obs.denominator === "number") return obs.denominator;
  return obs.denominator || "-";
}

function timePointsSorted() {
  const pts = observations.map((o) => o.time_point).filter(Boolean);
  return [...new Set(pts)].sort();
}

/* ---------------- filters ---------------- */

const state = { search: "", readout: "", study: "", intervention: "", status: "" };

function setOptions(selectId, values, allLabel) {
  const sel = el(selectId);
  sel.textContent = "";
  const all = document.createElement("option");
  all.value = "";
  all.textContent = allLabel;
  sel.appendChild(all);
  for (const v of values) {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    sel.appendChild(o);
  }
}

function rowMatches(row) {
  const obs = row.obs || {};
  const c = obs.context || {};
  if (state.readout && obs.readout_kind !== state.readout) return false;
  if (state.study && !studyOf(row).toLowerCase().includes(state.study.toLowerCase())) return false;
  const intervention = (c.intervention || "").toLowerCase();
  if (state.intervention && !intervention.includes(state.intervention.toLowerCase())) return false;
  if (state.status && (row.assessment && row.assessment.support) !== state.status) return false;
  if (state.search) {
    const q = state.search.toLowerCase();
    const hay = JSON.stringify([
      row.claim_text, row.claim_type, obs.readout_kind, obs.value, obs.unit,
      obs.denominator, obs.time_point, obs.sample_linkage, obs.evidence_locator,
      c.intervention, row.assessment && row.assessment.support, row.assessment && row.assessment.rationale,
    ]).toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function onFilter() {
  state.search = (el("search").value || "").trim();
  state.readout = el("f-readout").value;
  state.study = el("f-study").value;
  state.intervention = el("f-intervention").value;
  state.status = el("f-status").value;
  const visible = rows.filter(rowMatches);
  el("row-count").textContent = visible.length + " of " + rows.length + " cases";
  renderTable(visible);
  if (scene) scene.setVisible(rows.map(rowMatches));
}

/* ---------------- table ---------------- */

function buildTableRow(row) {
  const tr = document.createElement("tr");
  tr.className = "row";
  tr.dataset.obsId = row.obs_id;
  const add = (content, cls) => {
    const td = document.createElement("td");
    if (cls) td.className = cls;
    td.textContent = content == null ? "" : String(content);
    tr.appendChild(td);
  };
  add(row.claim_text, "claim");
  add(row.obs.readout_kind, "readout");
  add(studyOf(row), "study");
  add((row.obs.context && row.obs.context.intervention) || "", "intervention");
  add(valueLabel(row.obs), "value");
  add(row.obs.unit || "", "unit");
  add(denominatorLabel(row.obs), "denominator");
  add(row.obs.time_point || "", "time");
  add(row.obs.sample_linkage || "", "linkage");
  add(row.assessment.support, "status");
  add(row.obs.evidence_locator || "", "locator");
  return tr;
}

function renderTable(visible) {
  const tbody = el("table-body");
  tbody.textContent = "";
  for (const row of visible) {
    const tr = buildTableRow(row);
    tr.addEventListener("click", () => showEvidence(row));
    tr.addEventListener("mouseenter", () => scene && scene.highlight(row.obs_id));
    tbody.appendChild(tr);
  }
  if (visible.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 11;
    td.className = "empty";
    td.textContent = "No cases match the current filters.";
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
}

function renderStats() {
  const groups = new Set();
  for (const obs of observations) {
    if (obs.context && obs.context.study_group_id) groups.add(obs.context.study_group_id);
  }
  el("stats").textContent =
    rows.length + " cases · " + observations.length + " observations · " + groups.size + " study groups";
}

function renderLegend() {
  const legend = el("legend");
  legend.textContent =
    "Readouts: " + Object.keys(READOUT_HUE).join(", ") +
    " · Support levels: supported, contradicted, insufficient (see Evidence status column).";
}

/* ---------------- evidence panel ---------------- */

function field(title, value) {
  const div = document.createElement("div");
  div.className = "field";
  div.appendChild(tc(title + ":", "label"));
  div.appendChild(tc(value));
  return div;
}

function sourceCell(source) {
  const div = document.createElement("div");
  if (!source) return div;
  div.appendChild(tc(source.source_id, "value"));
  if (source.url && isSafeLink(source.url)) {
    const a = document.createElement("a");
    a.className = "source-link";
    a.href = source.url;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = source.url;
    div.appendChild(a);
  } else if (source.url) {
    div.appendChild(tc("unsafe link (not followed): " + source.url, "unsafe-link"));
  }
  if (source.figure_table) div.appendChild(tc("Figure/table: " + source.figure_table, "muted"));
  return div;
}

function showEvidence(row) {
  const obs = row.obs || {};
  const panel = el("panel-content");
  panel.textContent = "";
  const heading = (text) => {
    const h = document.createElement("h3");
    h.textContent = text;
    panel.appendChild(h);
  };
  heading("Claim");
  panel.appendChild(field("Claim", row.claim_text));
  panel.appendChild(field("Claim type", row.claim_type || "(none)"));

  heading("Decision");
  panel.appendChild(field("Evidence status", row.assessment.support));
  panel.appendChild(field("Direction", row.assessment.direction || "(none)"));
  panel.appendChild(field("Matched dimensions", row.assessment.matched_dimensions.join(", ") || "(none)"));
  panel.appendChild(field("Rationale", row.assessment.rationale));

  heading("Observation");
  panel.appendChild(field("Observation", obs.obs_id));
  panel.appendChild(field("Readout", obs.readout_kind));
  panel.appendChild(field("Assay", obs.assay || "(none)"));
  panel.appendChild(field("Value", valueLabel(obs)));
  panel.appendChild(field("Unit", obs.unit || "(none)"));
  panel.appendChild(field("Denominator", denominatorLabel(obs)));
  panel.appendChild(field("Time point", obs.time_point || "(none)"));
  panel.appendChild(field("Sample linkage", obs.sample_linkage || "(none)"));
  panel.appendChild(field("Uncertainty", obs.uncertainty || "(none)"));
  panel.appendChild(field("Direction", obs.direction || "(none)"));
  panel.appendChild(field("Endpoint definition", obs.evidence_locator || "(none)"));

  heading("Source");
  panel.appendChild(sourceCell(row.source));

  if (scene) scene.select(row.obs_id);
  const selected = document.querySelectorAll("#table-body .row");
  selected.forEach((r) => r.classList.toggle("selected", r.dataset.obsId === row.obs_id));
  if (prefersReducedMotion) return;
  gsap.from("#evidence-panel", { opacity: 0, x: -16, duration: 0.3, ease: "power2.out" });
}

/* ---------------- three.js map ---------------- */

const prefersReducedMotion = typeof window.matchMedia === "function"
  && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function initScene() {
  const canvas = el("map-canvas");
  if (typeof THREE === "undefined" || !canvas) return null;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / Math.max(canvas.clientHeight, 1), 0.1, 100);
  camera.position.set(0, 0, 14);
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));
  const light = new THREE.DirectionalLight(0xffffff, 0.6);
  light.position.set(3, 3, 8);
  scene.add(light);

  const timePoints = timePointsSorted();
  const pointObjects = [];
  rows.forEach((row, i) => {
    const obs = row.obs || {};
    const x = timePoints.includes(obs.time_point) ? timePoints.indexOf(obs.time_point) : 0;
    const y = STATUS_LEVEL[row.assessment.support] != null ? STATUS_LEVEL[row.assessment.support] : 0;
    const denom = typeof obs.denominator === "number" ? obs.denominator : 10;
    const size = Math.max(1.5, Math.min(8, 3 + Math.log10(denom + 1)));
    const color = new THREE.Color(READOUT_HUE[obs.readout_kind] || 0x6b7280);
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(size / 2, 8, 6),
      new THREE.MeshBasicMaterial({ color, depthTest: false })
    );
    mesh.position.set(x * 2 - 3, y * 2, 0);
    mesh.userData = { index: i };
    scene.add(mesh);
    pointObjects.push(mesh);
  });
  if (pointObjects.length && !prefersReducedMotion) {
    gsap.from(pointObjects, { opacity: 0, scale: 0, stagger: 0.04, duration: 0.3, ease: "power2.out" });
  }

  let hovered = null;
  const raycaster = new THREE.Raycaster();
  const vec = new THREE.Vector2();
  const computeIntersect = (e) => {
    vec.set((e.clientX / canvas.clientWidth) * 2 - 1, -(e.clientY / canvas.clientHeight) * 2 + 1);
    raycaster.setFromCamera(vec, camera);
    return raycaster.intersectObjects(pointObjects);
  };
  canvas.addEventListener("pointermove", (e) => {
    const hits = computeIntersect(e);
    const mesh = hits[0] && hits[0].object;
    if (mesh && mesh !== hovered) {
      hovered = mesh;
      if (!prefersReducedMotion) gsap.to(mesh, { scale: 1.25, duration: 0.15 });
    } else if (!mesh && hovered) {
      gsap.to(hovered, { scale: 1, duration: 0.15 });
      hovered = null;
    }
  });
  canvas.addEventListener("click", (e) => {
    const hits = computeIntersect(e);
    const mesh = hits[0] && hits[0].object;
    if (!mesh) return;
    showEvidence(rows[mesh.userData.index]);
    if (!prefersReducedMotion) gsap.to(mesh, { scale: 1.45, duration: 0.2, repeat: 1, yoyo: true });
  });

  function highlight(obsId) {
    const mesh = pointObjects.find((m) => rows[m.userData.index].obs_id === obsId);
    if (mesh && !prefersReducedMotion) gsap.to(mesh, { scale: 1.35, duration: 0.15, repeat: 1, yoyo: true });
  }
  function select(obsId) {
    const mesh = pointObjects.find((m) => rows[m.userData.index].obs_id === obsId);
    if (mesh && !prefersReducedMotion) gsap.to(mesh, { scale: 1.35, duration: 0.2 });
  }
  function setVisible(visibleList) {
    pointObjects.forEach((m, i) => {
      m.visible = visibleList[i];
    });
  }

  let rafId = 0;
  const animate = () => {
    renderer.render(scene, camera);
    rafId = requestAnimationFrame(animate);
  };
  animate();

  const onResize = () => {
    const w = canvas.clientWidth, h = Math.max(canvas.clientHeight, 1);
    renderer.setSize(w, canvas.clientHeight);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };
  window.addEventListener("resize", onResize);

  return { highlight, select, setVisible };
}

const scene = initScene();

/* ---------------- setup ---------------- */

function setupFilters() {
  setOptions("f-readout", [...new Set(observations.map((o) => o.readout_kind).filter(Boolean))].sort(), "All readouts");
  setOptions("f-study", [...new Set(rows.map(studyOf))].sort(), "All study types");
  setOptions(
    "f-intervention",
    [...new Set(observations.map((o) => o.context && o.context.intervention).filter(Boolean))].sort(),
    "All interventions"
  );
  setOptions("f-status", [...new Set(rows.map((r) => r.assessment.support))].sort(), "All statuses");
  el("f-readout").addEventListener("change", onFilter);
  el("f-study").addEventListener("change", onFilter);
  el("f-intervention").addEventListener("change", onFilter);
  el("f-status").addEventListener("change", onFilter);
  el("search").addEventListener("input", onFilter);
  el("search").addEventListener("search", onFilter);
  onFilter();
}

(function main() {
  renderStats();
  renderLegend();
  setupFilters();
})();
