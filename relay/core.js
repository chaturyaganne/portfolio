/* Shared deterministic core: runs in Node and in the browser. No model or network calls. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.RelayCore=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
 'use strict';
 const stop=new Set('a an the i my me to for of and or in on at is it this that with after before have has cannot can not need all please from'.split(' '));
 const tokens=text=>String(text).toLowerCase().match(/[a-z0-9]+/g)?.filter(t=>!stop.has(t)&&t.length>1)||[];
 function retrieve(query,role,documents){
  if(!['support','employee'].includes(role))throw Error('Unknown sample role.');
  const eligible=documents.filter(d=>d.status==='active'&&d.audience.includes(role));
  const corpus=eligible.map(doc=>({doc,terms:tokens(doc.title+' '+doc.text)}));
  const average=corpus.reduce((sum,x)=>sum+x.terms.length,0)/(corpus.length||1);
  const terms=[...new Set(tokens(query))];
  return corpus.map(({doc,terms:words})=>{let score=0,hits=0;for(const term of terms){const tf=words.filter(w=>w===term).length;if(!tf)continue;hits++;const df=corpus.filter(c=>c.terms.includes(term)).length;const idf=Math.log(1+(corpus.length-df+.5)/(df+.5));score+=idf*(tf*2.2)/(tf+1.2*(.25+.75*words.length/average));}return {...doc,score:Number(score.toFixed(3)),matchedTerms:hits};}).filter(d=>d.score>=1&&d.matchedTerms>=2).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id)).slice(0,3);
 }
 function fingerprint(value){let hash=2166136261;for(const char of JSON.stringify(value)){hash^=char.charCodeAt(0);hash=Math.imul(hash,16777619);}return (hash>>>0).toString(16).padStart(8,'0');}
 function plan(input,documents){
  if(!input||typeof input.title!=='string'||typeof input.details!=='string')throw Error('A title and details are required.');
  if(input.title.trim().length<4||input.details.trim().length<12)throw Error('Add a title (4+ characters) and details (12+ characters).');
  if(input.title.length>180||input.details.length>4000)throw Error('Keep the title under 180 characters and details under 4,000.');
  const role=input.role||'support';
  const started=typeof performance!=='undefined'?performance.now():Date.now();
  const query=input.title+' '+input.details;
  const sources=retrieve(query,role,documents);
  const suspicious=/ignore\s+(all\s+)?(previous|prior)\s+instructions|bypass\s+approval|send\s+me\s+(the\s+)?password|disable\s+(the\s+)?firewall|wipe\s+(the\s+)?device/i.test(query);
  const security=/phishing|compromised|malware/i.test(query);
  let category='unknown',decision='abstain',owner='Service Desk',reason='No sufficiently matching, active, permitted knowledge. Ask a human to investigate.';
  if(sources.length){category=sources[0].category;owner=sources[0].owner;decision='review';reason='Relevant sample evidence found. A human must review the proposed work note.';}
  if(security){category='security';owner='Security Response';decision='escalate';reason='Potential security incident. Keep the investigation human-led.';}
  if(suspicious){decision='blocked';reason='The ticket contains an instruction override or a high-risk request. Treat it as untrusted content and request human review.';}
  const primary=sources.find(s=>s.category===category);
  const steps=decision==='review'&&primary?primary.steps.map(text=>({text,sourceId:primary.id})):[];
  const draft=decision==='review'&&primary?`Suggested routing: ${owner}.\nEvidence: ${primary.text} [${primary.id}]\nNext checks:\n${steps.map((s,i)=>`${i+1}. ${s.text} [${s.sourceId}]`).join('\n')}\nHuman review required. No action has been executed.`:'';
  const elapsed=(typeof performance!=='undefined'?performance.now():Date.now())-started;
  const result={mode:'local-extractive',input:{title:input.title.trim(),details:input.details.trim(),role,number:input.number||'INC-DEMO-CUSTOM'},category,decision,owner,reason,sources,steps,draft,trace:[{name:'Validate request',detail:'Required fields and length checked.'},{name:'Filter knowledge',detail:`Active documents permitted for sample role: ${role}. Client-side role switching is a demo, not authentication.`},{name:'Retrieve evidence',detail:`BM25-style lexical ranking returned ${sources.length} matching sources.`},{name:'Apply policy',detail:reason},{name:'Prepare review',detail:decision==='review'?'Extractive work note ready. No model inference used.':'No executable proposal created.'}],metrics:{elapsedMs:Number(elapsed.toFixed(2)),retrieved:sources.length},approval:null};
  result.digest=digestFor(result);return result;
 }
 const digestFor=result=>fingerprint({input:result.input,draft:result.draft,decision:result.decision,owner:result.owner,category:result.category,steps:result.steps,sources:result.sources.map(s=>({id:s.id,revision:s.revision}))});
 function approve(result,{reviewer,confirmed,digest}){
  if(result.decision!=='review'||!result.draft)throw Error('This run cannot be approved.');
  if(!confirmed||typeof reviewer!=='string'||reviewer.trim().length<2)throw Error('Add a reviewer label and confirm the review.');
  if(digest!==result.digest||digestFor(result)!==result.digest)throw Error('The proposal changed. Review the latest run.');
  const approval={reviewer:reviewer.trim(),reviewedDigest:digest,recordedAt:new Date().toISOString(),scope:'sample work note only',identity:'self-declared demo label; not authenticated'};
  return {...result,approval};
 }
 function payload(result){
  if(!result.approval||result.approval.reviewedDigest!==result.digest||digestFor(result)!==result.digest)throw Error('Review and approve the current sample proposal before exporting a payload.');
  return {execution:'dry-run-only',method:'PATCH',path:'/api/now/table/incident/00000000000000000000000000000000',record:'placeholder sys_id; not a real incident',body:{work_notes:result.draft},review:result.approval,recommendedOwner:result.owner,limitations:'No request is sent. Assignment group resolution, authentication, server-side authorization and record verification are not implemented in this browser demo.'};
 }
 function evaluate(data){return data.evaluations.map(test=>{const scenario=data.scenarios.find(s=>s.id===test.scenario);const result=plan(scenario,data.documents);const checks=[{name:'Expected policy decision',pass:result.decision===test.expectedDecision}];if(test.expectedCategory)checks.push({name:'Expected category',pass:result.category===test.expectedCategory});if(test.expectedSource)checks.push({name:'Expected source retrieved',pass:result.sources.some(s=>s.id===test.expectedSource)});if(test.forbiddenSource)checks.push({name:'Forbidden source excluded',pass:!result.sources.some(s=>s.id===test.forbiddenSource)});checks.push({name:'Retired knowledge excluded',pass:result.sources.every(s=>s.status==='active')});return {id:test.id,name:test.name,pass:checks.every(c=>c.pass),checks,decision:result.decision,elapsedMs:result.metrics.elapsedMs};});}
 return {tokens,retrieve,plan,approve,payload,evaluate,fingerprint};
});
