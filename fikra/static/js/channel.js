document.addEventListener("DOMContentLoaded", function() {

  const nodesLocked = document.getElementsByClassName('node-locked');
  const nodesLockPopClose = document.getElementsByClassName('node-lock-conditions-close');

  for (var i=0; i<nodesLocked.length; i++) {
    nodesLocked[i].addEventListener('click', function(e){
      const id = this.dataset.id;
      const nodeLockPop = document.getElementById('node-lock-conditions' + id);
      nodeLockPop.style.display = 'block';
    });
  }

  for (var i=0; i<nodesLockPopClose.length; i++) {
    nodesLockPopClose[i].addEventListener('click', function(e){
      this.parentNode.style.display = 'none';
    });
  }

});
