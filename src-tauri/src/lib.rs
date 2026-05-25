use serde::Serialize;
use std::net::TcpListener;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{AppHandle, Manager, State};
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;

#[derive(Default)]
struct BackendState {
    runtime: Mutex<BackendRuntime>,
}

#[derive(Default)]
struct BackendRuntime {
    port: Option<u16>,
    child: Option<BackendChild>,
}

enum BackendChild {
    Dev(Child),
    Sidecar(CommandChild),
}

impl BackendChild {
    fn kill(self) -> Result<(), String> {
        match self {
            BackendChild::Dev(mut child) => child.kill().map_err(|e| e.to_string()),
            BackendChild::Sidecar(child) => child.kill().map_err(|e| e.to_string()),
        }
    }
}

#[derive(Serialize)]
struct BackendInfo {
    port: u16,
    url: String,
    mode: String,
}

#[tauri::command]
fn start_backend(app: AppHandle, state: State<BackendState>) -> Result<BackendInfo, String> {
    let mut runtime = state.runtime.lock().map_err(|_| "backend state poisoned".to_string())?;
    if let Some(port) = runtime.port {
        return Ok(BackendInfo {
            port,
            url: backend_url(port),
            mode: if cfg!(debug_assertions) { "dev".into() } else { "sidecar".into() },
        });
    }

    let port = reserve_port()?;
    let child = if cfg!(debug_assertions) {
        BackendChild::Dev(spawn_dev_backend(port)?)
    } else {
        BackendChild::Sidecar(spawn_sidecar_backend(&app, port)?)
    };

    runtime.port = Some(port);
    runtime.child = Some(child);

    Ok(BackendInfo {
        port,
        url: backend_url(port),
        mode: if cfg!(debug_assertions) { "dev".into() } else { "sidecar".into() },
    })
}

#[tauri::command]
fn stop_backend(state: State<BackendState>) -> Result<(), String> {
    shutdown_backend_state(&state)
}

fn reserve_port() -> Result<u16, String> {
    let listener = TcpListener::bind("127.0.0.1:0").map_err(|e| e.to_string())?;
    let port = listener.local_addr().map_err(|e| e.to_string())?.port();
    drop(listener);
    Ok(port)
}

fn backend_url(port: u16) -> String {
    format!("http://127.0.0.1:{port}")
}

fn project_root() -> Result<PathBuf, String> {
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    manifest_dir
        .parent()
        .map(Path::to_path_buf)
        .ok_or_else(|| "unable to resolve project root".to_string())
}

fn spawn_dev_backend(port: u16) -> Result<Child, String> {
    let root = project_root()?;
    let python = find_dev_python(&root).ok_or_else(|| {
        "未找到 Python 解释器。请先创建 .venv 或确保 python 在 PATH 中。".to_string()
    })?;

    Command::new(python)
        .current_dir(root)
        .arg("app.py")
        .arg("--port")
        .arg(port.to_string())
        .arg("--no-browser")
        .stdin(Stdio::null())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|e| format!("启动开发后端失败：{e}"))
}

fn find_dev_python(root: &Path) -> Option<PathBuf> {
    let candidates = if cfg!(target_os = "windows") {
        vec![
            root.join(".venv").join("Scripts").join("python.exe"),
            PathBuf::from("python"),
            PathBuf::from("py"),
        ]
    } else {
        vec![
            root.join(".venv").join("bin").join("python"),
            PathBuf::from("python3"),
            PathBuf::from("python"),
        ]
    };

    candidates.into_iter().find(|candidate| {
        if candidate.is_absolute() {
            candidate.exists()
        } else {
            true
        }
    })
}

fn spawn_sidecar_backend(app: &AppHandle, port: u16) -> Result<CommandChild, String> {
    let args = vec!["--port".to_string(), port.to_string(), "--no-browser".to_string()];
    let command = app
        .shell()
        .sidecar("binaries/pianke-backend")
        .map_err(|e| format!("准备 sidecar 失败：{e}"))?;
    let (mut rx, child) = command
        .args(args)
        .spawn()
        .map_err(|e| format!("启动 sidecar 失败：{e}"))?;

    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    println!("[pianke-backend] {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Stderr(line) => {
                    eprintln!("[pianke-backend] {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Error(message) => {
                    eprintln!("[pianke-backend] {message}");
                }
                _ => {}
            }
        }
    });

    Ok(child)
}

fn shutdown_backend_state(state: &State<BackendState>) -> Result<(), String> {
    let mut runtime = state.runtime.lock().map_err(|_| "backend state poisoned".to_string())?;
    if let Some(child) = runtime.child.take() {
        let _ = child.kill();
    }
    runtime.port = None;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .manage(BackendState::default())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![start_backend, stop_backend])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    let handle = app.handle().clone();
    app.run(move |_handle, event| {
        if matches!(event, tauri::RunEvent::Exit | tauri::RunEvent::ExitRequested { .. }) {
            let state = handle.state::<BackendState>();
            let _ = shutdown_backend_state(&state);
        }
    });
}
