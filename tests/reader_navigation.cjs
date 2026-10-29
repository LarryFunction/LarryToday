const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map();let scrolled=false,resolveChunk;
const el=key=>{if(!elements.has(key))elements.set(key,{value:'',innerHTML:'',style:{},dataset:{},setAttribute(){},addEventListener(){},after(){},scrollIntoView(options){scrolled=options.behavior==='instant';}});return elements.get(key);};
const context=vm.createContext({console,URL,Date,setTimeout,localStorage:{getItem(){return null;}},document:{querySelector:el,getElementById:el,addEventListener(){},createElement:el},fetch(){return new Promise(()=>{});}});
vm.runInContext(fs.readFileSync('public/app.js','utf8'),context);
vm.runInContext(`edition={date:'2026-10-29',articles:[{id:'a',title:'Title',category:'科技与 AI',source_id:'one',_chunk:'one.json',_search:'摘要'}],events:[{id:'event-a',lead_id:'a',article_ids:['a'],category:'科技与 AI'}],background_events:[]};`,context);
let calls=0;context.get=()=>{calls++;return new Promise(resolve=>{resolveChunk=resolve;});};
(async()=>{
 const pending=vm.runInContext("render('event-a')",context);
 assert.equal(scrolled,true,'jump must happen before network completes');
 assert.match(el('#articles').innerHTML,/摘要/);
 const second=vm.runInContext("loadRows(new Set(['a']))",context);
 assert.equal(calls,1,'concurrent chunk requests must be shared');
 resolveChunk([{id:'a',title:'Title',summary_zh:'完整摘要'}]);
 await Promise.all([pending,second]);
 assert.match(el('#articles').innerHTML,/完整摘要/);
 console.log('Reader navigation tests passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
