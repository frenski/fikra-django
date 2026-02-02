document.addEventListener("DOMContentLoaded", function() {
  console.log("Start");
  var gameIf = document.getElementById('games-container-if');
  if (_VPD.aspectRatio > 0) {
    if (_VPD.engine == 'game_mapconv') {
      const sW = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
      const sH = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
      if (sW > sH) {
        gameIf.style.height = (gameIf.offsetWidth / _VPD.aspectRatio) + 'px';
      } else {
        gameIf.style.height = (gameIf.offsetWidth * _VPD.aspectRatio) + 'px';
      }
    } else {
      gameIf.style.height = (gameIf.offsetWidth / _VPD.aspectRatio) + 'px';
    }
  } else {
    document.getElementById('games-container-if').onload = function() {
      // alert('myframe is loaded aaa');
      this.style.height = this.contentWindow.document.documentElement.scrollHeight + 'px';
    };
  }

});
