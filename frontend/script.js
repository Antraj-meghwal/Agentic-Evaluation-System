// -----------------------------------
// Fetch uploads when page loads
// -----------------------------------
window.onload = function () {

    fetchUploads();
};


// -----------------------------------
// Upload file function
// -----------------------------------
async function uploadFile() {

    // Get file input
    const fileInput =
        document.getElementById("fileInput");

    // Selected file
    const file = fileInput.files[0];

    // Validate selection
    if (!file) {

        alert("Please select a file");

        return;
    }

    // Create form data
    const formData = new FormData();

    formData.append("file", file);

    // Send upload request
    const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
            method: "POST",
            body: formData
        }
    );

    // Convert response
    const data = await response.json();

    // Show status
    document.getElementById("status").innerHTML = `
    
        File uploaded successfully!
    
    `;

    // Reload uploads from DB
    fetchUploads();
}


// -----------------------------------
// Fetch uploads from backend
// -----------------------------------
async function fetchUploads() {

    // Call backend API
    const response = await fetch(
        "http://127.0.0.1:8000/uploads"
    );

    // Convert to JSON
    const uploads = await response.json();

    // Get container
    const fileList =
        document.getElementById("fileList");

    // Clear old UI
    fileList.innerHTML = "";

    // Render uploads
    uploads.forEach((fileData) => {

        fileList.innerHTML += `
        
            <div class="file-item">

                <a href="${fileData.file_url}"
                   target="_blank">

                    ${fileData.filename}

                </a>

            </div>
        `;
    });
}