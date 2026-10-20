import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
let JSDOM;
try { ({JSDOM}=await import('jsdom')); }
catch { ({JSDOM}=await import(new URL('../frontend/node_modules/jsdom/lib/api.js',import.meta.url))); }
let indexURL=new URL('./dist/index.html',import.meta.url);
try { await access(indexURL); } catch { indexURL=new URL('../index.html',import.meta.url); }
const html=await readFile(indexURL,'utf8');
const script=await readFile(new URL('./app.js',import.meta.url),'utf8');

function fixture(t, hash='#encore-prototype', clipboard=true){
 const dom=new JSDOM(html,{url:'https://chaturyaganne.github.io/portfolio/'+hash,runScripts:'outside-only',pretendToBeVisual:true});
 const w=dom.window;w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=()=>{};
 w.HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};
 w.HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');};
 let copied='';
 if(clipboard)Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async text=>{copied=text;}}});
 w.eval(script);t.after(()=>w.close());
 const $=selector=>w.document.querySelector(selector);
 const all=selector=>[...w.document.querySelectorAll(selector)];
 const click=selector=>{const el=$(selector);assert.ok(el,'Missing element '+selector);el.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));return el;};
 const change=(selector,value)=>{const el=$(selector);if(el.type==='checkbox')el.checked=value;else el.value=String(value);el.dispatchEvent(new w.Event('change',{bubbles:true}));};
 return {w,$,all,click,change,getCopied:()=>copied,api:w.EncoreApp};
}
function groupFit(f){f.change('#quantity',4);f.change('#budget',100);f.change('#step-free',true);f.change('#clear-view',true);}
function openEvent(f){f.click('[data-event="midnight"]');}
function compare(f,ids=['a','b']){for(const id of ids)f.change(`[data-compare="${id}"]`,true);f.click('[data-action="compare"]');}

test('portfolio, case study and prototype routes render distinct views',t=>{
 const f=fixture(t,'#home');assert.equal(f.$('#home-view').hidden,false);assert.equal(f.$('#prototype-view').hidden,true);
 f.w.location.hash='encore';f.api.route();assert.equal(f.$('#case-view').hidden,false);assert.match(f.w.document.title,/UX Case Study/);
 f.w.location.hash='encore-prototype';f.api.route();assert.equal(f.$('#prototype-view').hidden,false);assert.equal(f.$('#site-header').hidden,true);
});
test('event categories filter actual cards',t=>{const f=fixture(t);assert.equal(f.all('.event-card').length,6);f.click('[data-category="Music"]');assert.equal(f.all('.event-card').length,3);assert.equal(f.$('[data-category="Music"]').getAttribute('aria-pressed'),'true');});
test('group constraints produce two clear-view step-free listings under $100',t=>{const f=fixture(t);groupFit(f);openEvent(f);assert.deepEqual(f.all('[data-ticket]').map(el=>el.dataset.ticket),['a','b']);assert.match(f.$('#ticket-results').textContent,/2 options for 4 people/);});
test('adjacent inventory and totals respond to party size',t=>{const f=fixture(t);openEvent(f);groupFit(f);f.change('#quantity',5);assert.equal(f.all('[data-ticket]').length,1);f.click('[data-select="a"]');assert.equal(f.$('#review-total').textContent,'$400');assert.match(f.$('.price-breakdown').textContent,/5 × \$64/);});
test('zero-result recovery widens budget without changing group needs',t=>{const f=fixture(t);openEvent(f);groupFit(f);f.change('#budget',40);assert.ok(f.$('.empty-state'));f.click('[data-action="widen-budget"]');assert.equal(f.api.state.quantity,4);assert.equal(f.api.state.stepFree,true);assert.equal(f.api.state.clearView,true);assert.equal(f.api.state.budget,150);assert.equal(f.all('[data-ticket]').length,2);});
test('clearing route/view preferences preserves quantity and budget',t=>{const f=fixture(t);openEvent(f);groupFit(f);f.change('#budget',70);assert.ok(f.$('.empty-state'));f.click('[data-action="relax-needs"]');assert.equal(f.api.state.budget,70);assert.equal(f.api.state.quantity,4);assert.equal(f.all('[data-ticket]').length,1);assert.equal(f.$('[data-ticket]').dataset.ticket,'c');});
test('map sections activate using keyboard and can be cleared',t=>{const f=fixture(t);openEvent(f);const map=f.$('[data-map="102"]');map.focus();map.dispatchEvent(new f.w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));assert.equal(f.all('[data-ticket]').length,1);assert.equal(f.api.state.section,'102');assert.equal(f.$('[data-map="102"]').getAttribute('aria-pressed'),'true');f.click('[data-action="clear-section"]');assert.equal(f.all('[data-ticket]').length,5);});
test('comparison table carries prices, group totals and access distinctions',t=>{const f=fixture(t);groupFit(f);openEvent(f);compare(f);const table=f.$('.compare-table');assert.match(table.textContent,/\$320/);assert.match(table.textContent,/\$384/);assert.match(table.textContent,/Wheelchair space/);assert.match(table.textContent,/Not confirmed/);assert.match(table.textContent,/Step-free route/);});
test('fourth comparison rejected with a clear status',t=>{const f=fixture(t);openEvent(f);for(const id of ['a','b','c','d'])f.change(`[data-compare="${id}"]`,true);assert.equal(f.api.state.compare.length,3);assert.equal(f.$('[data-compare="d"]').checked,false);assert.match(f.$('#status').textContent,/up to three/);});
test('changing group constraints clears stale comparisons',t=>{const f=fixture(t);openEvent(f);f.change('[data-compare="a"]',true);f.change('[data-compare="b"]',true);f.change('#quantity',5);assert.equal(f.api.state.compare.length,0);assert.equal(f.$('#compare-dock').hidden,true);assert.match(f.$('#status').textContent,/comparisons cleared/);});
test('choosing from comparison reaches exact review arithmetic',t=>{const f=fixture(t);groupFit(f);openEvent(f);compare(f);f.click('[data-select="b"]');assert.equal(f.$('#review-total').textContent,'$384');assert.match(f.$('.price-breakdown').textContent,/Tickets \(4 × \$78\)/);assert.match(f.$('.price-breakdown').textContent,/Fees \(4 × \$18\)/);});
test('invalid budget blocks selection and recovers after correction',t=>{const f=fixture(t);openEvent(f);f.change('#budget',999);assert.equal(f.$('#budget').getAttribute('aria-invalid'),'true');assert.equal(f.$('[data-select="a"]').disabled,true);f.click('[data-map="102"]');assert.equal(f.$('#budget').value,'999');assert.equal(f.$('[data-select="a"]').disabled,true);f.change('#budget',90);assert.equal(f.$('[data-select="a"]').disabled,false);f.click('[data-select="a"]');assert.equal(f.$('#review-total').textContent,'$320');});
test('dialog traps focus and Escape restores the initiating control',t=>{const f=fixture(t);openEvent(f);const trigger=f.$('[data-select="a"]');trigger.focus();trigger.click();assert.equal(f.w.document.activeElement.getAttribute('aria-label'),'Close dialog');f.w.document.activeElement.dispatchEvent(new f.w.KeyboardEvent('keydown',{key:'Tab',shiftKey:true,bubbles:true,cancelable:true}));assert.equal(f.w.document.activeElement.dataset.action,'finish');f.w.document.activeElement.dispatchEvent(new f.w.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));assert.equal(f.$('#app-dialog').open,false);assert.equal(f.w.document.activeElement,trigger);});
test('copy plan includes exact cost and no-reservation notice',async t=>{const f=fixture(t);groupFit(f);openEvent(f);f.click('[data-select="a"]');f.click('[data-action="copy-plan"]');await Promise.resolve();assert.match(f.getCopied(),/\$80 each/);assert.match(f.getCopied(),/\$320 group total/);assert.match(f.getCopied(),/No reservation or purchase/);assert.match(f.getCopied(),/Wheelchair space: not confirmed/);});
test('clipboard unavailable exposes selectable plan rather than fake success',async t=>{const f=fixture(t,'#encore-prototype',false);openEvent(f);f.click('[data-select="a"]');f.click('[data-action="copy-plan"]');await Promise.resolve();assert.ok(f.$('#plan-text'));assert.match(f.$('#plan-text').value,/SAMPLE GROUP PLAN/);assert.ok(f.$('[data-action="review-again"]'));});
test('guided task records real local interaction flags without inventing a study',async t=>{const f=fixture(t);f.api.startTask();groupFit(f);openEvent(f);compare(f);f.click('[data-select="a"]');f.click('[data-action="copy-plan"]');await new Promise(resolve=>setTimeout(resolve,0));f.click('[data-action="finish"]');const result=f.api.lastSession;assert.equal(result.selection_meets_task,true);assert.equal(result.compared,true);assert.equal(result.copied_plan,true);assert.equal(result.quantity,4);assert.equal(result.group_total_cents,32000);assert.ok(result.actions>0);assert.ok(result.elapsed_seconds>=0);assert.match(f.$('.session-disclaimer').textContent,/not validated usability outcomes/);});
test('finishing a free exploration never claims a completed purchase',t=>{const f=fixture(t);openEvent(f);f.click('[data-select="a"]');f.click('[data-action="finish"]');assert.match(f.$('#app-dialog').textContent,/No tickets were purchased or reserved/);assert.equal(f.api.lastSession.task,'free-exploration');assert.equal(f.api.lastSession.selection_meets_task,null);});
test('accessible controls have labels and duplicate IDs are absent',t=>{const f=fixture(t);openEvent(f);for(const input of f.all('input[id],select[id]'))assert.ok(f.$(`label[for="${input.id}"]`),'Missing label for '+input.id);const ids=f.all('[id]').map(el=>el.id);assert.equal(new Set(ids).size,ids.length);for(const button of f.all('button'))assert.ok(button.textContent.trim()||button.getAttribute('aria-label'));});
test('case study separates actual implementation from planned research',t=>{const f=fixture(t,'#encore');assert.match(f.$('#case-process').textContent,/not a research finding/);assert.match(f.$('#case-validation').textContent,/no participant study has been run/);assert.match(f.$('#case-handoff').textContent,/not a native Figma file/);assert.ok(f.$('a[href="encore/research-kit.md"]'));});
test('project assets exist and runtime makes no external service calls',async()=>{for(const name of ['site.css','app.js','design-handoff.svg','research-kit.md','design-spec.md'])await access(new URL('./'+name,import.meta.url));assert.doesNotMatch(script,/\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket/);});

test('restarting guided task clears invalid budget state',t=>{const f=fixture(t);openEvent(f);f.change('#budget',999);f.api.startTask();assert.equal(f.api.state.inputError,null);assert.equal(f.$('#budget').value,'150');openEvent(f);assert.equal(f.$('[data-select="a"]').disabled,false);});
