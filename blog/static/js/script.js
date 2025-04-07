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

document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
  
    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', function () {
        const isExpanded = sidebar.classList.contains('expanded');
  
        sidebar.classList.toggle('expanded', !isExpanded);
        sidebar.classList.toggle('collapsed', isExpanded);
        document.body.classList.toggle('sidebar-open', !isExpanded);
      });
    }
  });
