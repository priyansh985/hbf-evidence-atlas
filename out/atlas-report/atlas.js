import * as THREE from "./vendor/three.min.js";

const data = window.ATLAS_DATA || {};
const rows = data.rows || [];
const sourcesById = new Map((data.sources || []).map((s) => [s.source_id, s]));

function isSafeLink(url) {
  return /^https?:\/\//i.test(url);
}

function rowText(row) {
  return JSON.stringify(row).toLowerCase();
}

function studyOf(row) {
  const context = row.obs.context || {};
  return context.species + (context.model ? "/" + context.model : "");
}

function displayValue(o) {
  return o && o.value != null ? String(o.value) : "\u2014";
}

function displayDenom(o) {
  if (!o || o.denominator == null) return "\u2014";
  return String(o.denominator);
}

function statusText(assessment) {
  if (assessment.support === "supported") return "Supported";
  if (assessment.support === "contradicted") return "Contradicted";
  return "Insufficient";
}

function sourceCell(source) {
  const fragment = document.createDocumentFragment();
  if (!source) {
    fragment.appendChild(document.createTextNode("\u2014"));
    return fragment;
  }
  if (isSafeLink(source.url)) {
    const anchor = document.createElement("a");
    anchor.href = source.url;
    anchor.target = "_blank";
    anchor.rel = "noopener";
    anchor.textContent = source.source_id + (source.figure_table ? " \u00b7 " + source.figure_table : "");
    fragment.appendChild(anchor);
  } else {
    const span = document.createElement("span");
    span.className = "unsafe-link";
    span.title = "Not followed: unsafe link scheme.";
    span.textContent = source.url;
    fragment.appendChild(span);
  }
  return fragment;
}

const state = { search: "", readout: "", study: "", intervention: "", status: "" };

function visible(row) {
  const text = rowText(row);
  if (state.search && text.indexOf(state.search.toLowerCase()) === -1) return false;
  if (state.readout && row.obs.readout_kind !== state.readout) return false;
  if (state.study && studyOf(row) !== state.study) return false;
  const context = row.obs.context || {};
  if (state.intervention && (context.intervention || "") !== state.intervention) return false;
  if (state.status && row.assessment.support !== state.status) return false;
  return true;
}

function renderRows() {
  const tbody = document.getElementById("table-body");
  tbody.textContent = "";
  for (const row of rows.filter(visible)) {
    const tr = document.createElement("tr");
    const cells = [
      row.claim_text,
      row.claim_type || "",
      row.obs.readout_kind,
      studyOf(row),
      (row.obs.context || {}).intervention || "",
      displayValue(row.obs),
      row.obs.unit || "",
      displayDenom(row.obs),
      row.obs.time_point || "",
      row.obs.sample_linkage || "",
      statusText(row.assessment),
      row.obs.evidence_locator || "",
    ];
    cells.forEach((text, index) => {
      const td = document.createElement("td");
      td.textContent = text;
      tr.appendChild(td);
    });
    const tdSource = document.createElement("td");
    tdSource.appendChild(sourceCell(sourcesById.get(row.obs.source_id)));
    tr.appendChild(tdSource);
    tr.addEventListener("click", () => showEvidence(row));
    tbody.appendChild(tr);
  }
}

function buildSelectOptions(selectId, values) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const seen = new Set([""]);
  for (const value of Array.from(new Set(values.filter((v) => v != null && v !== ""))).sort()) {
    if (seen.has(value)) continue;
    seen.add(value);
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }
}

function showEvidence(row) {
  const panel = document.getElementById("evidence-panel");
  panel.classList.add("open");
  renderEvidence(row);
  revealPanel();
}

function renderEvidence(row) {
  const obs = row.obs;
  const assessment = row.assessment;
  const panelBody = document.getElementById("panel-body");
  panelBody.textContent = "";

  const claim = document.createElement("p");
  claim.className = "panel-claim";
  claim.textContent = row.claim_text;
  panelBody.appendChild(claim);

  const decision = document.createElement("div");
  decision.className = "panel-decision";
  const badge = document.createElement("span");
  badge.className = "status-badge status-" + assessment.support;
  badge.textContent = statusText(assessment);
  decision.appendChild(badge);
  if (assessment.direction) {
    const direction = document.createElement("span");
    direction.className = "panel-direction";
    direction.textContent = "Direction: " + assessment.direction;
    decision.appendChild(direction);
  }
  if (assessment.matched_dimensions && assessment.matched_dimensions.length > 0) {
    const dims = document.createElement("span");
    dims.className = "panel-dimensions";
    dims.textContent = "Matched dimensions: " + assessment.matched_dimensions.join(", ");
    decision.appendChild(dims);
  }
  const rationale = document.createElement("p");
  rationale.className = "panel-rationale";
  rationale.textContent = assessment.rationale || "";
  decision.appendChild(rationale);
  panelBody.appendChild(decision);

  const fields = [
    ["Readout", obs.readout_kind],
    ["Assay", obs.assay ? JSON.stringify(obs.assay) : "\u2014"],
    ["Value", displayValue(obs)],
    ["Unit", obs.unit || "\u2014"],
    ["Denominator", displayDenom(obs)],
    ["Time point", obs.time_point || "\u2014"],
    ["Sample linkage", obs.sample_linkage || "\u2014"],
    ["Uncertainty", obs.uncertainty != null ? String(obs.uncertainty) : "\u2014"],
    ["Evidence locator", obs.evidence_locator || "\u2014"],
  ];
  const list = document.createElement("dl");
  for (const [label, value] of fields) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    list.appendChild(dt);
    list.appendChild(dd);
  }
  panelBody.appendChild(list);

  const sourceSection = document.createElement("div");
  sourceSection.className = "panel-source";
  sourceSection.appendChild(sourceCell(sourcesById.get(obs.source_id)));
  panelBody.appendChild(sourceSection);
}

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function revealPanel() {
  const panel = document.getElementById("evidence-panel");
  gsap.from(panel, { x: -16, opacity: 0, duration: prefersReducedMotion() ? 0 : 0.3, ease: "power2.out" });
}

function animateRows() {
  const rowsEls = Array.from(document.querySelectorAll("#table-body tr"));
  if (rowsEls.length > 0) {
    gsap.from(rowsEls, { opacity: 0, stagger: 0.03, duration: prefersReducedMotion() ? 0 : 0.25 });
  }
}

function animateHover() {
  const tbody = document.getElementById("table-body");
  tbody.addEventListener("mouseover", (event) => {
    const tr = event.target.closest("tr");
    if (tr) {
      gsap.to(tr, { scale: 1.005, duration: prefersReducedMotion() ? 0 : 0.15, ease: "power2.out" });
    }
  });
  tbody.addEventListener("mouseout", (event) => {
    const tr = event.target.closest("tr");
    if (tr) {
      gsap.to(tr, { scale: 1, duration: prefersReducedMotion() ? 0 : 0.15 });
    }
  });
}

function readoutColor(readoutKind) {
  const palette = {
    "gamma-globin-rna": [0.13, 0.55, 0.87],
    "hbF-percent": [0.2, 0.65, 0.35],
    "f-cell-percent": [0.9, 0.45, 0.2],
    "hbF-per-cell": [0.7, 0.35, 0.65],
    "vo-free-event": [0.4, 0.75, 0.95],
  };
  const entry = palette[readoutKind || ""] || [0.65, 0.65, 0.65];
  return new THREE.Color().fromArray(entry);
}

function initScene() {
  const canvas = document.getElementById("map-canvas");
  if (typeof THREE === "undefined") {
    canvas.style.display = "none";
    return;
  }
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    50,
    canvas.clientWidth / Math.max(1, canvas.clientHeight),
    0.1,
    1000
  );
  camera.position.set(0, 0, 30);
  camera.lookAt(0, 0, 0);

  const timePoints = Array.from(new Set(rows.map((row) => row.obs.time_point || ""))).sort();
  const timeIndex = new Map(timePoints.map((tp, i) => [tp, i]));

  const pointsObjects = [];
  rows.forEach((row, i) => {
    const support = row.assessment.support;
    const y = support === "supported" ? 1 : support === "contradicted" ? -1 : 0;
    const timePoint = row.obs.time_point || "";
    const x = timeIndex.has(timePoint) ? timeIndex.get(timePoint) : 0;
    const denominator = typeof row.obs.denominator === "number" ? row.obs.denominator : 1;
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array([x, y, 0]), 3));
    const material = new THREE.PointsMaterial({
      color: readoutColor(row.obs.readout_kind),
      size: Math.max(2, Math.log10(denominator + 1) * 4),
      sizeAttenuation: true,
    });
    const pts = new THREE.Points(geometry, material);
    pts._rowIndex = i;
    scene.add(pts);
    pointsObjects.push(pts);
  });

  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  canvas.addEventListener("click", (event) => {
    if (pointsObjects.length === 0) return;
    mouse.x = (event.clientX / Math.max(1, canvas.clientWidth)) * 2 - 1;
    mouse.y = -((event.clientY / Math.max(1, canvas.clientHeight)) * 2 - 1);
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(pointsObjects, true);
    if (hits.length > 0) {
      showEvidence(rows[hits[0].object._rowIndex]);
    }
  });

  const resize = () => {
    const width = canvas.clientWidth;
    const height = Math.max(1, canvas.clientHeight);
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  resize();
  window.addEventListener("resize", resize);

  const animate = () => {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  };
  animate();
}

document.addEventListener("DOMContentLoaded", () => {
  const dataVersion = document.getElementById("data-version");
  if (dataVersion) dataVersion.textContent = String(data.data_version || "");

  buildSelectOptions("f-readout", rows.map((row) => row.obs.readout_kind));
  buildSelectOptions("f-study", rows.map((row) => studyOf(row)));
  buildSelectOptions("f-intervention", rows.map((row) => (row.obs.context || {}).intervention || ""));
  buildSelectOptions("f-status", rows.map((row) => row.assessment.support));

  const search = document.getElementById("search");
  if (search) {
    search.addEventListener("input", () => {
      state.search = search.value;
      renderRows();
    });
  }
  const filterSelects = [
    ["f-readout", "readout"],
    ["f-study", "study"],
    ["f-intervention", "intervention"],
    ["f-status", "status"],
  ];
  for (const [selectId, key] of filterSelects) {
    const select = document.getElementById(selectId);
    if (select) {
      select.addEventListener("change", () => {
        state[key] = select.value;
        renderRows();
      });
    }
  }

  renderRows();
  animateRows();
  animateHover();
  initScene();
});
