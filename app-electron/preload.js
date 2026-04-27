const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("hexoDecryptApi", {
  request: (endpoint, method, payload) => ipcRenderer.invoke("api:fetch", endpoint, method, payload)
});

