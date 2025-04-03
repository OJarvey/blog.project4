document.addEventListener("DOMContentLoaded", function () {
    // Select the textarea and submit button
    var commentBox = document.querySelector(".form-group textarea");
    var submitButton = document.querySelector("#comment-submit-button");

    if (commentBox && submitButton) {
        // Listen for input events on the textarea
        commentBox.addEventListener("input", function () {
            if (commentBox.value.trim() !== "") {
                submitButton.value = "Submit";
            } else {
                submitButton.value = "Add comment";
            }
        });
    } else {
        console.info("Comment form not found — skipping comment logic.");
      }
});
