document.addEventListener("DOMContentLoaded", function() {

  const nodeMenuButs = document.getElementsByClassName('node-menu-button');
  const nodeMenuPreviews = document.getElementsByClassName('node-menu-preview');
  const nodeMenuEdits = document.getElementsByClassName('node-menu-edit');
  const nodeMenuDeletes = document.getElementsByClassName('node-menu-delete');
  const nodeMenuEmbeds = document.getElementsByClassName('node-menu-embed');
  const nodeMenuScorms = document.getElementsByClassName('node-menu-scorm');
  const nodeMenuStats = document.getElementsByClassName('node-menu-stat');

  const dialogActCancelEl = document.getElementById('dialog-actions-cancel');
  const dialogActExecuteEl = document.getElementById('dialog-actions-execute');
  const dialogActIfrClose = document.getElementById('dialog-actions-ifr-close');
  const dialogWrapperEl = document.getElementById('dialog-wrapper');
  const dialogElDel = document.getElementById('dialog-del');
  const dialogElIfr = document.getElementById('dialog-ifr');
  const dialogIfrCode = document.getElementById('dialog-ifr-code');

  const embSwitch = document.getElementById('switch-show-embedded');
  const filterForm = document.getElementById('filter-form');

  const avInput = document.getElementById('id_picture_0');
  const avCrop = document.getElementById('cropper');
  const avImg = document.getElementById('avatarimg');

  const profForm = document.getElementById('profile_form');
  const profStatic = document.getElementById('profile-static');
  const profEditBut = document.getElementById('profile-edit-but');
  const profCloseBut = document.getElementById('profile-close-but');
  const profFormLoader = document.getElementById('profile-form-loader');
  const profFormSubmit = document.getElementById('profile_form_submit');


  for (var i=0; i<nodeMenuButs.length; i++) {
    nodeMenuButs[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      const id = this.dataset.id;
      const nodeMenuBlock = document.getElementById('node-menu-block' + id)
      if (nodeMenuBlock.style.display == 'none') {
        nodeMenuBlock.style.display = 'block';
      } else {
        nodeMenuBlock.style.display = 'none';
      }
    });
  }

  for (var i=0; i<nodeMenuPreviews.length; i++) {
    nodeMenuPreviews[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      window.open(this.dataset.url, '_blank').focus(e);
    });
  }

  for (var i=0; i<nodeMenuStats.length; i++) {
    nodeMenuStats[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      window.open(this.dataset.url, '_blank').focus(e);
    });
  }

  for (var i=0; i<nodeMenuEdits.length; i++) {
    nodeMenuEdits[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      window.open(this.dataset.url, '_blank').focus();
    });
  }

  for (var i=0; i<nodeMenuDeletes.length; i++) {
    nodeMenuDeletes[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      dialogActExecuteEl.setAttribute('href', this.dataset.url);
      if (dialogElDel) dialogElDel.style.display = 'block';
      if (dialogElIfr) dialogElIfr.style.display = 'none';
      dialogWrapperEl.style.display = 'block';
    });
  }

  dialogActCancelEl.addEventListener('click', function(e){
    e.preventDefault();
    e.stopPropagation();
    if (dialogElDel) dialogElDel.style.display = 'none';
    dialogWrapperEl.style.display = 'none';
    dialogActExecuteEl.setAttribute('href', '#');
  });

  for (var i=0; i<nodeMenuEmbeds.length; i++) {
    nodeMenuEmbeds[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      if (dialogElIfr) dialogElIfr.style.display = 'block';
      if (dialogElDel) dialogElDel.style.display = 'none';
      dialogWrapperEl.style.display = 'block';
      dialogIfrCode.value = '<iframe src="'+this.dataset.url+'" width="100%" height="100%"/>';
    });
  }

  for (var i=0; i<nodeMenuScorms.length; i++) {
    nodeMenuScorms[i].addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      window.open(this.dataset.url, '_blank').focus(e);
    });
  }

  if (dialogActIfrClose) {
    dialogActIfrClose.addEventListener('click', function(e){
      e.preventDefault();
      e.stopPropagation();
      if (dialogElDel) dialogElDel.style.display = 'none';
      if (dialogWrapperEl) dialogWrapperEl.style.display = 'none';
      dialogIfrCode.value = '';
      // dialogActExecuteEl.setAttribute('href', '#');
    });
  }


  embSwitch.addEventListener('change', function(e){
    console.log(this.checked);
    if (!this.checked) {
      filterForm.show_embedded.value = 'off';
    } else {
      filterForm.show_embedded.value = 'on';
    }
    filterForm.submit();
  });


  function open_file(){
    avInput.click();
  }

  if (avImg) {
    avImg.addEventListener('click', function()
    {
      open_file();
      avInput.addEventListener('change', function()
      {
        avCrop.style.visibility = "visible";
      });
    });
  }

  if (profEditBut) {
    profEditBut.addEventListener('click', function(){
      profStatic.style.display = 'none';
      profForm.style.display = 'block';
    });
  }

  if (profCloseBut) {
    profCloseBut.addEventListener('click', function(){
      profStatic.style.display = 'block';
      profForm.style.display = 'none';
    });
  }

  if (profFormSubmit) {
    profFormSubmit.addEventListener('click', function(){
      profFormSubmit.style.display = 'none';
      profFormLoader.style.display = 'block';
    });
  }


});
