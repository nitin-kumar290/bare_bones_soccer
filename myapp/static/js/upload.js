async function uploadToS3() {
    const fileInput = document.getElementById("uploadFile");
    if (!fileInput.files.length) {
        alert("Please select a file!");
        return;
    }

    const file = fileInput.files[0];

    // Step 1: Get a Pre-Signed URL from Django
    const response = await fetch(`/api/get_presigned_url/?filename=${file.name}&filetype=${file.type}`);
    const { url, fields, object_key } = await response.json();

    // Step 2: Upload the File Directly to S3
    const formData = new FormData();
    Object.keys(fields).forEach(key => formData.append(key, fields[key]));
    formData.append("file", file);

    await fetch(url, { method: "POST", body: formData });

    alert(`File uploaded successfully! S3 Path: ${object_key}`);
}
