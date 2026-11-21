/* MetStat fullscreen r157: move existing model chips, never clone them. */
(function(){
'use strict';
function relocate(){
  const fullscreen=document.getElementById('nvFs');
  if(!fullscreen)return false;
  const chips=fullscreen.querySelector('#fsMods');
  const top=fullscreen.querySelector('.fsRow.fsA');
  if(!chips||!top)return false;
  if(chips.parentElement!==top)top.appendChild(chips);
  const oldMenu=fullscreen.querySelector('.fsModDd');
  if(oldMenu)oldMenu.hidden=true;
  fullscreen.setAttribute('data-original-chips-horizontal','1');
  return true;
}
function start(){
  if(relocate())return;
  if(!document.body||typeof MutationObserver==='undefined')return;
  const watch=new MutationObserver(()=>{if(relocate())watch.disconnect();});
  watch.observe(document.body,{childList:true,subtree:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
else start();
window.MetStatFixOriginalModelChips=relocate;
}());
