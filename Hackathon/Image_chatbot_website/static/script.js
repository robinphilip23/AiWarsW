
document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const previewImg = document.getElementById("preview-img");
    const hudText = document.getElementById("hudText");
    const form = document.getElementById("uploadForm");
    const scanLine = document.getElementById("scanLine");
    const submitBtn = document.getElementById("submitBtn");

    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFile(fileInput.files[0]);
        }
    });

    fileInput.addEventListener("change", () => handleFile(fileInput.files[0]));

    function handleFile(file) {
        if (file) {
            previewImg.src = URL.createObjectURL(file);
            previewImg.style.display = "block";
            hudText.style.display = "none";
        }
    }


    form.addEventListener("submit", (e) => {
        if (!fileInput.files[0]) {
            e.preventDefault();
            return alert("Please upload an image first.");
        }

        // Show Loading Overlay
        document.getElementById("loadingOverlay").style.display = "flex";

        // Allow form to submit naturally to trigger redirect to /identify
    });
});

