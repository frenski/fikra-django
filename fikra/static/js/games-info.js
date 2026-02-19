document.addEventListener("DOMContentLoaded", function() {

  var butLike = document.getElementById('button-social-like');
  var butLikeCount = document.getElementById('button-social-like-count');
  var urlToLike = "/node_update/add_like/" + _VPD.NodeId;

  if (butLike) {
    butLike.addEventListener('click', function() {
      var lxhr = new XMLHttpRequest();
      lxhr.open('GET', urlToLike);
      lxhr.setRequestHeader('X-CSRFToken', cookies['csrftoken']);
      lxhr.onload = function() {
          if (lxhr.status === 200) {
          butLikeCount.innerHTML = lxhr.responseText;
        } else {
          alert( _LANGVARS.games.likeCountIssue );
        }
      }
      lxhr.send();
      return false;
    });
  }

});
