document.addEventListener("DOMContentLoaded", function () {
  /* listener for button that enables edit options */
  document.querySelectorAll("span.edit_button").forEach((span) => {
    span.onclick = function () {
      show_edit(this.dataset.post);
    };
  });

  /* listener for button that hides edit options */
  document.querySelectorAll("span.cancel_button").forEach((span) => {
    span.onclick = function () {
      hide_edit(this.dataset.post);
    };
  });

  /* listener for button that is used to submit edits */
  document.querySelectorAll("span.submit_button").forEach((span) => {
    span.onclick = function () {
      submit_edit(this.dataset.post);
    };
  });
});

function show_edit(post) {
  /* hide content */
  document.getElementById(`content-box-${post}`).style = "display: none;";

  /* reveal textarea for entry */
  document.getElementById(`edit-box-${post}`).style = "display: block inline;";

  /* fill text area with current post*/
  document.getElementById(`text_area${post}`).value = document.getElementById(
    `content_${post}`
  ).innerText;

  /* hide edit button */
  document.getElementById(`edit_button${post}`).style = "display: none;";

  /* reveal cancel button */
  document.getElementById(`cancel_button${post}`).style =
    "display: block inline;";

  /* reveal submit button */
  document.getElementById(`submit_button${post}`).style =
    "display: block inline;";

  return false;
}

function hide_edit(post) {
  /* reveal content */
  document.getElementById(`content-box-${post}`).style =
    "display: block inline;";

  /* hide textarea for entry */
  document.getElementById(`edit-box-${post}`).style = "display: none;";

  /* reveal edit button */
  document.getElementById(`edit_button${post}`).style =
    "display: block inline;";

  /* hide cancel button */
  document.getElementById(`cancel_button${post}`).style = "display: none;";

  /* hide submit button */
  document.getElementById(`submit_button${post}`).style = "display: none;";

  return false;
}

function submit_edit(post) {
  /* get csrf token in order to autherize post requests */
  const csrftoken = getCookie("csrftoken");

  /* get content typed by user in the textarea */
  new_content = document.getElementById(`text_area${post}`).value;

  /* package variables together */
  const variables = {
    post: post,
    new_content: new_content,
  };

  /* turn into json */
  data = JSON.stringify(variables);

  /* send post request to 'follow' view in django */
  response = fetch("/edit", {
    method: "POST",
    body: data,
    headers: { "X-CSRFToken": csrftoken },
  })
    .then((response) => response.json())
    .then((data) => {
      /* check if operation failed & show warning message */
      if (data["operation"] == "failure") {
        document.getElementById(`text_area${post}`).value =
          '  FAILED_403: "YOU != AUTHOR"';
      } else {
        /* update created/updated */
        document.getElementById(`created_updated${post}`).innerHTML =
          data["created_updated"];
        /* update post content displayed on page */
        document.getElementById(`content_${post}`).innerHTML = new_content;
        hide_edit(post);
      }
    });

  return false;
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
