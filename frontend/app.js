document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const fileInfo = document.getElementById("file-info");
  const fileName = document.getElementById("file-name");
  const removeFileBtn = document.getElementById("remove-file");
  const processBtn = document.getElementById("process-btn");
  const statusMessage = document.getElementById("status-message");
  const loader = document.querySelector(".loader");
  const btnText = document.querySelector(".btn-text");

  let selectedFile = null;

  // Trigger file input
  dropZone.addEventListener("click", () => fileInput.click());

  // Handle Drag & Drop
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  ["dragleave", "dragend"].forEach((type) => {
    dropZone.addEventListener(type, () => {
      dropZone.classList.remove("drag-over");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");

    if (e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  });

  // Handle Input Change
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });

  function handleFileSelect(file) {
    if (!file.name.endsWith(".xlsx") && !file.name.endsWith(".xls")) {
      showStatus("يُرجى اختيار ملف Excel صالح (.xlsx, .xls)", "error");
      return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    dropZone.classList.add("hidden");
    processBtn.disabled = false;
    hideStatus();
  }

  // Remove file
  removeFileBtn.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    dropZone.classList.remove("hidden");
    processBtn.disabled = true;
  });

  // Process File
  processBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    setLoading(true);
    hideStatus();

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("/evaluate", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          "حدث خطأ أثناء معالجة الملف. يرجى التأكد من تنسيق الملف الصحيح.",
        );
      }

      console.log("Response content-type:", response.headers.get("content-type"));
      
      const blob = await response.blob();
      console.log("Received blob size:", blob.size);

      if (blob.size < 100) {
        const text = await blob.text();
        console.error("Possible error message in blob:", text);
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `evaluated_${selectedFile.name}`;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        a.remove();
      }, 100);

      showStatus("تم معالجة الملف بنجاح! سيتم التحميل الآن.", "success");
    } catch (error) {
      console.error("Error:", error);
      showStatus(error.message, "error");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(isLoading) {
    if (isLoading) {
      processBtn.disabled = true;
      loader.classList.remove("hidden");
      btnText.textContent = "جاري المعالجة...";
    } else {
      processBtn.disabled = false;
      loader.classList.add("hidden");
      btnText.textContent = "بدء التقييم";
    }
  }

  function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.classList.remove("hidden");
  }

  function hideStatus() {
    statusMessage.classList.add("hidden");
  }
});
