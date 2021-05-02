document.addEventListener('DOMContentLoaded', function() {

  /* listener for click on like button */
    document.querySelectorAll("span.like_button").forEach (span => {
        span.onclick = function() {
            like(this.dataset.post, this.dataset.user);
        }
    });

});

function like(post, user) {

    /* get csrf token in order to authorize post requests */
    const csrftoken = getCookie("csrftoken");

    /* package variables together */
    const variables = {
        user: user,
        post: post,
    };

    /* turn into json */
    let data = JSON.stringify(variables);

    /* send post request to 'like' view in django */
    fetch("/like", {
        method: "POST",
        body: data,
        headers: {"X-CSRFToken": csrftoken},
    })
        .then(response => response.json())
        .then((data) => {
            /* check if operation failed */
            if (data["status"] === "403") {
                return false;
            } else {
                /* update html to display that post is 'liked' */
                document.getElementById(`like_text_${post}`).innerHTML =
                    data["text"];
                /* update html to display total number of likes a post has */
                document.getElementById(`like_number_${post}`).innerHTML =
                    data["likes"];
                return false;
            }
        })

}

/* taken from django documentation */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}