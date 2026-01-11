/**
 * ICH Detection - Detection Page Logic
 * Handles file upload, drag-and-drop, and API communication
 */

// API Configuration
const API_URL = "http://localhost:8000";

// DOM Elements
const uploadArea = document.getElementById("upload-area");
const fileInput = document.getElementById("dicom-file");
const runButton = document.getElementById("run-button");
const fileNameDisplay = document.getElementById("file-name");
const loadingOverlay = document.getElementById("loading-overlay");

// Selected file storage
let selectedFile = null;

/**
 * Initialize event listeners
 */
function init() {
  // Click to upload
  uploadArea.addEventListener("click", () => {
    fileInput.click();
  });

  // File selection change
  fileInput.addEventListener("change", handleFileSelect);

  // Drag and drop events
  uploadArea.addEventListener("dragover", handleDragOver);
  uploadArea.addEventListener("dragleave", handleDragLeave);
  uploadArea.addEventListener("drop", handleDrop);

  // Run detection button
  runButton.addEventListener("click", runDetection);
}

/**
 * Handle file selection from input
 */
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    validateAndDisplayFile(file);
  }
}

/**
 * Handle drag over event
 */
function handleDragOver(event) {
  event.preventDefault();
  uploadArea.classList.add("dragover");
}

/**
 * Handle drag leave event
 */
function handleDragLeave(event) {
  event.preventDefault();
  uploadArea.classList.remove("dragover");
}

/**
 * Handle file drop
 */
function handleDrop(event) {
  event.preventDefault();
  uploadArea.classList.remove("dragover");

  const files = event.dataTransfer.files;
  if (files.length > 0) {
    validateAndDisplayFile(files[0]);
  }
}

/**
 * Validate and display selected file
 */
function validateAndDisplayFile(file) {
  // Check if file is DICOM
  if (!file.name.toLowerCase().endsWith(".dcm")) {
    alert("Please select a DICOM (.dcm) file");
    return;
  }

  // Check file size (50 MB limit)
  const maxSize = 50 * 1024 * 1024; // 50 MB in bytes
  if (file.size > maxSize) {
    alert("File size exceeds 50 MB limit");
    return;
  }

  // Store file and display name
  selectedFile = file;
  fileNameDisplay.textContent = `Selected: ${file.name}`;
  runButton.disabled = false;

  console.log(
    "File selected:",
    file.name,
    `(${(file.size / 1024 / 1024).toFixed(2)} MB)`
  );
}

/**
 * Show loading overlay
 */
function showLoading() {
  loadingOverlay.classList.add("active");
}

/**
 * Hide loading overlay
 */
function hideLoading() {
  loadingOverlay.classList.remove("active");
}

/**
 * Run hemorrhage detection
 */
async function runDetection() {
  if (!selectedFile) {
    alert("Please select a DICOM file");
    return;
  }

  // Disable button and show loading
  runButton.disabled = true;
  showLoading();

  try {
    // Create form data
    const formData = new FormData();
    formData.append("file", selectedFile);

    console.log("Sending request to API...");

    // Send request to backend
    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      body: formData,
    });

    console.log("Response status:", response.status);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Prediction failed");
    }

    // Parse response
    const result = await response.json();
    console.log("Detection result:", result);

    // Store results in sessionStorage
    sessionStorage.setItem("detectionResult", JSON.stringify(result));

    // Redirect to results page
    window.location.href = "results.html";
  } catch (error) {
    console.error("Error:", error);
    hideLoading();
    runButton.disabled = false;

    // User-friendly error messages
    let errorMessage = "An error occurred during detection. ";

    if (error.message.includes("Failed to fetch")) {
      errorMessage +=
        "Please ensure the backend server is running on http://localhost:8000";
    } else {
      errorMessage += error.message;
    }

    alert(errorMessage);
  }
}

/**
 * Check backend health on page load
 */
async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      console.log("Backend health:", data);

      if (!data.model_loaded) {
        console.warn("Warning: Model is not loaded on backend");
      }
    }
  } catch (error) {
    console.warn("Backend health check failed:", error.message);
    console.warn(
      "Make sure the backend server is running on http://localhost:8000"
    );
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  init();
  checkBackendHealth();
});
