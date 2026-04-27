const state = {
  fetchResult: null,
  dictionaries: [],
  blocks: []
};

const urlInput = document.getElementById("urlInput");
const fetchBtn = document.getElementById("fetchBtn");
const fetchResult = document.getElementById("fetchResult");
const reloadDictBtn = document.getElementById("reloadDictBtn");
const dictFileList = document.getElementById("dictFileList");
const blockType = document.getElementById("blockType");
const blockArg1 = document.getElementById("blockArg1");
const blockArg2 = document.getElementById("blockArg2");
const addBlockBtn = document.getElementById("addBlockBtn");
const blockList = document.getElementById("blockList");
const limitInput = document.getElementById("limitInput");
const startCrackBtn = document.getElementById("startCrackBtn");
const refreshStatusBtn = document.getElementById("refreshStatusBtn");
const crackStatus = document.getElementById("crackStatus");
let dragFromIndex = -1;

function renderDictionaries() {
  if (state.dictionaries.length === 0) {
    dictFileList.innerHTML = "<li>暂无字典文件</li>";
    return;
  }
  dictFileList.innerHTML = state.dictionaries
    .map((item) => `<li>${item.name} (${item.count} 条)</li>`)
    .join("");
}

function renderBlocks() {
  blockList.innerHTML = state.blocks
    .map(
      (block, idx) =>
        `<li draggable="true" data-index="${idx}">#${idx + 1} ${describeBlock(block)} <button data-remove-index="${idx}">删除</button></li>`
    )
    .join("");
}

function describeBlock(block) {
  if (block.type === "dict") {
    return `字典块(dict_name=${block.config.dict_name})`;
  }
  return `枚举块(charset=${block.config.charset}, length=${block.config.length})`;
}

function maskFetchResult(data) {
  const masked = { ...data };
  const cipherHex = String(data.cipher_hex || "");
  if (cipherHex) {
    masked.cipher_hex = "[已隐藏]";
    masked.cipher_hex_length = cipherHex.length;
  }
  return masked;
}

async function loadDictionaries() {
  const data = await window.hexoDecryptApi.request("/api/dictionaries", "GET");
  state.dictionaries = data.dictionaries || [];
  renderDictionaries();
}

fetchBtn.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!url) return;
  const data = await window.hexoDecryptApi.request("/api/fetch", "POST", { url });
  state.fetchResult = data;
  fetchResult.textContent = JSON.stringify(maskFetchResult(data), null, 2);
});

reloadDictBtn.addEventListener("click", async () => {
  await loadDictionaries();
});

addBlockBtn.addEventListener("click", () => {
  const type = blockType.value;
  let config;
  if (type === "dict") {
    const dictName = blockArg1.value.trim();
    if (!dictName) {
      alert("字典块请输入字典名（比如 common-5000-demo.txt）");
      return;
    }
    config = { dict_name: dictName };
  } else {
    const charset = blockArg1.value;
    const length = Number(blockArg2.value || 1);
    if (!charset) {
      alert("枚举块请输入字符集");
      return;
    }
    if (!Number.isInteger(length) || length <= 0) {
      alert("枚举块长度必须是正整数");
      return;
    }
    config = { charset, length };
  }
  state.blocks.push({ type, config });
  blockArg1.value = "";
  renderBlocks();
});

blockType.addEventListener("change", () => {
  if (blockType.value === "dict") {
    blockArg1.placeholder = "输入字典文件名，如 common-5000-demo.txt";
    blockArg2.disabled = true;
  } else {
    blockArg1.placeholder = "输入字符集，如 abc123";
    blockArg2.disabled = false;
  }
});

blockList.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;
  const index = Number(target.dataset.removeIndex);
  if (!Number.isInteger(index)) return;
  state.blocks.splice(index, 1);
  renderBlocks();
});

blockList.addEventListener("dragstart", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLLIElement)) return;
  dragFromIndex = Number(target.dataset.index);
});

blockList.addEventListener("dragover", (event) => {
  event.preventDefault();
});

blockList.addEventListener("drop", (event) => {
  event.preventDefault();
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  const li = target.closest("li");
  if (!(li instanceof HTMLLIElement)) return;
  const dragToIndex = Number(li.dataset.index);
  if (!Number.isInteger(dragFromIndex) || !Number.isInteger(dragToIndex) || dragFromIndex === dragToIndex) return;
  const [moved] = state.blocks.splice(dragFromIndex, 1);
  state.blocks.splice(dragToIndex, 0, moved);
  dragFromIndex = -1;
  renderBlocks();
});

startCrackBtn.addEventListener("click", async () => {
  if (!state.fetchResult?.cipher_hex) {
    alert("请先抓取成功后再开始破解");
    return;
  }
  if (state.blocks.length === 0) {
    alert("请至少添加一个方块");
    return;
  }
  const payload = {
    cipher_hex: state.fetchResult.cipher_hex,
    hmac_digest: state.fetchResult.hmac_digest,
    blocks: state.blocks,
    limit: Number(limitInput.value || 100000)
  };
  const data = await window.hexoDecryptApi.request("/api/crack/start", "POST", payload);
  crackStatus.textContent = JSON.stringify(data, null, 2);
});

refreshStatusBtn.addEventListener("click", async () => {
  const data = await window.hexoDecryptApi.request("/api/crack/status", "GET");
  crackStatus.textContent = JSON.stringify(data, null, 2);
});

blockType.dispatchEvent(new Event("change"));
loadDictionaries();

