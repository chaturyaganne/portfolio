/* Progressive enhancement only: core content works without JavaScript. */
(() => {
 'use strict';
 const $=s=>document.querySelector(s),all=s=>[...document.querySelectorAll(s)];
 const status=$('#site-status'),menu=$('.menu-toggle'),nav=$('#primary-nav');
 menu.hidden=false;
 menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
 nav.addEventListener('click',e=>{if(e.target.closest('a')){menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');menu.focus();}});
 $('.filter-bar').hidden=false;
 all('[data-filter]').forEach(button=>button.addEventListener('click',()=>{const category=button.dataset.filter;let count=0;all('.work-card').forEach(card=>{card.hidden=category!=='all'&&category!==card.dataset.category;if(!card.hidden)count++;});all('[data-filter]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));$('#filter-count').textContent=`${count} ${count===1?'project':'projects'}`;}));
 let copyTrigger=null;
 all('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{copyTrigger=button;const url='https://chaturyaganne.github.io/portfolio/';try{if(!navigator.clipboard?.writeText)throw Error('Clipboard unavailable');await navigator.clipboard.writeText(url);status.textContent='Link copied. Ready to share.';button.dataset.originalLabel??=button.innerHTML;button.textContent='Link copied ✓';setTimeout(()=>{button.innerHTML=button.dataset.originalLabel;},2400);}catch{$('#copy-notice').hidden=false;$('#copy-fallback').value=url;$('#copy-fallback').focus();$('#copy-fallback').select();status.textContent='Automatic copy is unavailable. Select and copy the displayed link.';}}));
 $('#close-copy').addEventListener('click',()=>{$('#copy-notice').hidden=true;copyTrigger?.focus();});
})();
