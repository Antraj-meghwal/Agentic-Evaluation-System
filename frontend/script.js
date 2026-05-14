// Function runs when upload button is clicked
async function uploadFile() {

    // Get file input element
    const fileInput =
        document.getElementById("fileInput");

    // Get selected file
    const file = fileInput.files[0];

    // If no file selected
    if (!file) {

        alert("Please select a file");

        return;
    }

    // Create form data
    const formData = new FormData();

    // "file" matches backend parameter
    formData.append("file", file);

    // Send request to backend
    const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
            method: "POST",
            body: formData
        }
    );

    // Convert response into JSON
    const data = await response.json();

    // Show success message and clickable link
    document.getElementById("status").innerHTML = `

    File uploaded successfully!

    <br><br>

    <a href="${data.file_url}" target="_blank">
        Open Uploaded File
    </a>

    `; 
}