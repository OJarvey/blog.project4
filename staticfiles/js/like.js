document.addEventListener('DOMContentLoaded', function () {
    const likeButtons = document.querySelectorAll('.btn-like')
    const csrfTokenElem = document.querySelector("#csrf-form input[name='csrfmiddlewaretoken']")
    const csrfToken = csrfTokenElem ? csrfTokenElem.value : ''
  
    likeButtons.forEach((button) => {
      button.addEventListener('click', function (e) {
        e.preventDefault()
        const postId = this.getAttribute('data-post-id')
  
        fetch(`/blog/${postId}/like/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        })
          .then((response) => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
            return response.json()
          })
          .then((data) => {
            if (data.status === 'success') {
              this.classList.toggle('liked', data.liked)
              const likeCount = this.querySelector('.like-count')
              likeCount.textContent = data.likes_count
  
              const showLikersBtn = document.querySelector(`.btn-show-likers[data-post-id="${postId}"]`)
              const likersList = document.getElementById(`likers-${postId}`)
  
              if (data.likes_count > 0) {
                if (!showLikersBtn) {
                  const newButton = document.createElement('button')
                  newButton.className = 'btn-show-likers'
                  newButton.setAttribute('data-post-id', postId)
                  newButton.textContent = `Hide Likers (${data.likes_count})`
                  this.parentNode.insertBefore(newButton, this.nextElementSibling)
                  newButton.addEventListener('click', toggleLikersList)
                } else {
                  showLikersBtn.style.display = 'inline-block'
                  showLikersBtn.textContent = `Show Likers (${data.likes_count})`

                }
  
                if (likersList) {
                  let ul = likersList.querySelector('ul')
                  if (!ul) {
                    ul = document.createElement('ul')
                    likersList.appendChild(ul)
                  }
                  ul.innerHTML = data.likers.map((username) => `<li>${username}</li>`).join('')
                }
              }
            }
          })
      })
    })

    // This must be outside the likeButtons loop
    const showLikersButtons = document.querySelectorAll('.btn-show-likers')
    showLikersButtons.forEach((button) => {
      button.addEventListener('click', toggleLikersList)
    })

    function toggleLikersList(e) {
      const postId = this.getAttribute('data-post-id')
      const likersList = document.getElementById(`likers-${postId}`)
      if (!likersList) return
  
      const isVisible = likersList.style.display === 'block'
      likersList.style.display = isVisible ? 'none' : 'block'
      this.textContent = `${isVisible ? 'Show' : 'Hide'} Likers (${likersList.querySelectorAll('li').length})`
    }
  })

  document.addEventListener("DOMContentLoaded", function () {
    const deleteForms = document.querySelectorAll(".delete-comment-form");
  
    deleteForms.forEach((form) => {
      form.addEventListener("submit", function (e) {
        const confirmed = confirm(
          "Are you sure you want to delete this comment?"
        );
        if (!confirmed) {
          e.preventDefault();
        }
      });
    });
  });
  