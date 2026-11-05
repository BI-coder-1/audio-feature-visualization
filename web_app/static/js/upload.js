const modeButtons = document.querySelectorAll("[data-mode-button]");
const modePanels = document.querySelectorAll("[data-mode-panel]");

function activateMode(selectedMode) {
    modeButtons.forEach((button) => {
        const isSelected = button.dataset.modeButton === selectedMode;
        button.setAttribute("aria-selected", String(isSelected));
    });
    modePanels.forEach((panel) => {
        panel.hidden = panel.dataset.modePanel !== selectedMode;
    });
}

modeButtons.forEach((button) => {
    button.addEventListener("click", () => activateMode(button.dataset.modeButton));
});

document.querySelectorAll("input[type='file'][data-file-label]").forEach((fileInput) => {
    const fileName = document.getElementById(fileInput.dataset.fileLabel);
    const dropZone = fileInput.closest("[data-drop-zone]");

    function showSelectedFile(file) {
        if (file && fileName) {
            fileName.textContent = `已选择：${file.name}`;
            dropZone.classList.add("has-file");
        }
    }

    fileInput.addEventListener("change", () => showSelectedFile(fileInput.files[0]));

    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add("is-dragging");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove("is-dragging");
        });
    });

    dropZone.addEventListener("drop", (event) => {
        const droppedFiles = event.dataTransfer.files;
        if (droppedFiles.length > 0) {
            fileInput.files = droppedFiles;
            showSelectedFile(droppedFiles[0]);
        }
    });
});

document.querySelectorAll(".analysis-form").forEach((form) => {
    form.addEventListener("submit", () => {
        const submitButton = form.querySelector("button[type='submit']");
        submitButton.disabled = true;
        submitButton.querySelector("span").textContent = "正在计算，请稍候…";
    });
});
