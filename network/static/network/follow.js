document.addEventListener('DOMContentLoaded', function() {

    /* listener for clikc on follow button */
    document.getElementById("follow_button").onclick = function () {
        follow(this.dataset.user, this.dataset.follower);
      };

});

function follow(user, follower) {
  /* get csrf token in order to autherize post requests */
  const csrftoken = getCookie("csrftoken");

  /* package variables together */
  const variables = {
    user: user,
    follower: follower,
  };

  /* turn into json */
  data = JSON.stringify(variables);

  /* send post request to 'follow' view in django */
  response = fetch("/follow", {
    method: "POST",
    body: data,
    headers: { "X-CSRFToken": csrftoken },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      /* check if operation failed */
      if (data["operation"] == "failure") {
        return false;
      } else {
        /* update html to dislay whether user is now 'following' (or not)*/
        if (data["strike"]) {
          document.getElementById("follow_strike").style =
            "text-decoration:line-through";
        } else {
          document.getElementById("follow_strike").style = "";
        }

        /* update html to dislpay the total number of followers */
        document.getElementById("number_of_followers").innerHTML =
          data["followers"];
        return false;
      }
    });
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