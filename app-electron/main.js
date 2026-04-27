const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

const API_BASE_URL = process.env.HEXO_DECRYPT_API || "http://127.0.0.1:8765";

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 840,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile(path.join(__dirname, "renderer", "index.html"));
}

ipcMain.handle("api:fetch", async (_, endpoint, method = "GET", payload = null) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: payload ? JSON.stringify(payload) : undefined
  });
  return response.json();
});

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

