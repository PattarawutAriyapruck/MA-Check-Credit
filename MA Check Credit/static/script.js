function showContent(contentId) {
    // Hide all content boxes
    const contentBoxes = document.querySelectorAll('.content-box');
    contentBoxes.forEach(box => {
        box.style.display = 'none';
    });

    // Show the selected content box
    const selectedBox = document.getElementById(contentId);
    if (selectedBox) {
        selectedBox.style.display = 'block';
    }
}
