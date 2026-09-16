export const nums={2022:['273.428','48.732','12.304'],2030:['318.892','60.915','15.090'],2040:['378.416','75.986','18.980'],2050:['442.650','94.126','22.130']};

// ponytail: SVG inline em vez de biblioteca de icones - traco fino, 24x24, herda currentColor.
const ICONS={
elder:'<circle cx="9.5" cy="4" r="2.3"/><path d="M9.5 6.5v7.3"/><path d="M9.5 8.6 6.4 11.8"/><path d="M9.5 8.6 15 9.4"/><path d="M9.5 13.8 7.2 21"/><path d="M9.5 13.8 11.7 21"/><path d="M16.4 9.4v11.4"/><path d="M14.8 9.4h3.2"/>',
users:'<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><path d="M16 6a3 3 0 0 1 0 6"/><path d="M18 14a6 6 0 0 1 3 5"/>',
heartPulse:'<path d="M20 9a4.5 4.5 0 0 0-8-2.8A4.5 4.5 0 0 0 4 9c0 4.2 5.3 7.9 8 9.7 1.5-1 4-2.6 6-4.8"/><path d="M2.5 12.5h3l1.5-3 2 5 1.5-2h3"/>',
home:'<path d="M3.5 10.5 12 4l8.5 6.5"/><path d="M5.5 12v8h13v-8"/><path d="M10 20v-5h4v5"/>',
clock:'<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5.3l3.4 2"/>',
gauge:'<path d="M4 17a8.5 8.5 0 1 1 16 0"/><path d="M12 14.5 16 10"/><circle cx="12" cy="16" r="1.4"/>',
trendUp:'<path d="M3.5 16.5 9 11l3.5 3.5L20.5 6.5"/><path d="M15.5 6.5h5v5"/><path d="M3.5 20.5h17"/>',
chart:'<path d="M4 20.5V4"/><path d="M4 20.5h16.5"/><rect x="7.5" y="12" width="3" height="6" rx="1"/><rect x="13" y="8" width="3" height="10" rx="1"/><rect x="18" y="4.5" width="3" height="13.5" rx="1"/>',
target:'<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
building:'<path d="M4 20.5V5.5l8-3 8 3v15"/><path d="M2.5 20.5h19"/><path d="M8.5 9h2M13.5 9h2M8.5 13h2M13.5 13h2"/><path d="M10 20.5v-4h4v4"/>',
map:'<path d="M9 4 3.5 6.2v13.3L9 17.3l6 2.2 5.5-2.2V4L15 6.2z"/><path d="M9 4v13.3"/><path d="M15 6.2v13.3"/>',
wheelchair:'<circle cx="16" cy="4" r="1.7"/><path d="m18 19 1-7-6 1"/><path d="m5 8 3-3 5.5 3-2.36 3.5"/><path d="M4.24 14.5a5 5 0 0 0 6.88 6"/><path d="M13.76 17.5a5 5 0 0 0-6.88-6"/>',
shield:'<path d="M12 3.2 5 6v5.5c0 4.2 3 7.5 7 9.3 4-1.8 7-5.1 7-9.3V6z"/><path d="M9.2 12.2l2 2 3.6-4"/>',
alert:'<path d="M12 3.8 2.8 19.8h18.4z"/><path d="M12 9.5v4.5"/><path d="M12 17.2h.01"/>',
check:'<circle cx="12" cy="12" r="8.5"/><path d="M8.3 12.3l2.6 2.6 4.8-5.4"/>',
book:'<path d="M4 4.5h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v13h-6a3 3 0 0 0-2 1 3 3 0 0 0-2-1H4z"/><path d="M12 5.5v13"/>',
};
export function svg(name){const p=ICONS[name];return p?`<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${p}</svg>`:name}
export function icon(symbol,color='teal'){return `<span class="round-icon ${color}">${svg(symbol)}</span>`}
export function kpis(year,mode='overview'){const n=nums[year];const rows=mode==='reason'?[['users','Brasil 60+','32,1 milhões','15,8% da população'],['elder','Campinas 60+',n[0],'24,0% da população'],['trendUp','Horizonte 2050','442.650','Estimativa de 60+ em Campinas'],['clock','Planejar agora','+62%','Aumento estimado até 2050']]:[['users','População 60+',n[0],'24,0% do total'],['elder','População 80+',n[1],'Estimativa para planejamento'],['home','Demanda SAD',n[2],`Cenário ${year}`],['gauge','Pressão territorial','Alta','Índice composto demonstrativo']];return `<div class="kpi-grid">${rows.map((r,i)=>`<article class="kpi"><span class="round-icon ${['teal','blue','green','orange'][i]}">${svg(r[0])}</span><div><b>${r[1]}</b><strong>${r[2]}</strong><small>${r[3]}</small></div></article>`).join('')}</div>`}
export const YEARS=[2022,2030,2040,2050];
export const fmt=n=>Number(n||0).toLocaleString('pt-BR');
export const val=s=>+String(s).replace(/\./g,'');
const X=[45,145,245,345];
// ponytail: o grafico era geometria fixa no SVG - o parametro `values` so mexia nos rotulos,
// entao a curva de 80+ era um clone da de 60+ e nada reagia ao ano. Agora sai de `nums`.
export function chart(title,color,serie=0,year=2050){
  const serie_=YEARS.map(y=>val(nums[y][serie]));
  const lo=serie_[0], span=(serie_[serie_.length-1]-lo)||1;       // dominio fixo 2022->2050
  const pts=serie_.map((v,i)=>[X[i],137-(v-lo)/span*87]);          // mesma faixa visual de antes
  const n=Math.max(1,YEARS.indexOf(Number(year))+1);
  const vis=pts.slice(0,n);
  const d=p=>p.map(([x,y],i)=>`${i?'L':'M'}${x} ${y.toFixed(1)}`).join(' ');
  const line=d(vis);
  // ponytail: sem o tracejado, 2022 virava um ponto solto num grid vazio e parecia grafico
  // quebrado. Solido = ja alcancado, tracejado = projecao a frente.
  const futuro=`<path d="${d(pts)}" fill="none" stroke="${color}" stroke-width="2" stroke-dasharray="5 5" opacity=".32"/>`+pts.slice(n).map(([x,y])=>`<circle class="ghost" cx="${x}" cy="${y.toFixed(1)}" r="4" fill="#fff" stroke="${color}" stroke-width="2" opacity=".4"/>`).join('');
  return `<div class="chart"><h3>${title}</h3><svg viewBox="0 0 360 220" role="img" aria-label="${title||'Evolução'} até ${YEARS[n-1]}"><g class="grid-lines"><path d="M45 25H345M45 68H345M45 111H345M45 154H345M45 197H345"/><path d="M45 25V197M145 25V197M245 25V197M345 25V197"/></g>${futuro}<path d="${line} L${vis[vis.length-1][0]} 197 L45 197Z" fill="${color}" opacity=".13"/><path d="${line}" fill="none" stroke="${color}" stroke-width="4"/><g fill="white" stroke="${color}" stroke-width="4">${vis.map(([x,y])=>`<circle cx="${x}" cy="${y.toFixed(1)}" r="6"/>`).join('')}</g>${vis.map(([x,y],i)=>`<text x="${x}" y="${(y-15).toFixed(1)}" text-anchor="${i===3?'end':'middle'}" class="value" fill="${color}">${nums[YEARS[i]][serie]}</text>`).join('')}<g class="axis">${YEARS.map((y,i)=>`<text x="${X[i]}" y="217" text-anchor="middle" class="${i<n?'':'dim'}">${y}</text>`).join('')}</g></svg></div>`
}
export function insight(icon,title,text,color='teal'){return `<div class="insight">${icon?`<span class="mini-icon ${color}">${svg(icon)}</span>`:''}<div><b>${title}</b><p>${text}</p></div></div>`}
