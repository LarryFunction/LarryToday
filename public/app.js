let currentPage=1, pageSignature='', renderVersion=0;
const PAGE_SIZE=30;
const $ = s => document.querySelector(s);
const categories = ['全部','国际政治','科技与 AI','经济与投资','科学与探索','环境与气候','社会与文化'];
const mapping = {international:'国际政治',regional:'国际政治',diplomacy:'国际政治',technology:'科技与 AI',ai:'科技与 AI',economy:'经济与投资',macro:'经济与投资',disclosure:'经济与投资',science:'科学与探索',climate:'环境与气候',society:'社会与文化'};
let health=[],socialStatus={},socialPosts=[],focusOnly=false,savedArticles={};
try{savedArticles=JSON.parse(localStorage.getItem('larrytoday-saved-articles')||'{}');}catch{}
let edition = {articles:[]}, sources = [], category = '全部', savedOnly = false, directory = false, saved = new Set();
try { saved = new Set(JSON.parse(localStorage.getItem('larrytoday-saved') || '[]')); } catch {}
const esc = v => String(v ?? '').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safe = u => {try {const v=new URL(u); return ['http:','https:'].includes(v.protocol)?esc(v.href):'#';}catch{return '#';}};
const name = id => sources.find(s=>s.id===id)?.name || edition.articles.find(a=>a.source_id===id)?.source_name || (edition.social_posts||[]).find(a=>a.source_id===id)?.source_name || id;
const date = v => v ? new Date(v).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}) : '发布时间未提供';
const link = a => `<a href="${safe(a.url)}" target="_blank" rel="noopener noreferrer">${esc(a.title_zh||a.title)}</a>`;
const kicker = a => `<div class="kicker theme-${themes[a.category]?.[0]||'world'}">${esc(a.category)}</div>`;
const themes = {
  '全部': ['world','A WORLD IN MOTION','GLOBAL PERSPECTIVES','地球上的每一天','从纷繁的新闻中，寻找世界的脉络。'],
  '国际政治': ['politics','ACROSS THE BORDERS','POWER / PEOPLE / PLACES','疆界之外，世界之内','观察地缘格局，也看见格局中的人。'],
  '科技与 AI': ['technology','THE NEXT POSSIBILITY','CODE / INTELLIGENCE / FUTURE','计算未来的可能','在技术的加速中，理解改变的方向。'],
  '经济与投资': ['economy','THE SHAPE OF VALUE','CAPITAL / MARKETS / ECONOMY','理解价值的流向','透过数据与市场，阅读经济的温度。'],
  '科学与探索': ['science','BEYOND THE KNOWN','SCIENCE / SPACE / DISCOVERY','向未知，再进一步','让证据引路，让好奇心继续远行。'],
  '环境与气候': ['climate','ONE SHARED PLANET','EARTH / ENERGY / CLIMATE','同一个星球，共同的明天','关注地球的变化，与我们生活的联系。'],
  '社会与文化': ['culture','THE HUMAN MOSAIC','SOCIETY / ARTS / CULTURE','每一种生活，都值得看见','在不同的声音中，理解人的丰富。']
};
function editionArt(){
  const [theme,caption,footer,title,description]=themes[category];
  const valid=/^\d{4}-\d{2}-\d{2}$/.test(edition.date||'');
  const d=valid?new Date(edition.date+'T12:00:00+08:00'):null;
  const month=d?d.toLocaleDateString('en-US',{month:'short',timeZone:'Asia/Shanghai'}).toUpperCase():'—';
  const day=valid?edition.date.slice(8):'—';
  const year=valid?edition.date.slice(0,4):'待刊';
  const weekday=d?d.toLocaleDateString('en-US',{weekday:'long',timeZone:'Asia/Shanghai'}).toUpperCase():'COMING SOON';
  return `<section class="edition-art theme-${theme}" aria-label="${esc(category)} · ${esc(edition.date||'待刊')} 日报视觉"><div class="art-copy"><div class="eyebrow">${caption}</div><h2>${title}</h2><p>${description}</p><span class="art-edition">VOL. ${year} <b>/</b> ${String(categories.indexOf(category)).padStart(2,'0')} — ${esc(category==='全部'?'每日环球版':category)}</span></div><div class="date-poster"><div class="poster-grid" aria-hidden="true"></div><div class="poster-shape shape-one" aria-hidden="true"></div><div class="poster-shape shape-two" aria-hidden="true"></div><div class="poster-shape shape-three" aria-hidden="true"></div><div class="poster-month">${month}<span>${year}</span></div><div class="poster-day">${day}</div><div class="poster-weekday">${weekday}<span>DAILY EDITION / UTC+8</span></div></div><div class="poster-footer"><span>${footer}</span><span>${valid?esc(edition.date):'等待首版'} <b>↗</b></span></div></section>`;
}
function comparisonPanel(a){
  const groups=a._event?.comparison?[a._event.comparison]:(edition.comparisons||[]).filter(g=>g.article_ids.includes(a.id));
  return groups.map(g=>`<details class="comparison"><summary>${esc(g.comparison_type||'多源视角')} <span>${esc(g.title_zh)} ↗</span></summary><div class="comparison-body"><p class="comparison-common">${esc(g.common_ground)}</p>${g.differences.map(d=>{const source=edition.articles.find(r=>r.id===d.article_id);return source?`<div class="source-perspective"><a href="${safe(source.url)}" target="_blank" rel="noopener noreferrer">${esc(name(source.source_id))} ↗</a><p>${esc(d.focus)}</p></div>`:'';}).join('')}</div></details>`).join('');
}
function geoMark(a){
  const topic={ '国际政治':['Affairs','国际事务'], '科技与 AI':['Tech','科技与智能'], '经济与投资':['Markets','经济与市场'], '科学与探索':['Research','科学研究'], '环境与气候':['Climate','环境与气候'], '社会与文化':['Culture','社会与文化'] };
  let g=a.geography;
  if(!g||g.kind==='unknown'){
    const [code,label]=topic[a.category]||['Topics','专题观察'];
    g={code,label,kind:'topic'};
  }
  if(g.code==='RESEARCH')g={...g,kind:'topic',label:'科学研究'};
  const isCountry=['single','pair'].includes(g.kind);
  const display=isCountry?g.code:String(g.code).toLowerCase().replace(/^[a-z]/,c=>c.toUpperCase());
  const codes=String(display).split(/\s*\/\s*/);
  const labelMarkup=String(g.label).split(' / ').map(label=>`<span>${esc(label)}</span>`).join('<i aria-hidden="true"> / </i>');
  const meaning={single:'单国 · 单圆',pair:'双国 · 双圆交叠',multi:'多国 · 多圆交叠',scope:'区域范围 · 经纬网格',topic:'主题归属 · 菱形'}[g.kind]||'主题归属';
  return `<aside class="geo-mark geo-${esc(g.kind)} ${!isCountry?'geo-word geo-wide':''} ${codes.join('').length>6?'geo-long':''}" aria-label="${g.kind==='topic'?'主题':'报道地域'}：${esc(g.label)}" title="${esc(meaning)}"><div class="geo-composition" aria-hidden="true"><i class="geo-orbit"></i><i class="geo-bar"></i><i class="geo-axis"></i></div><b class="geo-code">${codes.map(c=>`<span>${esc(c)}</span>`).join('')}</b><div class="geo-label">${labelMarkup}</div></aside>`;
}
function articleRow(a,i){
  const bilingual=a.title_zh?`<div class="english-title" lang="en">${esc(a.title_en||a.title)}</div>`:'';
  const summary=a.summary_zh||a.summary||a.feed_excerpt;
  const kind=a.research_status==='preprint'?'预印本':a.content_type;
  const typeTag=kind&&kind!=='新闻'?`<span class="type-tag">${esc(kind)}</span>`:'';
  return `<article class="news-row theme-${themes[a.category]?.[0]||'world'}" id="${esc(a._event?.id||'event-'+a.id)}"><div class="row-index"><span>${String(i+1).padStart(2,'0')}</span>${kicker(a)}<div class="row-source">${esc(name(a.source_id))}</div><time>${date(a.published_at)}</time></div><div class="row-story"><h3>${link(a)}</h3>${bilingual}${summary?`<p class="news-summary">${esc(summary)}</p>`:''}<div class="tags">${typeTag}${(a.tags||[]).map(t=>`<button data-tag="${esc(t)}">${esc(t)}</button>`).join('')}</div>${eventSources(a)}${comparisonPanel(a)}</div>${geoMark(a)}</article>`;
}
function notify(t){$('#toast').textContent=t;$('#toast').style.display='block';setTimeout(()=>$('#toast').style.display='none',2200);}
function matches(a,q){
  const members=a._event?.article_ids.map(id=>edition.articles.find(r=>r.id===id)).filter(Boolean)||[a];
  return members.some(r=>`${r.title} ${r.title_zh||''} ${r.title_en||''} ${r.summary_zh||r.summary||r._search||''} ${(r.tags||[]).join(' ')} ${name(r.source_id)}`.toLowerCase().includes(q));
}
function eventSources(a){
  const ids=a._event?.article_ids||[];
  if(ids.length<2)return '';
  return `<details class="event-sources"><summary>${a._event?.grouping_basis==='identical_headline'?'同题报道':'同一事件'} · ${ids.length} 篇报道 · ${new Set(ids.map(id=>edition.articles.find(r=>r.id===id)?.source_id)).size} 家来源　展开 ↗</summary>${ids.map(id=>{const r=edition.articles.find(a=>a.id===id);return r?`<div class="event-source"><b>${esc(name(r.source_id))}</b><time>${date(r.published_at)}</time><p>${link(r)}</p></div>`:'';}).join('')}</details>`;
}
function morning(){
  const items=(edition.briefing||[]).filter(b=>category==='全部'||b.category===category);
  if(category!=='全部' && !focusOnly && items.length<3){
    for(const event of edition.events||[]){
      const row=edition.articles.find(a=>a.id===event.lead_id);
      if(row?.category===category && !items.some(b=>b.event_id===event.id)) items.push({event_id:event.id,category:row.category,title:row.title_zh||row.title,summary:row.summary_zh||row.summary||row._search||''});
      if(items.length>=3)break;
    }
  }
  if(!items.length)return '';
  const item=(b,i)=>`<li class="morning-card"><a href="#${esc(b.event_id)}"><div class="morning-card-top"><span class="morning-number">${String(i+1).padStart(2,'0')}</span><span class="morning-category">${esc(b.category)}</span><span class="morning-arrow" aria-hidden="true">↗</span></div><h3>${esc(b.title)}</h3><p>${esc(b.summary)}</p></a></li>`;
  return `<section class="morning theme-${themes[category][0]}" aria-label="晨读提要"><div class="morning-heading"><div><span class="morning-label">THE MORNING LETTER / ${String(items.length).padStart(2,'0')}</span><h2>${category==='全部'?'晨读 · 今日提要':'晨读 · 本版提要'}</h2></div><p>先读要点，再看世界<span>点击卡片，进入完整报道 ↗</span></p></div><ol class="morning-grid">${items.slice(0,3).map(item).join('')}</ol>${items.length>3?`<details class="morning-more"><summary><span>继续晨读</span> 展开其余 ${items.length-3} 则 <b aria-hidden="true">＋</b></summary><ol class="morning-grid">${items.slice(3).map((b,i)=>item(b,i+3)).join('')}</ol></details>`:''}<p class="morning-note">${category==='全部'?'按重要性线索与来源多样性自动选编':'本版精选优先，按发布时间补充本期报道'}</p></section>`;
}
function supplements(q){
  const rows=(edition.background_events||[]).map(e=>({...edition.articles.find(r=>r.id===e.lead_id),_event:e})).filter(a=>(category==='全部'||a.category===category)&&matches(a,q));
  let html=rows.length?`<details class="background-reading"><summary>背景阅读 · ${rows.length} 条 <small>早于本期窗口，帮助理解持续议题</small></summary>${rows.map(articleRow).join('')}</details>`:'';
  if(category==='科技与 AI'){
    const cutoff=edition.window?Date.parse(edition.window.end):Date.now();
    const posts=(edition.social_posts||[]).filter(p=>Date.parse(p.published_at)<cutoff&&Date.parse(p.published_at)>=cutoff-86400000&&matches(p,q));
    html+=`<section class="voices"><h2>业界声音 <span>VOICES & IDEAS</span></h2>${posts.length?posts.map(articleRow).join(''):`<p>本期暂无符合时间窗口的作者通讯或社交平台发言。${socialStatus.configured?'可在服务端观察名单配置账号。':'X 尚未配置访问凭证；不会以转述冒充原始发言。'}</p>`}</section>`;
  }
  return html;
}
function sourceState(id){
  const feeds=health.filter(h=>h.source_id===id);
  if(!feeds.length)return '<p class="source-state">目录收录 · 尚未接入</p>';
  const states={available:'可用',empty:'订阅可用 · 本轮暂无更新',unavailable:'暂不可用',stale:'订阅已过时',date_only:'仅日期，无精确时间',disabled:'未启用'};
  const count=(edition.articles||[]).filter(a=>a.source_id===id&&a.section!=='背景阅读').length;
  return `<p class="source-state">${feeds.map(f=>esc(states[f.state]||f.state)).filter((v,i,a)=>a.indexOf(v)===i).join(' / ')} · 本期 ${count} 篇</p><p class="ai-note">最近成功：${date(feeds.map(f=>f.last_success).filter(Boolean).sort().pop())}</p>`;
}
function healthSummary(){
  const available=health.filter(h=>h.state==='available');
  const regions=edition.coverage?.regions||{};
  return `<div class="health-summary"><p>${health.length} 个配置入口 · ${new Set(available.map(h=>h.source_id)).size} 家来源有可用精确日期订阅 · ${health.filter(h=>h.state==='stale').length} 个过时入口</p><p>本期来源地区：${Object.entries(regions).map(([r,n])=>esc(r)+' '+n).join(' / ')||'旧版暂无统计'}</p><p class="ai-note">统计反映接入与收录，不代表独立性或事实核验。X：${socialStatus.configured?'已配置凭证':'未配置凭证'}。</p></div>`;
}
function persistSaved(){localStorage.setItem('larrytoday-saved-articles',JSON.stringify(savedArticles));}
function rememberSaved(){for(const a of edition.articles){if(saved.has(a.id)&&!savedArticles[a.id]&&(!a._chunk||a._loaded))savedArticles[a.id]={...a,_editionDate:edition.date};}try{persistSaved();}catch{}}
async function hydrateSaved(){
  if([...saved].every(id=>savedArticles[id]))return;
  try{const days=await get('api/archive.json');for(const day of days){const n=await get('api/editions/'+day+'.json');for(const a of n.articles){if(saved.has(a.id)&&!savedArticles[a.id]&&(!a._chunk||a._loaded))savedArticles[a.id]={...a,_editionDate:day};}if([...saved].every(id=>savedArticles[id]))break;}persistSaved();}catch{notify('部分旧收藏暂未恢复，可打开对应原刊恢复。');}
}
function resetEdition(){currentPage=1;pageSignature='';directory=false;savedOnly=false;focusOnly=false;category='全部';$('#search').value='';updateEditionLabel();render();}
async function revisionDialog(day){const history=await get('api/revisions/'+day+'.json');showDialog(`<h2>${esc(day)} · 版本记录</h2><p>初版与每次修订分别保存，可随时查阅当时内容。</p>${history.map(h=>`<button class="archive-day" data-rev="${h.revision}" data-date="${day}">${h.revision===1?'初版':'修订 '+h.revision} · ${date(h.published_at)}<br>${esc(h.note)}</button>`).join('')}`);}
$('#focus-button').onclick=()=>{focusOnly=!focusOnly;render();};
$('#latest-button').onclick=async()=>{try{edition=await latestEdition();resetEdition();}catch{notify('无法读取最新一期');}};
$('#revision-button').onclick=async()=>{try{await revisionDialog(edition.date);}catch{notify('版本记录暂不可用');}};
async function loadRows(ids, snapshot=edition){
  const paths=[...new Set(snapshot.articles.filter(a=>ids.has(a.id)&&a._chunk&&!a._loaded).map(a=>a._chunk))];
  await Promise.all(paths.map(async path=>{
    const rows=await get(path);
    if(!Array.isArray(rows))throw Error('正文块格式错误');
    const byId=new Map(rows.map(a=>[a.id,a]));
    if(snapshot.articles.some(a=>a._chunk===path&&!byId.has(a.id)))throw Error('日报版本已变化，请刷新');
    for(const a of snapshot.articles){if(a._chunk===path&&byId.has(a.id))Object.assign(a,byId.get(a.id),{_loaded:true});}
  }));
}
async function latestEdition(){try{return await get('api/reader.json');}catch{return get('api/news.json');}}
async function render(){
  const version=++renderVersion;
  const signature=JSON.stringify([edition.date,edition.revision,category,savedOnly,focusOnly,directory,$('#search').value]);
  if(signature!==pageSignature){currentPage=1;pageSignature=signature;}
  $('#categories').innerHTML=categories.map(c=>`<button class="${c===category?'active':''}" aria-pressed="${c===category}" data-category="${c}">${c}</button>`).join('');
  $('#news-view').hidden=directory;$('#sources-view').hidden=!directory;
  $('#sources-button').textContent=directory?'返回日报 ↗':'信息源目录 ↗';
  $('#page-title').textContent=directory?'从一手来源，观察世界。':savedOnly?'留给下一次深入阅读。':category==='全部'?'今日，世界正在发生。':category+'，每日一读。';
  const q=$('#search').value.trim().toLowerCase();
  $('#saved-button').setAttribute('aria-pressed',savedOnly);
  if(directory){
    const filtered=sources.filter(s=>(category==='全部'||(mapping[s.category]||s.category)===category)&&`${s.name} ${s.usage_notes} ${s.coverage_regions.join(' ')}`.toLowerCase().includes(q));
    $('#result-count').textContent=`${filtered.length} 个来源 / 目录共 ${sources.length} 个`;
    $('#source-health-summary').innerHTML=healthSummary();
    $('#source-list').innerHTML=filtered.map(s=>`<article class="source"><small>${esc(mapping[s.category]||s.category||'核验与发现')} / ${esc(s.languages.join(' · '))}</small><h3><a href="${safe(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.name)} ↗</a></h3><p>${esc(s.usage_notes)}</p><p>${esc(s.coverage_regions.join(' / '))}</p>${sourceState(s.id)}</article>`).join('')||'<p>没有匹配的信息源。</p>';
    return;
  }
  rememberSaved();
  const all=edition.events?edition.events.map(e=>({...edition.articles.find(a=>a.id===e.lead_id),_event:e})):edition.articles;
  const pool=savedOnly?Object.values(savedArticles).filter(a=>saved.has(a.id)):all;
  const featured=new Set((edition.briefing||[]).map(b=>b.article_id));
  const filtered=pool.filter(a=>(category==='全部'||a.category===category)&&(!focusOnly||savedOnly||featured.has(a.id))&&matches(a,q));
  const errors=health.filter(s=>!s.ok).length;
  $('#result-count').textContent=`${filtered.length} ${savedOnly?'条收藏':'条事件'} · ${edition.articles.length} 篇来源报道${errors?' · '+errors+' 个订阅暂不可用':''}`;
  const showHero=!q&&!savedOnly;
  $('#hero').hidden=!showHero;
  $('#hero').innerHTML=showHero?editionArt():'';
  $('#morning').innerHTML=showHero?morning():'';
  $('#focus-button').setAttribute('aria-pressed',focusOnly);
  const expected=new Date(Date.now()+3600000).toISOString().slice(0,10);
  const ageNote=edition.date&&edition.date<expected?`正在阅读 ${edition.date} 往期日报 · `:'';
  $('#window-note').textContent=ageNote+(edition.window?`收录 ${date(edition.window.start)} — ${date(edition.window.end)}（北京时间） · 约 ${edition.reading_minutes||1} 分钟`:'历史版本 · 尚未采用固定截稿窗口');
  const pages=Math.max(1,Math.ceil(filtered.length/PAGE_SIZE));
  currentPage=Math.max(1,Math.min(currentPage,pages));
  $('#result-count').textContent+=` · 第 ${currentPage} / ${pages} 页`;
  const start=(currentPage-1)*PAGE_SIZE;
  const visible=filtered.slice(start,start+PAGE_SIZE);
  const ids=new Set(visible.flatMap(a=>a._event?.article_ids||[a.id]));
  for(const event of edition.background_events||[])for(const id of event.article_ids)ids.add(id);
  $('#articles').setAttribute('aria-busy','true');
  $('#articles').innerHTML='<p class="page-loading" role="status">正在读取本页报道…</p>';
  try{await loadRows(ids);}catch{if(version===renderVersion){$('#articles').innerHTML='<p role="alert">本页加载失败，请重试；若日报刚更新，请刷新页面。</p><button data-retry>重新加载</button>';$('#articles').setAttribute('aria-busy','false');}return;}
  if(version!==renderVersion)return;
  $('#articles').setAttribute('aria-busy','false');
  $('#articles').innerHTML=visible.map((a,i)=>articleRow({...a,...(!savedOnly?edition.articles.find(r=>r.id===a.id):{})},start+i)).join('');
  let pagination=$('#pagination');
  if(!pagination){pagination=document.createElement('nav');pagination.id='pagination';pagination.setAttribute('aria-label','新闻分页');$('#articles').after(pagination);}
  pagination.innerHTML=`<span>共 ${filtered.length} 条 · 第 ${currentPage} / ${pages} 页</span><div><button data-page="${currentPage-1}" ${currentPage===1?'disabled':''}>← 上一页</button><label>跳至 <input id="page-number" type="number" min="1" max="${pages}" value="${currentPage}" aria-label="页码"></label><button data-jump="${pages}">前往</button><button data-page="${currentPage+1}" ${currentPage===pages?'disabled':''}>下一页 →</button></div>`;
  $('#supplements').innerHTML=!savedOnly&&!focusOnly?supplements(q):'';
  $('#empty').hidden=filtered.length>0;
  $('#empty').textContent=savedOnly?'此分类下暂无收藏。收藏会在此浏览器保留原刊快照，可跨日期阅读。':'本期没有符合条件的事件。可查看下方背景阅读，或切换分类和关键词。';

}
async function get(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error('读取失败');return r.json();}
function showDialog(html){$('#dialog-content').innerHTML=html;$('#dialog').showModal();}
function updateEditionLabel(){ $('#edition').textContent=edition.date?`${edition.date.replaceAll('-',' / ')} · 刊期${edition.revision>1?' · 修订 '+edition.revision:''}`:'每日版 / DAILY EDITION'; }
$('#categories').addEventListener('click',e=>{const b=e.target.closest('[data-category]');if(b){category=b.dataset.category;render();}});
$('#search').addEventListener('input',render);
document.addEventListener('click',e=>{const b=e.target.closest('[data-tag]');if(b){$('#search').value=b.dataset.tag;render();}});
$('#saved-button').onclick=async()=>{savedOnly=!savedOnly;directory=false;category='全部';focusOnly=false;render();if(savedOnly){await hydrateSaved();render();}};
$('#sources-button').onclick=()=>{directory=!directory;savedOnly=false;render();};
document.addEventListener('click',e=>{const b=e.target.closest('[data-save]');if(!b)return;const id=b.dataset.save;if(saved.has(id)){saved.delete(id);delete savedArticles[id];}else{saved.add(id);const row=edition.articles.find(a=>a.id===id)||(edition.social_posts||[]).find(a=>a.id===id);if(row)savedArticles[id]={...row,_editionDate:edition.date};}try{localStorage.setItem('larrytoday-saved',JSON.stringify([...saved]));persistSaved();notify('收藏已更新 · 原刊快照保存在此浏览器');}catch{notify('浏览器未允许保存，收藏仅本次有效');}render();});

$('#close-dialog').onclick=()=>$('#dialog').close();
$('#help-button').onclick=()=>showDialog('<h2>每日早晨，与世界同步。</h2><p>在服务器或项目目录运行，即可采集已配置 RSS，原子发布新一期日报。网页只提供阅读功能。</p><code>python scripts/update_news.py</code><p>每期按北京时间07:00截稿，初版永久保留。同日再次发布须加 --revision-note &quot;修订说明&quot;。人工编辑：参考 data/manual.example.json，修改内容后导入。</p><code>python scripts/update_news.py --import-file data/manual.json</code><p>自动更新：项目 deploy/ 目录提供 Linux systemd 每日 07:00（北京时间）定时配置。更新后刷新页面即可查看。配置 AI 后自动生成双语标题、中文导读与标签；AI 依据为 RSS 摘要或标题，不代替事实核验。</p>');
$('#archive-button').onclick=async()=>{try{const days=await get('api/archive.json');showDialog(`<h2>往期日报</h2><p>初版永久保留。选择日期后可查看初版、修订说明与各次版本。</p>${days.map(d=>`<button class="archive-day" data-day="${esc(d)}">${esc(d)} <span>阅读本期 ↗</span></button>`).join('')||'<p>尚无已发布日报。</p>'}`);}catch{notify('暂时无法读取往期日报');}};
$('#dialog-content').addEventListener('click',async e=>{const day=e.target.closest('[data-day]');const rev=e.target.closest('[data-rev]');try{if(day)await revisionDialog(day.dataset.day);if(rev){edition=await get('api/revisions/'+rev.dataset.date+'/'+rev.dataset.rev+'.json');resetEdition();$('#dialog').close();}}catch{notify('该期版本暂时不可用');}});

$('#clock').textContent=new Date().toLocaleDateString('zh-CN',{timeZone:'Asia/Shanghai',year:'numeric',month:'long',day:'numeric',weekday:'long'});
Promise.all([latestEdition(),get('api/sources.json'),get('api/source-health.json').catch(()=>[]),get('api/social-status.json').catch(()=>({})),get('api/social-posts.json').catch(()=>[])]).then(([n,s,h,ss,sp])=>{edition=n;sources=s.sources;health=h;socialStatus=ss;socialPosts=sp;updateEditionLabel();render();}).catch(()=>{$('#result-count').textContent='日报加载失败，请刷新重试。';$('#empty').hidden=false;$('#empty').textContent='暂时无法连接新闻服务。';});

document.addEventListener('click',async e=>{
  const retry=e.target.closest('[data-retry]');if(retry){render();return;}
  const page=e.target.closest('[data-page]'),jump=e.target.closest('[data-jump]');
  if(page||jump){currentPage=page?Number(page.dataset.page):Math.max(1,Math.min(Number(jump.dataset.jump),Math.trunc(Number($('#page-number').value))||1));await render();$('#articles').scrollIntoView({block:'start'});return;}
  const morningLink=e.target.closest('#morning a[href^="#"]');
  if(morningLink){e.preventDefault();const id=morningLink.getAttribute('href').slice(1);const events=(edition.events||[]).filter(a=>category==='全部'||a.category===category);const at=events.findIndex(a=>a.id===id);if(at<0)return;focusOnly=false;currentPage=Math.floor(at/PAGE_SIZE)+1;pageSignature=JSON.stringify([edition.date,edition.revision,category,savedOnly,focusOnly,directory,$('#search').value]);await render();document.getElementById(id)?.scrollIntoView({block:'center'});}
});
