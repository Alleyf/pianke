#!/usr/bin/env bash
# 片刻 · Linux 启动器
#
# 双击或 chmod +x 后运行：自动装 Python + 依赖 + 检查更新 + 启动桌面应用

set -e
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export LANG="${LANG:-en_US.UTF-8}"

cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  片刻 · Linux 启动器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

find_uv() {
  if command -v uv >/dev/null 2>&1; then
    echo "uv"
    return
  fi
  for cand in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv"; do
    if [ -x "$cand" ]; then
      echo "$cand"
      return
    fi
  done
}

UV="$(find_uv || true)"
if [ -z "$UV" ]; then
  echo ""
  echo "[首次准备] 正在下载 uv（Python 工具链，~30MB）..."
  if ! command -v curl >/dev/null 2>&1; then
    echo ""
    echo "❌ 系统没有 curl，无法自动安装 uv。"
    echo "   Debian / Ubuntu 可先执行：sudo apt install curl"
    exit 1
  fi
  curl -LSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  UV="$(find_uv || true)"
fi

if [ -z "$UV" ]; then
  echo ""
  echo "❌ uv 安装失败，请稍后重试。"
  exit 1
fi

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

echo ""
echo "正在准备 Python 环境并启动 launcher..."
exec "$UV" run --no-project --python ">=3.10" -- python scripts/launcher.py
