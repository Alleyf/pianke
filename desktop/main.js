import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-shell";

window.__piankeShellOpen = open;

const statusEl = document.getElementById("status");
const detailEl = document.getElementById("detail");
const retryBtn = document.getElementById("retry");

function setStatus(text) {
  statusEl.textContent = text;
}

function setDetail(text) {
  detailEl.textContent = text;
}

function showRetry(show) {
  retryBtn.classList.toggle("hidden", !show);
}

async function waitForBackend(url, timeoutMs = 90_000) {
  const startedAt = Date.now();
  let attempts = 0;

  while (Date.now() - startedAt < timeoutMs) {
    attempts += 1;
    setStatus(`本地引擎启动中…（第 ${attempts} 次探测）`);
    try {
      const resp = await fetch(`${url}/api/capabilities`, { cache: "no-store" });
      if (resp.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 600));
  }

  throw new Error("后端启动超时");
}

async function boot() {
  showRetry(false);
  setStatus("准备启动桌面后端…");
  setDetail("首次打开如果需要装模型或解压依赖，时间会稍长一点。");

  try {
    const { url, mode } = await invoke("start_backend");
    setStatus(mode === "sidecar" ? "桌面后端已拉起，正在检查健康状态…" : "开发后端已拉起，正在检查健康状态…");
    setDetail(url);
    await waitForBackend(url);
    setStatus("就绪，正在进入片刻…");
    window.location.replace(url);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    setStatus("桌面引擎启动失败");
    setDetail(message);
    showRetry(true);
  }
}

retryBtn.addEventListener("click", boot);
boot();
