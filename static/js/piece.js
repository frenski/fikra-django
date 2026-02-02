document.addEventListener("DOMContentLoaded", function() {
	// main vars

  var ctrBar = document.getElementById('controlbar');
  var butPlay = document.getElementById('playstopbutton-container');
  var ctrTimeline = document.getElementById('controlbar-timeline');
  var ctrTimer = document.getElementById('controlbar-timer');
  var ctrAudio = document.getElementById('controlbar-volumecontrol');
  var metaDataBox = document.getElementById('metadata');
  var infoBut = document.getElementById('infobutton');
  var branding = document.getElementById('branding');
  var metaDataCloseBut = document.getElementById('metadata-closebut');
  var volCtr = document.getElementById('controlbar-volumecontrol');
  var volCtrInput = document.getElementById('controlbar-volumecontrol-input');
  var volCtrIco_old = document.getElementById('controlbar-volumecontrol-icon');
  var volCtrIco = volCtrIco_old.cloneNode(true);
  volCtrIco_old.parentNode.replaceChild(volCtrIco, volCtrIco_old);
  var vcUnfoldClass = 'vc-unfold';
  var vcInputUnfoldClass = 'vcinput-unfold';
  var metaDataShowClass = "metadata-show";

  if (_VPD.controlsPlay) {
    butPlay.style.display = "block";
  }

  if (_VPD.controlsTimeline) {
    ctrTimeline.style.display = "block";
    ctrTimer.style.display = "block";
  }

  if (_VPD.controlsAudio) {
    ctrAudio.style.display = "block";
  }

  if (!_VPD.controlsPlay && !_VPD.controlsTimeline && !_VPD.controlsAudio) {
    ctrBar.style.display = "none";
  }

  if (!_VPD.branding) {
    branding.style.display = "none";
  }

  if (_VPD.show_meta_data) {
    infoBut.style.display = "block";
    infoBut.addEventListener('click', function(){
      if (!metaDataBox.classList.contains(metaDataShowClass)) {
        metaDataBox.classList.add(metaDataShowClass);
      }
    });
    metaDataCloseBut.addEventListener('click', function(){
      metaDataBox.classList.remove(metaDataShowClass);
    });
  }

  if (volCtrIco) {
    volCtrIco.addEventListener('click', function() {
      if (volCtr.classList.contains(vcUnfoldClass)) {
        volCtr.classList.remove(vcUnfoldClass);
      } else {
        volCtr.classList.add(vcUnfoldClass);
      }

      if (volCtrInput.classList.contains(vcInputUnfoldClass)) {
        volCtrInput.classList.remove(vcInputUnfoldClass);
      } else {
        volCtrInput.classList.add(vcInputUnfoldClass);
      }
    });
  }


});
