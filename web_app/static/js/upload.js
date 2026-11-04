const fileInput = document.querySelector("#audio-file");
const fileName = document.querySelector("#file-name");
const dropZone = document.querySelector("#drop-zone");
const uploadForm = document.querySelector("#upload-form");
const submitButton = document.querySelector("#submit-button");

function showSelectedFile(file) {
    if (file && fileName) {
        fileName.textContent = `已选择：${file.name}`;
        dropZone?.classList.add("has-file");
    }
}

fileInput?.addEventListener("change", () => {
    showSelectedFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
    dropZone?.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add("is-dragging");
    });
});

["dragleave", "drop"].forEach((eventName) => {
    dropZone?.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove("is-dragging");
    });
});

dropZone?.addEventListener("drop", (event) => {
    const droppedFiles = event.dataTransfer.files;
    if (droppedFiles.length > 0 && fileInput) {
        fileInput.files = droppedFiles;
        showSelectedFile(droppedFiles[0]);
    }
});

uploadForm?.addEventListener("submit", () => {
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.querySelector("span").textContent = "正在分析，请稍候…";
    }
});
